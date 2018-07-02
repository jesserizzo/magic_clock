import requests
import json
import RPi.GPIO as GPIO
import time

DEBUG_MODE = False
DELAY = 0.01

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
coil_A_1_pin = 6 #  pink
coil_A_2_pin = 13 #  orange
coil_B_1_pin = 19 #  blue
coil_B_2_pin = 26 #  yellow

# adjust if different
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

# GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

# GPIO.output(enable_pin, 1)


class Clock():
    def __init__(self):
        self.jesse_hand = 0
        self.megan_hand = 0


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


def get_jesse_location():
    """Get Jesse's location from Home Assistant"""
    url = "http://192.168.1.11:8123/api/states/device_tracker.google_maps"\
          "_115948204649955307306?api_password=ty2PNJAAHLk4bqU9145h"
    try:
        response = requests.get(url, timeout=5)
        return (json.loads(response.text)["state"])
    except (requests.exceptions.RequestException, ValueError):
        print("error getting jesse location")
        return


def get_jesse_travelling():
    """Get Jesse's travelling status from Home Assistant"""
    url = "http://192.168.1.11:8123/api/states/proximity.home"\
          "?api_password=ty2PNJAAHLk4bqU9145h"
    try:
        response = requests.get(url, timeout=5)
        return (json.loads(response.text)["attributes"]["dir_of_travel"])
    except (requests.exceptions.RequestException, ValueError):
        print("error getting jesse travelling")
        return


def get_jesse_status():
    if DEBUG_MODE is True:
        return (int(input()))
    if get_jesse_location() == "home":
        # return "Home"
        return 0
    elif get_jesse_location() == "school":
        # return "School"
        return 1
    elif get_jesse_location() == "work":
        # return "Work"
        return 2
    elif get_jesse_location() = "away" and get_jesse_travelling() == \
            "towards" or get_jesse_travelling() == "away_from":
        # return "Travelling"
        return 3
    elif get_jesse_location() == "away" and get_jesse_travelling() \
            == "stationary":
        # return "Somewhere Else"
        return 4
    elif get_jesse_location() == "hospital":
        # return "Hospital"
        return 5
    elif get_jesse_location() == "prison":
        # return "Prison"
        return 6
    elif get_jesse_location() == "mortal peril":
        # return "Moral Peril"
        return 7


def update_clock_hand(clock):
    clock = clock
    new_position = get_jesse_status()
    steps = 0

    if new_position == clock.jesse_hand:
        pass
    else:
        steps = new_position - clock.jesse_hand
        clock.jesse_hand = clock.jesse_hand + steps
    return steps


def __main__():
    clock = Clock()
    try:
        while True:
            print("current position {}".format(clock.jesse_hand))
            num_steps = update_clock_hand(clock)
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
