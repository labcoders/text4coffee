#!/bin/python
import RPi.GPIO as gp

from app import redis, app

PIN = 16

def set_state(state):
    gp.setwarnings(False)
    gp.setmode(gp.BOARD)
    gp.setup(PIN, gp.OUT)

    gp.output(PIN, state)
    print "setting to state:", state
    redis.set(app.config.get('PIN_STATE'), state)

def get_state():
    gp.setwarnings(False)
    gp.setmode(gp.BOARD)
    gp.setup(PIN, gp.OUT)

    if redis.get(app.config.get('PIN_STATE')) is None:
        set_state(False)

    v = redis.get(app.config.get('PIN_STATE'))

    if v is None:
        raise RuntimeError('pinstate failed to set')

    return v != "False"

def toggle(state=None):
    gp.setwarnings(False)
    gp.setmode(gp.BOARD)
    gp.setup(PIN, gp.OUT)

    if state is None:
        print "State is none"
        set_state(not get_state())
    elif type(state) != bool:
        raise ValueError('Invalid state for pin. Use True or False.')
    else:
        set_state(state)

    return get_state()
