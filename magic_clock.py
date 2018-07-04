import requests
import json
import RPi.GPIO as GPIO
import time

DEBUG_MODE = False
DELAY = 0.01
CONFIG = open("config.txt", "r")
PWD = CONFIG.readline()
TRACKERS = ["device_tracker.google_maps_115948204649955307306"]
PROXIMITIES = ["proximity.home"]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
coil_A_1_pin = 6
coil_A_2_pin = 13
coil_B_1_pin = 19
coil_B_2_pin = 26


clockwise = [0, 1, 2, 3, 4, 5, 6, 7]
clockwise[0] = [0, 0 ,0, 1]
clockwise[1] = [0, 0, 1, 1]
clockwise[2] = [0, 0, 1, 0]
clockwise[3] = [0, 1, 1, 0]
clockwise[4] = [0, 1, 0, 0]
clockwise[5] = [1, 1, 0, 0]
clockwise[6] = [1, 0, 0, 0]
clockwise[7] = [1, 0, 0, 1]

counter_clockwise = [0, 1, 2, 3, 4, 5, 6, 7]
counter_clockwise[0] = [1, 0, 0, 0]
counter_clockwise[1] = [1, 1, 0, 0]
counter_clockwise[2] = [0, 1, 0, 0]
counter_clockwise[3] = [0, 1, 1, 0]
counter_clockwise[4] = [0, 0, 1, 0]
counter_clockwise[5] = [0, 0, 1, 1]
counter_clockwise[6] = [0, 0, 0, 1]
counter_clockwise[7] = [1, 0, 0, 1]

GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)


class Clock():
    def __init__(self):
        self.hand_1 = 0
        self.hand_2 = 0


def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)


def backwards(steps):
    for i in range(steps):
        for j in range(8):
            setStep(clockwise[j][0], clockwise[j][1], clockwise[j][2], clockwise[j][3])
            time.sleep(DELAY)


def forward(steps):
    for i in range(steps):
        for j in range(8):
            setStep(counter_clockwise[j][0], counter_clockwise[j][1], counter_clockwise[j][2], counter_clockwise[j][3])
            time.sleep(DELAY)


def get_location(tracker):
    """Get  location from Home Assistant"""
    url = "http://192.168.1.11:8123/api/states/{}?api_password={}".format(tracker, PWD)
    try:
        response = requests.get(url, timeout=5)
        return (json.loads(response.text)["state"])
    except (requests.exceptions.RequestException, ValueError):
        print("error getting location for {}".format(tracker))
        return


def get_travelling(proximity):
    """Get travelling status from Home Assistant"""
    url = "http://192.168.1.11:8123/api/states/{}?api_password={}".format(proximity, PWD)
    try:
        response = requests.get(url, timeout=5)
        return (json.loads(response.text)["attributes"]["dir_of_travel"])
    except (requests.exceptions.RequestException, ValueError):
        print("error getting travelling status for {}".format(proximity))
        return


def get_status(tracker, proximity):
    if get_location(tracker) == "home":
        # return "Home"
        return 0
    elif get_location(tracker) == "school":
        # return "School"
        return 1
    elif get_location(tracker) == "work":
        # return "Work"
        return 2
    elif get_location(tracker) == "not_home" and get_travelling(proximity) \
            == "towards" or get_travelling(proximity) == "away_from":
        # return "Travelling"
        return 3
    elif get_location(tracker) == "hospital":
        # return "Hospital"
        return 5
    elif get_location(tracker) == "prison":
        # return "Prison"
        return 6
    elif get_location(tracker) == "mortal peril":
        # return "Moral Peril"
        return 7
    else:
        # return "Somewhere Else"
        return 4


def update_clock_hand(clock, new_position):
    clock = clock
    steps = 0

    if new_position == clock.hand_1:
        pass
    else:
        steps = new_position - clock.hand_1
        clock.hand_1 = clock.hand_1 + steps
    return steps


def __main__():
    clock = Clock()
    try:
        while True:
            for i in len(TRACKERS):
                new_position = get_status(TRACKERS[i], PROXIMITIES[i])
                num_steps = update_clock_hand(clock, new_position)
                if num_steps > 0:
                    forward(num_steps * 64)
                elif num_steps < 0:
                    backwards(abs(num_steps * 64))

                time.sleep(1)
    except KeyboardInterrupt:
        setStep(0, 0, 0, 0)
        exit()

if __name__ == "__main__":
    __main__()
