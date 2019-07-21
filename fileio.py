import json
from datetime import datetime

class FileIO:

    def __init__(self):
        self.dict = {}
        self.read_tries = 0
        self.read_config_file()


    def write_hand_position_to_file(self, hand_position, hand_num):
        """Write new postion of the clock hand to config file, so we know
        where it is on next program start"""
        with open("config.json", "r+") as config:
            config_json = json.loads(config.read())
            if hand_num is None:
                self.dict["clock_hands"] = hand_position
                config.truncate(0)
                config_json["clock_hands"] = hand_position
                config.seek(0)
                json.dump(config_json, config, indent=1)
            else:
                self.dict["clock_hands"][hand_num] = hand_position
                config.truncate(0)
                config_json["clock_hands"][hand_num] = hand_position
                config.seek(0)
                json.dump(config_json, config, indent=1)


    def read_config_file(self):
        """Reads config.json file for some constants"""
        try:
            with open("/home/pi/magic_clock/config.json", "r") as config:
                config_json = json.loads(config.read())
                try:
                    self.dict["access_token"] = config_json["access_token"]
                    self.dict["trackers"] = config_json["trackers"]
                    self.dict["group_location"] = config_json["group_location"]
                    self.dict["proximities"] = config_json["proximities"]
                    self.dict["url"] = config_json["url"]
                    self.dict["motor_pins"] = config_json["motor_pins"]
                    self.dict["motor_delay"] = config_json["motor_delay"]
                except KeyError:
                    message = "config.json not set up correctly. See readme for "
                    message += "instructions on setting up config.json"
                    print(message)
                    self.write_log(message)
                    exit()

                # Reads max log lines from the config, default to 100
                try:
                    self.dict["max_log_lines"] = config_json["max_log_lines"]
                except KeyError:
                    self.dict["max_log_lines"] = 100

                # Reads update interval from config.json, defaults to 60 seconds
                try:
                    self.dict["update_interval"] = config_json["update_interval"]
                except KeyError:
                    self.dict["update_interval"] = 60

                # Reads clock hands position from the config file, defaults to
                # all at 0
                try:
                    self.dict["clock_hands"] = config_json["clock_hands"]
                except KeyError:
                    self.dict["clock_hands"] = []
                    for i in range(len(self.dict["trackers"])):
                        self.dict["clock_hands"].append(0)
                    write_hand_position_to_file(self.dict["clock_hands"], None)

        except FileNotFoundError:
            message = "config.json file not found. See readme for instructions "
            message += "on setting up config.json"
            print(message)
            self.write_log(message)
            time.sleep(60)

            if self.read_tries > 3:
                message = "Unable to read config.json. Shutting down"
                print(message)
                self.write_log(message)
                exit()
            self.read_tries += 1
            self.read_config_file()

        except json.JSONDecodeError:
            message = "config.json file not set up correctly. See readme for "
            message += "instructions on setting up config.json"
            print(message)
            self.write_log(message)
            exit()


    def write_log(self, message):
        try:
            with open("magic_clock.log", "a+") as log:
                log.write(
                    "{} - {}\n".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message
                    )
                )
            with open("magic_clock.log", "r+") as log:
                # If there is too many lines in the log, go back to the beginning
                # of the file, over write with the number of lines we should
                # have and truncate the rest of the file
                lines = log.readlines()
                if len(lines) > self.dict["max_log_lines"]:
                    log.seek(0)
                    for i in range(
                        len(lines) - self.dict["max_log_lines"], len(lines)
                    ):
                        log.write(lines[i])
                    log.truncate()
        except:
            return
