import secret_config as config

from redis import Redis

from time import time

import app.toggle as toggle

redis = Redis()

def time_ok():
    last_brew_time = redis.get(config.LAST_BREW_TIME)
    if last_brew_time is None:
        return False
    now = time()
    d = now - float(last_brew_time)
    v = d > config.BREW_WAIT_LENGTH
    if not v:
        print "[ANALYZER] time is not ok; delta = %.2f" % d
    return v

def state_ok():
    v = redis.get(config.PIN_STATE) != 'False'
    if not v:
        print "[ANALYZER] state is not ok"
    return v

def brew_ok(last_average):
    v = last_average < config.BREW_CONTOUR_THRESHOLD
    if not v:
        print (
                "[ANALYZER] brew is not ok; %.2f/%.2f" % (
                    last_average,
                    config.BREW_CONTOUR_THRESHOLD,
                )
        )
    return v

def annie_ok():
    _, last_average = redis.brpop(config.AVERAGE_LIST)
    last_average = float(last_average)
    return time_ok() and state_ok() and brew_ok(last_average)

def turn_off():
    return toggle.toggle(False)

if __name__ == '__main__':
    while True:
        if annie_ok():
            print "[ANALYZER] You've been struck by a smooth dark roast."
            turn_off()
        else:
            print "[ANALYZER] Staying on"
