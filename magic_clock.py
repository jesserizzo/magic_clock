import requests
import json
import RPi.GPIO as GPIO
import time
from datetime import datetime
import traceback


CONFIG_DICT = {}


def setup_GPIO():
    """Set up the GPIO pins on the Raspberry Pi to outputs"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in CONFIG_DICT["motor_pins"]:
        GPIO.setup(pin, GPIO.OUT)


def read_config_file(read_tries=1):
    """Reads config.json file for some constants"""
    try:
        with open("config.json", "r") as config:
            config_json = json.loads(config.read())
            try:
                CONFIG_DICT["password"] = config_json["password"]
                CONFIG_DICT["trackers"] = config_json["trackers"]
                CONFIG_DICT["proximities"] = config_json["proximities"]
                CONFIG_DICT["url"] = config_json["url"]
                CONFIG_DICT["motor_pins"] = config_json["motor_pins"]
                CONFIG_DICT["motor_delay"] = config_json["motor_delay"]
            except KeyError:
                message = "config.json not set up correctly. See readme for "
                message += "instructions on setting up config.json"
                print (message)
                write_log(message)
                exit()

            # Reads max log lines from the config, default to 100
            try:
                CONFIG_DICT["max_log_lines"] = config_json["max_log_lines"]
            except KeyError:
                CONFIG_DICT["max_log_lines"] = 100

            # Reads update interval from config.json, defaults to 60 seconds
            try:
                CONFIG_DICT["update_interval"] = \
                    config_json["update_interval"]
            except KeyError:
                CONFIG_DICT["update_interval"] = 60

            # Reads clock hands position from the config file, defaults to
            # all at 0
            try:
                CONFIG_DICT["clock_hands"] = config_json["clock_hands"]
            except KeyError:
                CONFIG_DICT["clock_hands"] = []
                for i in range(len(CONFIG_DICT["trackers"])):
                    CONFIG_DICT["clock_hands"].append(0)
                write_hand_position_to_file(CONFIG_DICT["clock_hands"], None)

    except FileNotFoundError:
        message = "config.json file not found. See readme for instructions "
        message += "on setting up config.json"
        print (message)
        write_log(message)
        time.sleep(60)

        if read_tries > 4:
            message = "Unable to read config.json. Shutting down"
            print(message)
            write_log(message)
            exit()
        read_config_file(read_tries + 1)

    except json.JSONDecodeError:
        message = "config.json file not set up correctly. See readme for "
        message += "instructions on setting up config.json"
        print (message)
        write_log(message)
        exit()


def write_log(message):
    try:
        with open("magic_clock.log", "a+") as log:
            log.write("{} - {}\n".format(datetime.now().strftime
                                         ("%Y-%m-%d %H:%M:%S"), message))
        with open("magic_clock.log", "r+") as log:
            # If there is too many lines in the log, go back to the beginning
            # of the file, over write with the number of lines we should
            # have and truncate the rest of the file
            lines = log.readlines()
            if len(lines) > CONFIG_DICT["max_log_lines"]:
                log.seek(0)
                for i in range(len(lines) - CONFIG_DICT["max_log_lines"],
                               len(lines)):
                    log.write(lines[i])
                log.truncate()
    except:
        return


def set_step(motor_num, pins_high_or_low_list):
    """Set to high the specified pins to switch each step of the motor,
    see the arrays in backwards and forwards functions."""
    for i in range(4):
        GPIO.output(CONFIG_DICT["motor_pins"][motor_num][i],
                    pins_high_or_low_list[i])


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
            set_step(motor_num, backwards[j])
            time.sleep(CONFIG_DICT["motor_delay"])


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
            set_step(motor_num, forwards[j])
            time.sleep(CONFIG_DICT["motor_delay"])


def get_location(tracker):
    """Get  location from the Home Assistant Api"""
    url = "{}/api/states/{}".format(CONFIG_DICT["url"], tracker)
    headers = {'x-ha-access': CONFIG_DICT["password"],
               'content-type': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return (json.loads(response.text)["state"])
    except (requests.exceptions.RequestException, ValueError):
        message = "error getting location for {}".format(tracker)
        print(message)
        write_log(message)
        return


def get_travelling(proximity):
    """Get proximity status from the Home Assistant Api"""
    url = "{}/api/states/{}".format(CONFIG_DICT["url"], proximity)
    headers = {'x-ha-access': CONFIG_DICT["password"],
               'content-type': 'application/json'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return (json.loads(response.text)["attributes"]["dir_of_travel"])
    except (requests.exceptions.RequestException, ValueError):
        message = "error getting travelling status for {}".format(proximity)
        print(message)
        write_log(message)
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
    else:
        # Point clock hand to "elsewhere".
        return 8


def move_clock_hand(hand_num, new_position):
    """Calculate how many steps to move the hand, move it,
    and store the new hand position to file"""
    steps = 0
    if new_position == CONFIG_DICT["clock_hands"][hand_num]:
        pass
    else:
        num_steps = new_position - CONFIG_DICT["clock_hands"][hand_num]
        CONFIG_DICT["clock_hands"][hand_num] =\
            CONFIG_DICT["clock_hands"][hand_num] + num_steps
        # It's num_steps * 51 because the motor has 512 steps in a full
        # revolution, and I've got 10 locations on my clock face
        if num_steps > 0:
            forward(num_steps * 51, hand_num)
            # So the motor doesn't draw power when not moving
            set_step(hand_num, [0, 0, 0, 0])
        elif num_steps < 0:
            backwards(abs(num_steps * 51), hand_num)
            set_step(hand_num, [0, 0, 0, 0])
        write_hand_position_to_file(new_position, hand_num)


def write_hand_position_to_file(hand_position, hand_num):
    """Write new postion of the clock hand to config file, so we know
       where it is on next program start"""
    with open("config.json", "r+") as config:
        config_json = json.loads(config.read())
        if hand_num is None:
            CONFIG_DICT["clock_hands"] = hand_position
            config.truncate(0)
            config_json["clock_hands"] = hand_position
            config.seek(0)
            json.dump(config_json, config, indent=1)
        else:
            CONFIG_DICT["clock_hands"][hand_num] = hand_position
            config.truncate(0)
            config_json["clock_hands"][hand_num] = hand_position
            config.seek(0)
            json.dump(config_json, config, indent=1)


def __main__():
    try:
        write_log("Program started")
        read_config_file()
        setup_GPIO()
        while True:
            # Iterate through how ever many trackers you have set up
            # Getting the new position and moving the clock hand for each
            for i in range(len(CONFIG_DICT["trackers"])):
                new_position = get_status(CONFIG_DICT["trackers"][i],
                                          CONFIG_DICT["proximities"][i])
                move_clock_hand(i, new_position)
                time.sleep(CONFIG_DICT["update_interval"])
    except KeyboardInterrupt:
        write_log("Program shutdown by user")
        GPIO.cleanup()
        exit()
    except:
        write_log(traceback.format_exc())
        traceback.print_exc()
        exit()

if __name__ == "__main__":
    __main__()
