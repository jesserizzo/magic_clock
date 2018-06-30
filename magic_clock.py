import requests
import json
# import RPi.GPIO as GPIO
import time


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
    if get_jesse_location() == "home" and get_jesse_travelling() == \
            "arrived" or get_jesse_travelling() == "stationary":
        # return "Home"
        return 0
    elif get_jesse_location() == "school" and get_jesse_travelling() == \
            "arrived" or get_jesse_travelling() == "stationary":
        # return "School"
        return 1
    elif get_jesse_location() == "work" and get_jesse_travelling() == \
            "arrived" or get_jesse_travelling() == "stationary":
        # return "Work"
        return 2
    elif get_jesse_travelling() == "towards" or get_jesse_travelling() \
            == "away_from":
        # return "Travelling"
        return 3
    # if get_jesse_location() == "not_home":
    #    return "Lost"
    #    return 4
    elif get_jesse_location() == "hospital" and get_jesse_travelling() \
            == "arrived" or get_jesse_travelling() == "stationary":
        # return "Hospital"
        return 5
    elif get_jesse_location() == "prison" and get_jesse_travelling() \
            == "arrived" or get_jesse_travelling() == "stationary":
        # return "Prison"
        return 6
    elif get_jesse_location() == "mortal peril":
        # return "Moral Peril"
        return 7


def move_clock_hand(clock_position, new_clock_position):


def __main__():
    clock_position = 0
    while True:
        jesse = get_jesse_status()


        time.sleep(1)
        print(jesse)

if __name__ == "__main__":
    __main__()


"""
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
coil_A_1_pin = 4 # pink
coil_A_2_pin = 17 # orange
coil_B_1_pin = 23 # blue
coil_B_2_pin = 24 # yellow

# adjust if different
StepCount = 8
Seq = range(0, StepCount)
Seq[0] = [0,1,0,0]
Seq[1] = [0,1,0,1]
Seq[2] = [0,0,0,1]
Seq[3] = [1,0,0,1]
Seq[4] = [1,0,0,0]
Seq[5] = [1,0,1,0]
Seq[6] = [0,0,1,0]
Seq[7] = [0,1,1,0]

GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

GPIO.output(enable_pin, 1)

def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)

def forward(delay, steps):
    for i in range(steps):
        for j in range(StepCount):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

def backwards(delay, steps):
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

if __name__ == '__main__':
    while True:
        delay = raw_input("Time Delay (ms)?")
        steps = raw_input("How many steps forward? ")
        forward(int(delay) / 1000.0, int(steps))
        steps = raw_input("How many steps backwards? ")
        backwards(int(delay) / 1000.0, int(steps))
"""
