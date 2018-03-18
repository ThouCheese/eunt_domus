from os import system
from time import sleep
from datetime import datetime, timedelta
from astral import Astral  # dependency
from phue import Bridge  # dependency

# dict that contains a bunch of city objects
astral = Astral()
# city object that can calculate sunrise and down, Amsterdam is close enough
city = astral['Amsterdam']
# make sure the ip of the hue bridge is always the same
ip = '192.168.1.4'
# weird ass codes
scenes = {'bright': 'LUA5ONeFAb0I3sF', 'dim': 'ijw3l2w2wXn2p8n'}
# wait time in seconds
wait_time = 15 * 60


def activate_lights():
    # create new sun object every call with new datetime
    sun = city.sun(date=datetime.now(), local=True)
    # lights go dim after 23 'c clock
    if datetime.now().hour > 23 or datetime.now().hour < 6:
        Bridge(ip=ip).activate_scene(1, scenes['dim'])
    # lights go bright one hour before dusk
    elif datetime.now() > sun['dusk'].replace(tzinfo=None) - timedelta(hours=2):
        Bridge(ip=ip).activate_scene(1, scenes['bright'])


# true if phone present
def phone_present(): return system("ping -c 1 192.168.1.2") == 0


def remains_gone():
    checks = 3  # check three times, evenly spaced within wait_time
    for _ in range(wait_time // checks, wait_time, wait_time // checks):
        if phone_present():
            return False
        sleep(wait_time // checks)
    return True


was_present = True
while True:
    sleep(1)
    # do nothing if the lights are already on
    if not Bridge(ip=ip).get_light(3, 'on'):
        if phone_present():
            # if the phone was already present, do not turn the lights on
            if was_present:
                sleep(wait_time)  # that way I still able to turn them off
            else:
                was_present = True  # mark the phone as present
                activate_lights()  # turn on the appropriate light scheme
        # timeout after wait_time, if the phone remains gone,
        elif remains_gone():
            was_present = False  # start listening for the phone again
