import json, random

from app import redis
from . import database

_KEY_PREFIX = 'acl-'
_PASSWORD_PREFIX = 'acl-password-'

PRIVILEGE_CONTROL = "control"
PRIVILEGE_ADMIN = "admin"
PRIVILEGE_QUERY = "query"

DEFAULT_PRIVILEGES = set([
    PRIVILEGE_QUERY
])

ALL_PRIVILEGES = set([
    PRIVILEGE_CONTROL,
    PRIVILEGE_ADMIN,
    PRIVILEGE_QUERY,
])

PASSWORD_CHARS = [c for c in "qwertyuiopasdfghjklzxcvbnm"]

def get_token(password):
    return redis.get(_PASSWORD_PREFIX + password)

def remove_token(password):
    redis.delete(_PASSWORD_PREFIX + password)

def make_token(privileges=DEFAULT_PRIVILEGES, length=8):
    """ Generate and record a password to redis. """
    password = ''.join(
            [random.choice(PASSWORD_CHARS) for _ in xrange(length)]
    )
    redis.set(
            _PASSWORD_PREFIX + password,
            json.dumps(
                dict(
                    password=password,
                    privileges=list(privileges),
                ),
            ),
    )
    return password

def make_key(number):
    return _KEY_PREFIX + number

def _load_privileges(id, conn=None):
    with database.connect(conn) as conn:
        cur = conn.cursor()

        # load the account's privileges
        cur.execute(
                "SELECT p.name "
                "FROM privilege p, link_privilege_account lpa "
                "WHERE p.id = lpa.privilege_id "
                "AND lpa.account_id = %s "
                ";",
                (id,)
        )
        rows = cur.fetchall()
        privileges = rows

        return [p[0] for p in privileges]

class Account(object):
    @classmethod
    def load_all(cls, conn=None):
        with database.connect(conn) as conn:
            cur = conn.cursor()

            cur.execute("SELECT id, name, number FROM account;")
            rows = cur.fetchall()

            accounts = []
            for id, name, number in rows:
                privileges = _load_privileges(id, conn)
                accounts.append(
                        cls(
                            id=id,
                            name=name,
                            number=number,
                            privileges=privileges,
                        ),
                )

            return accounts

    @classmethod
    def _load(cls, strategy, value, conn=None):
        if strategy not in ["id", "number"]:
            raise ValueError("Invalid account loading strategy.")

        with database.connect(conn) as conn:
            cur = conn.cursor()
            cur.execute(
                    " ".join([
                        "SELECT id, name, number FROM account WHERE",
                        strategy,
                        " = %s;",
                    ]),
                    (value,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            id, name, number = row

            a = cls(
                    id=id,
                    number=number,
                    name=name,
                    privileges=_load_privileges(id, conn),
            )
            print a
            return a

    @classmethod
    def load_by_number(cls, number, conn=None):
        return cls._load("number", number, conn=conn)

    @classmethod
    def load_by_id(cls, id, conn=None):
        return cls._load("id", id, conn=conn)

    def __init__(self, id, number, name, privileges):
        self.id = id
        self.number = number
        self.name = name
        self.privileges = privileges

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def privileges(self):
        return self._privileges

    @privileges.setter
    def privileges(self, value):
        self._privileges = set(value)

    def check_privilege(self, privilege):
        return privilege in self.privileges

    def grant_privilege(self, privilege):
        self.privileges.add(privilege)

    def _persist_privileges(self, account_id=None, conn=None):
        if account_id is None:
            account_id = self.id

        with database.connect(conn) as conn:
            cur = conn.cursor()

            cur.execute(
                    "SELECT id, name "
                    "FROM privilege "
                    ";"
            )
            _db_privileges = cur.fetchall()

            db_privileges = dict(
                    (name, id)
                    for id, name
                    in _db_privileges
            )

            # Load the account's current privileges
            cur.execute(
                    "SELECT p.id, p.name "
                    "FROM privilege p, link_privilege_account lpa "
                    "WHERE p.id = lpa.privilege_id "
                    "AND lpa.account_id = %s "
                    ";",
                    (account_id,),
            )
            _my_db_privileges = cur.fetchall()

            my_db_privileges = dict(
                    (name, id)
                    for id, name
                    in _my_db_privileges
            )

            for privilege in self.privileges:
                if privilege not in my_db_privileges:
                    privilege_id = db_privileges.get(privilege, None)
                    if privilege_id is None:
                        raise RuntimeError(
                                "Invalid privilege `%s`." % (
                                    privilege,
                                ),
                        )
                    cur.execute(
                            "INSERT INTO link_privilege_account "
                            "( account_id, privilege_id ) "
                            "VALUES "
                            "( %s, %s ) "
                            ";",
                            (account_id, privilege_id),
                    )

    def _persist_new(self, conn=None):
        with database.connect(conn) as conn:
            cur = conn.cursor()
            cur.execute(
                    "INSERT INTO account ( name, number ) "
                    "VALUES ( %s, %s ) "
                    "RETURNING id "
                    ";",
                    (self.name, self.number),
            )
            (account_id,) = cur.fetchone()

            self._persist_privileges(account_id, conn)

        self.id = account_id

    def _persist_update(self, conn=None):
        with database.connect(conn) as conn:
            cur = conn.cursor()
            cur.execute(
                    "UPDATE account "
                    "SET ( name, number ) "
                    "= ( %s, %s ) "
                    "WHERE id = %s "
                    ";",
                    (self.name, self.number, self.id),
            )

    def delete(self, conn=None):
        with database.connect(conn) as conn:
            if self.id is None:
                raise ValueError("This account is not persisted.")

            cur = conn.cursor()
            cur.execute(
                    "DELETE FROM link_privilege_account "
                    "WHERE account_id = %s "
                    ";",
                    (self.id,),
            )
            cur.execute(
                    "DELETE FROM account "
                    "WHERE id = %s "
                    ";",
                    (self.id,),
            )
            conn.commit()

    def save(self, conn=None):
        with database.connect(conn) as conn:
            if self.id is None:
                self._persist_new(conn)
            else:
                self._persist_update(conn)
            conn.commit()

    def serialize(self):
        return json.dumps(
                dict(
                    number=self.number,
                    privileges=list(self.privileges),
                    name=self.name,
                )
        )

    def __repr__(self):
        return "Account(%d, %s, %s, %s)" % (
                self.id,
                self.number,
                self.name,
                repr(self.privileges),
        )
