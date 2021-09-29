import config
from fileio import FileIO
import json
from motor import Motor
import psutil
import requests
import time
import traceback


fileIO = FileIO()
motor = Motor(config.MOTOR_PINS, config.MOTOR_DELAY)

class MagicClock:
    def __init__(self):
#        self.zones = self.get_zones()
        self.hands = fileIO.read_hand_positions_from_file()


    # def access_response(self, response, accessor):
    #     split_accessor = accessor.split(".")
    #     for item in split_accessor:
    #         response = response[item]
    #     return response


#    def get_zones(self):
#        """Get the location zones from Home Assistant API"""
#        headers = {
#            "Authorization": "Bearer {}".format(config.ACCESS_TOKEN),
#            "content-type": "application/json",
#        }
#        try:
#            if type(config.ZONES) is str:
#                response = requests.get(config.ZONES, headers=headers, timeout=5)
#                response.raise_for_status()
#                zones = config.zones_accessor(json.loads(response.text))
#                return zones
#            else:
#                return config.ZONES
#
#        except:
#            message = "error getting list of zones from {}".format(config.ZONES)
#            fileIO.write_log(message)
#            fileIO.write_log(traceback.format_exc())
#            return []


    def update_location(self, url_index):
        """Get location from the Home Assistant Api"""
        headers = {
            "Authorization": "Bearer {}".format(config.ACCESS_TOKEN),
            "content-type": "application/json",
        }
        try:
            response = requests.get(config.LOCATION_URLS[url_index], headers=headers, timeout=5)
            response.raise_for_status()
            response_json = json.loads(response.text)

            self.zone = response_json["state"]
#            self.latitude = config.latitude_accessor(response_json)
#            self.longitude = config.longitude_accessor(response_json)
            return
        except ():
            message = "error getting location for {}".format(config.LOCATION_URLS[url_index])
            fileIO.write_log(message)
            fileIO.write_log(traceback.format_exc())
            return


    def update_travelling(self, url_number):
        """Get proximity status from the Home Assistant Api"""
        headers = {
            "Authorization": "Bearer {}".format(config.ACCESS_TOKEN),
            "content-type": "application/json",
        }
        try:
           response = requests.get(config.LOCATION_URLS[url_number], headers=headers, timeout=5)
           response.raise_for_status()
           self.travelling = int(json.loads(response.text)["attributes"]["speed"])

           return
        except:
            message = "error getting travelling status for {}".format(config.LOCATION_URLS[url_number])
            fileIO.write_log(message)
            fileIO.write_log(traceback.format_exc())
            self.travelling = 0
            return


#    def update_zone(self):
#        """Iterate through zones and return the first that we are located in."""
#        try:
#            for zone in self.zones:
#                latitude_meters_diff = abs(zone["latitude"] - self.latitude) * 111139
#                longitude_meters_diff = abs(zone["longitude"] - self.longitude) * 111139
#
#                if latitude_meters_diff < zone["radius"] and longitude_meters_diff < zone["radius"]:
#                    self.zone = zone["friendly_name"].lower()
#                    return
#            self.zone = None
#            return
#        except:
#            fileIO.write_log("Error while attempting to find current zone")
#            fileIO.write_log(traceback.format_exc())
#            self.zone = None
#            return


    def update_hand_position(self):
        """Gets the location and proximity states from Home Assistant and
        returns an int corresponding to location on the clock face"""
        try:
            if self.zone == "home":
                return 4
            elif (self.travelling >= 5):
                return 5
            elif self.zone == "mortal peril":
                return 0
            elif self.zone == "friends" and self.travelling < 5:
                return 1
            elif self.zone == "family" and self.travelling < 5:
                return 2
            elif self.zone == "work" and self.travelling < 5:
                return 3
            elif self.zone == "school" and self.travelling < 5:
                return 6
            elif self.zone == "hospital" and self.travelling < 5:
                return 7
            else:
                # Point clock hand to "elsewhere".
                return 8
        except:
            fileIO.write_log("Error while attempting to update clock hand position")
            fileIO.write_log(traceback.format_exc())

def main():
    fileIO.write_log("Program started")

    clock = MagicClock()
    try:
        while (True):
            # Iterate through how ever many trackers you have set up
            # Getting the new position and moving the clock hand for each
            for i in range(len(config.LOCATION_URLS)):
                clock.update_location(i)
                clock.update_travelling(i)
#                clock.update_zone()

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
        fileIO.write_log("Unexpected exception in main program loop")
        fileIO.write_log(traceback.format_exc())


main()
