import time

LAST_STMP = -1

SEQUENCE_BIT = 12

MAX_SEQUENCE_NUM = -1 ^ (-1 << SEQUENCE_BIT)
SEQUENCE = 0

MACHINE_BIT = 7
TIMESTMP_LEFT = SEQUENCE_BIT + MACHINE_BIT
MACHINE_LEFT = SEQUENCE_BIT
machineId = 1

START_STMP = 1546272000000

def get_next_time():
    t = int(time.time() * 1000)
    if t< START_STMP:
        t = int(time.time() * 1000)
    return t

def get_guid():
    global SEQUENCE
    global LAST_STMP
    curr = int(time.time() * 1000)
    if curr < LAST_STMP: raise Exception
    if curr == LAST_STMP:
        SEQUENCE = (SEQUENCE + 1) & MAX_SEQUENCE_NUM
        if SEQUENCE == 0:
            curr = get_next_time()
    else:
        SEQUENCE = 0

    LAST_STMP = curr
    return (curr - START_STMP) << TIMESTMP_LEFT | machineId << MACHINE_LEFT | SEQUENCE;


# print(get_guid())
