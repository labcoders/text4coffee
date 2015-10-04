from flask import request
from . import app, toggle, util, acl

@app.route("/sms", methods=["POST"])
def twizzle():
    msg = request.form['Body']
    number = request.form['From']

    msg = msg.lower().strip()
    words = msg.split()
    print "Got message:", msg
    current_state = toggle.get_state()

    if msg == "on":
        state = toggle.toggle(True)
    elif msg == "off":
        state = toggle.toggle(False)
    elif msg == "q":
        state = toggle.get_state()
    elif words[0] == "register":
        admin_password = app.config.get("ADMIN_PASSWORD", None)
        if len(words) < 3:
            return util.twizslify("usage: register <password> <name>")

        if admin_password is not None and words[1] == admin_password:
            account = acl.Account(
                    number=number,
                    name=" ".join(words[2:]),
                    privileges=acl.ALL_PRIVILEGES,
            )
            account.save()
            return util.twizzlify("Registered administrator account.")

        token = acl.get_token(words[1])

        if token is not None and token['password'] == words[1]:
            account = acl.Account(
                    number=number,
                    name=" ".join(words[2:]),
                    privileges=token['privileges'],
            )
            account.save()
            acl.remove_token(token['password'])
            return util.twizzlify("Registered.")

        return util.twizzlify("Registration failed.")

    elif msg == "help":
        return util.twizzlify("Commands: on, off, q, register <password>")
    else:
        return util.twizzlify("Unknown command. Try 'help'.")

    changed = current_state != state

    return util.twizzlify(
            "".join([
                "Coffee is ",
                "now " if changed else "currently ", 
                "on" if state else "off"
            ])
    )

