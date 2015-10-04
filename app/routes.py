import json
from flask import request
from . import app, toggle, util, acl, redis
from time import sleep
from time import time
import cv2

@app.route("/sms", methods=["POST"])
def twizzle():
    redis.set(app.config['LAST_BREW_TIME'], time())
    msg = request.form['Body']
    number = request.form['From']

    msg = msg.strip()
    words = msg.split()
    command = words[0].lower()

    print "Got message:", msg
    current_state = toggle.get_state()

    account = acl.Account.load_by_number(number=number)

    check_yo_privilege = util.twizzlify("Check yo' privilege")
    not_registered = util.twizzlify("You are not registered.")

    if command == "on":
        if not account:
            return not_registered

        if not account.check_privilege(acl.PRIVILEGE_CONTROL):
            return check_yo_privilege

        state = toggle.toggle(True)
    elif command == "off":
        if not account:
            return not_registered

        if not account.check_privilege(acl.PRIVILEGE_CONTROL):
            return check_yo_privilege

        state = toggle.toggle(False)
    elif command == "q" or command == "query":
        if not account:
            return not_registered

        if not account.check_privilege(acl.PRIVILEGE_QUERY):
            return check_yo_privilege

        state = toggle.get_state()
    elif command == "revoke":
        if account is None:
            return not_registered

        if not account.check_privilege(acl.PRIVILEGE_ADMIN):
            return check_yo_privilege

        if len(words) < 2:
            return twizzlify(
                    "usage: revoke <token>"
            )

        password = words[1]

        acl.remove_token(password)

        return util.twizzlify(
                "Revoked.",
        )
    elif command == "register":
        if account is not None:
            return util.twizzlify(
                    "This number is already registered to %s." % (
                        account.name,
                    ),
            )

        if len(words) < 3:
            return util.twizzlify("usage: register <password> <name>")

        admin_password = app.config.get("ADMIN_PASSWORD", None)

        if admin_password is not None and words[1] == admin_password:
            account = acl.Account(
                    id=None,
                    number=number,
                    name=" ".join(words[2:]),
                    privileges=acl.ALL_PRIVILEGES,
            )
            account.save()
            return util.twizzlify("Registered administrator account.")

        token = acl.get_token(words[1])

        if token is not None:
            print token
            token = json.loads(token)
            if token['password'] == words[1]:
                account = acl.Account(
                        id=None,
                        number=number,
                        name=" ".join(words[2:]),
                        privileges=token['privileges'],
                )
                account.save()
                acl.remove_token(token['password'])
                return util.twizzlify("Registered.")

        return util.twizzlify("Invalid password.")
    elif command == "unregister":
        if account is None:
            return not_registered

        if len(words) < 2:
            account.delete()

            return util.twizzlify(
                    "Unregistered.",
            )

        if not account.check_privilege(acl.PRIVILEGE_ADMIN):
            return check_yo_privilege

        other_number = words[1]
        other_account = acl.Account.load_by_number(other_number)

        if other_account is None:
            return util.twizzlify(
                    "No account with number %s." % (
                        other_number,
                    ),
            )

        other_account.delete()

        return util.twizzlify(
                "Unregistered.",
        )
    elif command == "list":
        if account is None:
            return not_registered

        if not account.check_privilege(acl.PRIVILEGE_ADMIN):
            return check_yo_privilege

        accounts = acl.Account.load_all()

        return util.twizzlify(
                '\n'.join(
                    ["Accounts:"]
                    +
                    [
                        "%s: %s [%s]" % (
                            a.name,
                            a.number,
                            ', '.join(p[0] for p in a.privileges),
                        )
                        for a
                        in accounts
                    ]
                ),
        )
    elif command == "token":
        if account is None:
            return not_registered

        if not account.check_privilege(acl.PRIVILEGE_ADMIN):
            return check_yo_privilege

        privileges = words[1:]

        if privileges and any(p not in acl.ALL_PRIVILEGES for p in privileges):
            return util.twizzlify(
                    "One or more privileges are invalid.\n"
                    "Valid privileges are: " + ", ".join(acl.ALL_PRIVILEGES)
            )

        if privileges:
            token = acl.make_token(privileges)
        else:
            token = acl.make_token()

        return util.twizzlify("Created token: " + token)
    elif command == "doc":
        return util.twizzlify(
                '\n'.join([
                    'Commands:',
                    'on: turn coffee maker on',
                    'off: turn coffee maker off',
                    'q|query: query coffee status',
                    'register <password> <name...>: register an account',
                    'token <privilege...>: create a registration token',
                    'unregister [number]: delete an account',
                    'revoke <token>: revoke a token',
                    'list: list accounts',
                    'doc: show this help',
                ]),
        )
    else:
        return util.twizzlify("Unknown command. Try 'doc'.")

    changed = current_state != state

    return util.twizzlify(
            "".join([
                "Coffee is ",
                "now " if changed else "currently ",
                "on" if state else "off"
            ])
    )
