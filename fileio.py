import config
from datetime import datetime
import json
import pathlib

class FileIO:

    def write_hands_to_file(self, new_hands):
        """Write new postion of the clock hand to config file, so we know
        where it is on next program start"""

        with open("/home/pi/magic_clock/magic_clock.save", "w") as save:
            to_write = ""
            for hand in new_hands:
                to_write += "{}\n".format(hand)
            save.write(to_write)


    def read_hand_positions_from_file(self):
        try:
            with open("/home/pi/magic_clock/magic_clock.save", "r") as save:
                lines = save.readlines()
                hands = []
                for line in lines:
                    hand = int(line)
                    hands.append(hand)
                return hands
        except FileNotFoundError:
            new_hands = []
            for i in range(len(config.URLS)):
                new_hands.append(0)
            self.write_hands_to_file(new_hands)
            return new_hands


    def write_log(self, message):
        try:
            with open("/home/pi/magic_clock/magic_clock.log", "a+") as log:
                log.write(
                    "{} - {}\n".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message
                    )
                )
                print(message)
            with open(pathlib.Path(__file__).parent / "magic_clock.log", "r+") as log:
                # If there is too many lines in the log, go back to the beginning
                # of the file, over write with the number of lines we should
                # have and truncate the rest of the file
                lines = log.readlines()
                if len(lines) > config.MAX_LOG_LINES:
                    log.seek(0)
                    for i in range(
                        len(lines) - config.MAX_LOG_LINES, len(lines)
                    ):
                        log.write(lines[i])
                    log.truncate()
        except:
            return
