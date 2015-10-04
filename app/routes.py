from flask import request

from . import app, toggle, util

@app.route("/sms", methods=["POST"])
def twizzle():
    msg = request.form['Body']
    msg = msg.lower()
    print "Got message:", msg
    current_state = toggle.get_state()

    if msg == "on":
        state = toggle.toggle(True)
    elif msg == "off":
        state = toggle.toggle(False)
    elif msg == "q":
        state = toggle.get_state()
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

