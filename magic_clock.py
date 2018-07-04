import requests
import json
import RPi.GPIO as GPIO
import time

# Delay between each phase of the stepper motor, the lower this number
# the faster the motor turns
MOTOR_DELAY = 0.01
#Local IP address and port num of your Home Assistant server
URL = "http://192.168.1.11:8123"
# The entity id(s) of your device trackers in Home Assistant
TRACKERS = ["device_tracker.google_maps_115948204649955307306",
            "device_tracker.google_maps_103614229965349669808"]
# The entity id(s) of your proximities in Home Assistant
PROXIMITIES = ["proximity.jesse_home", "proximity.megan_home"]
# A list of ints for the position of the clock hands, set to 0 at program start
CLOCK_HANDS = []
for i in len(TRACKERS):
    CLOCK_HANDS.append(0)
# The pins on the Raspberry pi used to drive the motor controller(s)
MOTOR_1_PHASE_A = 6
MOTOR_1_PHASE_B = 13
MOTOR_1_PHASE_C = 19
MOTOR_1_PHASE_D = 26
MOTOR_2_PHASE_A = 12
MOTOR_2_PHASE_B = 16
MOTOR_2_PHASE_C = 20
MOTOR_2_PHASE_D = 21

# Config file containing the password, simply so it isn't uploaded to
# Github. You could just hardcode it if you aren't using Github
with open("config.txt", "r") as config:
    config_json = json.loads(config.read())
    PWD = config_json["password"]

# Set up the GPIO pins on the Raspberry Pi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(MOTOR_1_PHASE_A, GPIO.OUT)
GPIO.setup(MOTOR_1_PHASE_B, GPIO.OUT)
GPIO.setup(MOTOR_1_PHASE_C, GPIO.OUT)
GPIO.setup(MOTOR_1_PHASE_D, GPIO.OUT)
GPIO.setup(MOTOR_2_PHASE_A, GPIO.OUT)
GPIO.setup(MOTOR_2_PHASE_B, GPIO.OUT)
GPIO.setup(MOTOR_2_PHASE_C, GPIO.OUT)
GPIO.setup(MOTOR_2_PHASE_D, GPIO.OUT)


# Function that actually makes the motor spin.
def setStep(motor_num, w1, w2, w3, w4):
    if motor_num == 0:
        GPIO.output(MOTOR_1_PHASE_A, w1)
        GPIO.output(MOTOR_1_PHASE_B, w2)
        GPIO.output(MOTOR_1_PHASE_C, w3)
        GPIO.output(MOTOR_1_PHASE_D, w4)
    if motor_num == 1:
        GPIO.output(MOTOR_2_PHASE_A, w1)
        GPIO.output(MOTOR_2_PHASE_B, w2)
        GPIO.output(MOTOR_2_PHASE_C, w3)
        GPIO.output(MOTOR_2_PHASE_D, w4)



def backwards(steps, motor_num):
    """Look up documentation for your motor driver board to find what
    pins to energize in what order. This is for the ULN2003"""
    backwards = [0, 1, 2, 3, 4, 5, 6, 7]
    backwards[0] = [0, 0, 0, 1]
    backwards[1] = [0, 0, 1, 1]
    backwards[2] = [0, 0, 1, 0]
    backwards[3] = [0, 1, 1, 0]
    backwards[4] = [0, 1, 0, 0]
    backwards[5] = [1, 1, 0, 0]
    backwards[6] = [1, 0, 0, 0]
    backwards[7] = [1, 0, 0, 1]
    for i in range(steps):
        for j in range(8):
            setStep(motor_num, backwards[j][0], backwards[j][1],
                    backwards[j][2], backwards[j][3])
            time.sleep(MOTOR_DELAY)


def forward(steps, motor_num):
    """Look up documentation for your motor driver board to find what
    pins to energize in what order. This is for the ULN2003"""
    forwards = [0, 1, 2, 3, 4, 5, 6, 7]
    forwards[0] = [1, 0, 0, 0]
    forwards[1] = [1, 1, 0, 0]
    forwards[2] = [0, 1, 0, 0]
    forwards[3] = [0, 1, 1, 0]
    forwards[4] = [0, 0, 1, 0]
    forwards[5] = [0, 0, 1, 1]
    forwards[6] = [0, 0, 0, 1]
    forwards[7] = [1, 0, 0, 1]
    for i in range(steps):
        for j in range(8):
            setStep(motor_num, forwards[j][0], forwards[j][1], forwards[j][2],
                    forwards[j][3])
            time.sleep(MOTOR_DELAY)


def get_location(tracker):
    """Get  location from Home Assistant"""
    url = "{}/api/states/{}?api_password={}".format(URL, tracker, PWD)
    try:
        response = requests.get(url, timeout=5)
        return (json.loads(response.text)["state"])
    except (requests.exceptions.RequestException, ValueError):
        print("error getting location for {0}".format(tracker))
        return


def get_travelling(proximity):
    """Get proximity status from Home Assistant"""
    url = "{}/api/states/{}?api_password={}".format(URL, proximity, PWD)
    try:
        response = requests.get(url, timeout=5)
        return (json.loads(response.text)["attributes"]["dir_of_travel"])
    except (requests.exceptions.RequestException, ValueError):
        print("error getting travelling status for {}".format(proximity))
        return


def get_status(tracker, proximity):
    """Gets the location and proximity states from Home Assistant and
    returns an int corresponding to location on the clock face"""
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


def update_clock_hand(hand_num, new_position):
    """Calculate how many steps to move the hand and store the
    new hand position"""
    steps = 0
    if new_position == CLOCK_HANDS[hand_num]:
        pass
    else:
        steps = new_position - CLOCK_HANDS[hand_num]
        CLOCK_HANDS[hand_num] = CLOCK_HANDS[hand_num] + steps
    return steps

def __main__():
    try:
        while True:
            for i in range(len(TRACKERS)):
                new_position = get_status(TRACKERS[i], PROXIMITIES[i])
                num_steps = update_clock_hand(i, new_position)
                if num_steps > 0:
                    forward(num_steps * 64, i)
                elif num_steps < 0:
                    backwards(abs(num_steps * 64), i)

                time.sleep(1)
    except KeyboardInterrupt:
        setStep(0, 0, 0, 0, 0)
        setStep(1, 0, 0, 0, 0)
        GPIO.cleanup()
        exit()

if __name__ == "__main__":
    __main__()
