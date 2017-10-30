from os import system
from time import sleep
from datetime import datetime, timedelta
from astral import Astral  # dependency
from phue import Bridge  # dependency

astral = Astral()  # dict that contains a bunch of city objects
city = astral['Amsterdam']  # city object that can calculate sunrise and down, Amsterdam is close enough
bridge = Bridge(ip='192.168.1.4')  # make sure the ip of the hue bridge is always the same
scenes = {'bright': 'LUA5ONeFAb0I3sF', 'dim': 'ijw3l2w2wXn2p8n'}  # weird ass codes
wait_time = 15 * 60  # wait time in seconds


def activate_lights():
    sun = city.sun(date=datetime.now(), local=True)  # create new sun object every call with new datetime
    if datetime.now().hour > 23 or datetime.now().hour < 6:  # lights go dim after 23 'c clock
        bridge.activate_scene(1, scenes['dim'])
    elif datetime.now() > sun['dusk'].replace(tzinfo=None) - timedelta(hours=2):  # lights go bright one hour before dusk
        bridge.activate_scene(1, scenes['bright'])


def phone_present(): return system("ping -c 1 192.168.1.2") == 0  # true if phone present


def remains_gone():
    checks = 3  # check three times, evenly spaced within wait_time
    for _ in range(wait_time // checks, wait_time, wait_time // checks):
        if phone_present():
            return False
        sleep(wait_time // checks)
    return True


was_present = False
while True:
    sleep(1)
    print('running lights script')
    if not bridge.get_light(3, 'on'):  # do nothing if the lights are already on
        if phone_present():
            if was_present:  # if the phone was already present, do not turn the lights on.
                sleep(wait_time)  # that way I still able to turn them off
            else:
                was_present = True  # mark the phone as present
                activate_lights()  # turn on the appropriate light scheme
        elif remains_gone():  # timeout after wait_time, if the phone remains gone,
            was_present = False  # start listening for the phone again
