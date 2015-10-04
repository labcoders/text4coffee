import twilio.twiml
from .fortune import fortune

def twizzlify(msg):
    resp = twilio.twiml.Response()
    resp.sms(msg + '\n' + fortune())
    return str(resp)
