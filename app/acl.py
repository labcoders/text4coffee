import json, random

from app import redis

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
    password = [random.choice(PASSWORD_CHARS) for _ in xrange(length)]
    redis.set(
            _PASSWORD_PREFIX + password,
            dict(
                password=password,
                privileges=list(privileges),
            ),
    )
    return password

def make_key(number):
    return _KEY_PREFIX + number

class Account(object):
    @classmethod
    def load(cls, number):
        s = redis.get(make_key(number))
        if s is None:
            return None
        return cls(

        )

    def __init__(self, number, name, privileges):
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

    def has_privilege(self, privilege):
        return privilege in self.privileges

    def grant_privilege(self, privilege):
        self.privileges.add(privilege)

    def save(self):
        redis.set(make_key(self.number), self.serialize())

    def serialize(self):
        return json.dumps(
                dict(
                    number=self.number,
                    privileges=list(self.privileges),
                    name=self.name,
                )
        )
