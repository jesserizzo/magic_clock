import requests
import json
import time
import traceback
from fileio import FileIO
import motor

fileIO = FileIO()
motor = motor.Motor(fileIO.dict["motor_pins"], fileIO.dict["motor_delay"], fileIO.dict["clock_hands"])


def get_location(tracker, group_location):
    """Get  location from the Home Assistant Api"""
    url = "{}/api/states/{}".format(fileIO.dict["url"], tracker)
    url_group = "{}/api/states/{}".format(fileIO.dict["url"], group_location)
    headers = {
          "Authorization": "Bearer {}".format(fileIO.dict["access_token"]),
          "content-type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response_group = requests.get(url_group, headers=headers, timeout=5)
        #print(str(response.status_code) + "location")
        #print(str(reponse_group.status_code) + "group location")
        return (json.loads(response.text)["state"], json.loads(response_group.text)["state"])
    except (requests.exceptions.RequestException, ValueError):
        message = "error getting location for {}".format(tracker)
        #print(message)
        fileIO.write_log(message)
        return


def get_travelling(proximity):
    """Get proximity status from the Home Assistant Api"""
    url = "{}/api/states/{}".format(fileIO.dict["url"], proximity)
    headers = {
        "Authorization": "Bearer {}".format(fileIO.dict["access_token"]),
        "content-type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        #print(str(response.status_code) + "traveling")
        return json.loads(response.text)["attributes"]["dir_of_travel"]
    except (requests.exceptions.RequestException, ValueError):
        message = "error getting travelling status for {}".format(proximity)
        #print(message)
        fileIO.write_log(message)
        return


def get_status(tracker, group_location, proximity):
    """Gets the location and proximity states from Home Assistant and
    returns an int corresponding to location on the clock face"""
    location_results = get_location(tracker, group_location)
    location = ""
    group_location = ""
    try:
        if (location_results):
            location = location_results[0]
            group_location = location_results[1]
    except:
        fileIO.write_log("Error parsing location results")

    travelling = get_travelling(proximity)

    if location == "" or group_location == "":
        return
    if location == "home":
        return 4
    elif (travelling == "towards" or travelling == "away_from"):
        return 5
    elif location == "mortal peril":
        return 0
    elif location == "friends" and travelling == "stationary":
        return 1
    elif location == "family" and travelling == "stationary":
        return 2
    elif location == "work" and travelling == "stationary":
        return 3
    elif location == "school" and travelling == "stationary":
        return 6
    elif location == "hospital" and travelling == "stationary":
        return 7
    else:
        # Point clock hand to "elsewhere".
        return 8


def __main__():
    try:
        fileIO.write_log("Program started")
        print("Program started")
        while True:
            # Iterate through how ever many trackers you have set up
            # Getting the new position and moving the clock hand for each
            for i in range(len(fileIO.dict["trackers"])):
                new_position = get_status(
                    fileIO.dict["trackers"][i], fileIO.dict["group_location"][i] ,fileIO.dict["proximities"][i]
                )
                if new_position != None:
                    num_steps = new_position - fileIO.dict["clock_hands"][i]
                    motor.move_clock_hand(i, num_steps)
                    fileIO.write_hand_position_to_file(new_position, i)
                time.sleep(fileIO.dict["update_interval"])
    except KeyboardInterrupt:
        fileIO.write_log("Program shutdown by user")
        motor.cleanup_GPIO()
        exit()
    except:
        fileIO.write_log(traceback.format_exc())
        traceback.print_exc()
        exit()


if __name__ == "__main__":
    __main__()
