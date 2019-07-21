import config
from fileio import FileIO
import json
from motor import Motor
import requests
import time
import traceback


fileIO = FileIO()
motor = Motor(config.MOTOR_PINS, config.MOTOR_DELAY)

class MagicClock:
    def __init__(self):
        self.zones = self.get_zones()
        self.hands = fileIO.read_hand_positions_from_file()

    def get_zones(self):
        """Get the location zones from Home Assistant API"""
        url = "{}/api/states".format(config.URL)
        headers = {
            "Authorization": "Bearer {}".format(config.ACCESS_TOKEN),
            "content-type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            zones = list(filter(lambda x: "zone" in x["entity_id"], json.loads(response.text)))
            zones_attributes = list(map(lambda y: y["attributes"], zones))
            return zones_attributes 
        except (requests.exceptions.RequestException, ValueError):
            message = "error getting location for {}".format(tracker)
            print(message)
            fileIO.write_log(message)
            return


    def update_location(self, tracker):
        """Get  location from the Home Assistant Api"""
        url = "{}/api/states/{}".format(config.URL, tracker)
        headers = {
            "Authorization": "Bearer {}".format(config.ACCESS_TOKEN),
            "content-type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            response_json = json.loads(response.text)
            #self.location = response_json["state"]
            self.latitude = response_json["attributes"]["latitude"]
            self.longitude = response_json["attributes"]["longitude"]
            return
        except (requests.exceptions.RequestException, ValueError):
            message = "error getting location for {}".format(tracker)
            print(message)
            fileIO.write_log(message)
            return


    def update_travelling(self, proximity):
        """Get proximity status from the Home Assistant Api"""
        url = "{}/api/states/{}".format(config.URL, proximity)
        headers = {
            "Authorization": "Bearer {}".format(config.ACCESS_TOKEN),
            "content-type": "application/json",
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            self.travelling = json.loads(response.text)["attributes"]["dir_of_travel"]
            return
        except (requests.exceptions.RequestException, ValueError):
            message = "error getting travelling status for {}".format(proximity)
            print(message)
            fileIO.write_log(message)
            return

    def update_zone(self):
        """Iterate through zones and return the first that we are located in."""
        for zone in self.zones:
            diff_latitude = abs(zone["latitude"] - self.latitude) * 111139
            diff_longitude = abs(zone["longitude"] - self.longitude) * 111139

            if diff_latitude < zone["radius"] and diff_longitude < zone["radius"]:
                self.zone = zone["friendly_name"].lower()
                return
        self.zone = None
        return


    def update_hand_position(self):
        """Gets the location and proximity states from Home Assistant and
        returns an int corresponding to location on the clock face"""

        if self.zone == "home":
            return 4
        elif (self.zone == "towards" or self.travelling == "away_from"):
            return 5
        elif self.zone == "mortal peril":
            return 0
        elif self.zone == "friends" and self.travelling == "stationary":
            return 1
        elif self.zone == "family" and self.travelling == "stationary":
            return 2
        elif self.zone == "work" and self.travelling == "stationary":
            return 3
        elif self.zone == "school" and self.travelling == "stationary":
            return 6
        elif self.zone == "hospital" and self.travelling == "stationary":
            return 7
        else:
            # Point clock hand to "elsewhere".
            return 8


def __main__():
    try:
        fileIO.write_log("Program started")
        print("Program started")
        
        clock = MagicClock()
        while True:         
            # Iterate through how ever many trackers you have set up
            # Getting the new position and moving the clock hand for each
            for i in range(len(config.TRACKERS)):
                clock.update_location(config.TRACKERS[i])
                clock.update_travelling(config.PROXIMITIES[i])
                clock.update_zone()
                
                new_position = clock.update_hand_position()

                num_steps = new_position - clock.hands[i]
                motor.move_clock_hand(i, num_steps)

                clock.hands[i] = new_position
                fileIO.write_hands_to_file(clock.hands)

            time.sleep(config.UPDATE_INTERVAL)
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
