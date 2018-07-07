import requests
import json
import RPi.GPIO as GPIO
import time


# Delay between each phase of the stepper motor, the lower this number
# the faster the motor turns
MOTOR_DELAY = 0.01

# The pins on the Raspberry pi used to drive the motor controller(s)
MOTOR_1_PHASE_A = 6
MOTOR_1_PHASE_B = 13
MOTOR_1_PHASE_C = 19
MOTOR_1_PHASE_D = 26
MOTOR_2_PHASE_A = 12
MOTOR_2_PHASE_B = 16
MOTOR_2_PHASE_C = 20
MOTOR_2_PHASE_D = 21


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
    if get_location(tracker) == "mortal peril":
        return 0
    elif get_location(tracker) == "friends":
        return 1
    elif get_location(tracker) == "family":
        return 2
    elif get_location(tracker) == "work":
        return 3
    elif get_location(tracker) == "home":
        return 4
    elif get_location(tracker) == "not_home" and get_travelling(proximity) \
            == "towards" or get_travelling(proximity) == "away_from":
        # Point clock hand to traveling
        return 5
    elif get_location(tracker) == "school":
        return 6
    elif get_location(tracker) == "hospital":
        return 7
    elif get_location(tracker) == "prison":
        return 9
    else:
        # Point clock hand to "elsewhere".
        return 8


def move_clock_hand(hand_num, new_position):
    """Calculate how many steps to move the hand and store the
    new hand position"""
    steps = 0
    if new_position == CLOCK_HANDS[hand_num]:
        pass
    else:
        num_steps = new_position - CLOCK_HANDS[hand_num]
        CLOCK_HANDS[hand_num] = CLOCK_HANDS[hand_num] + num_steps
        if num_steps > 0:
            forward(num_steps * 51, hand_num)
        elif num_steps < 0:
            backwards(abs(num_steps * 51), hand_num)
        write_hand_position_to_file(hand_num, new_position)


def write_hand_position_to_file(hand_position, hand_num):
    """Write new postion of the clock hand to config file, so we know
       where it is on next program start"""
    with open("config.json", "r+") as config:
        if hand_num is None:
            config.truncate(0)
            config_json["clock_hands"] = hand_position
            config.seek(0)
            json.dump(config_json, config, indent=1)
        else:
            config.truncate(0)
            config_json["clock_hands"][hand_num] = hand_position
            config.seek(0)
            json.dump(config_json, config, indent=1)


# Reads config file for Home Assistant password, entity IDs
# Home assistant URL, and interval in seconds between updates
try:
    with open("config.json", "r") as config:
        config_json = json.loads(config.read())
        PWD = config_json["password"]
        TRACKERS = config_json["trackers"]
        PROXIMITIES = config_json["proximities"]
        URL = config_json["url"]
        UPDATE_INTERVAL = config_json["update_interval"]
except FileNotFoundError:
    print ("config.txt file not found. See readme for instructions "
           "on setting up config.txt")
    exit()
except KeyError:
    print ("Config.txt not set up correctly. See readme for instructions "
           "on setting up config.txt")
    exit()


# Try reading clock hands position from the config file, if it is not found
# then set them all to 0
with open("config.json", "r+") as config:
    config_json = json.loads(config.read())
    try:
        CLOCK_HANDS = config_json["clock_hands"]
    except KeyError:
        CLOCK_HANDS = []
        for i in range(len(TRACKERS)):
            CLOCK_HANDS.append(0)
        write_hand_position_to_file(CLOCK_HANDS, None)


def __main__():
    try:
        while True:
            # Iterate through how ever many trackers you have set up
            # Getting the new position and moving the clock hand for each
            for i in range(len(TRACKERS)):
                new_position = get_status(TRACKERS[i], PROXIMITIES[i])
                move_clock_hand(i, new_position)
                time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()

if __name__ == "__main__":
    __main__()
