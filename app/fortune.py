import subprocess as sp

def fortune(max_length=100):
    return sp.check_output(['/usr/games/fortune', '-n', str(max_length), '-s'])
