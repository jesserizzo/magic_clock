from magic_clock import MagicClock
from fileio import FileIO
import motor
import RPi.GPIO as GPIO
import time

fileIO = FileIO()
motor = motor.Motor(fileIO.dict["motor_pins"], fileIO.dict["motor_delay"], [])
magic_clock = MagicClock()


def wiggle_hands():
    print("starting test")

    num_steps = input("Number of positions to move hand? ")
    print("moving clock hand forward {} position".format(num_steps))
    motor.move_clock_hand(1, int(num_steps))

    print("wait for one second")
    time.sleep(1)

    print("moving clock hand back")
    motor.move_clock_hand(1,-int(num_steps))

    print("test complete")


def input_lat_long():
    latitude = input("Input latitude: ")
    longitude = input("Input longitude: ")

    print("Moving clock hand to zone that corresponds to {} {}".format(latitude, longitude))

    magic_clock.latitude = float(latitude)
    magic_clock.longitude = float(longitude)
    magic_clock.travelling = "stationary"
    magic_clock.update_zone()

    new_position = magic_clock.update_hand_position()
    num_steps = new_position - fileIO.dict["clock_hands"][0]

    motor.move_clock_hand(0, num_steps)
    time.sleep(1)
    print("Moving hand back.")
    motor.move_clock_hand(0, -num_steps)


def input_location_name():
    location = input("Input location name: ")
    print("Moving hand to {}".format(location))

    magic_clock.zone = location
    magic_clock.travelling = "stationary"

    new_position = magic_clock.update_hand_position()
    num_steps = new_position - fileIO.dict["clock_hands"][0]
    
    motor.move_clock_hand(0, num_steps)
    time.sleep(1)
    print("Moving hand back.")
    motor.move_clock_hand(0, -num_steps)


while True:
    print("Select test to run: ")
    print("1. Wiggle clock hands")
    print("2. Input name of location")
    print("3. Input Lat / Long")
    print("4. Test writing to log")
    print("(q)uit")
    user_input = input()

    if user_input == "1":
        wiggle_hands()
    
    elif user_input == "2":
        input_location_name()

    elif user_input == "3":
        input_lat_long()

    elif user_input == "4":
        fileIO.write_log("Test writing to log")
        print("Test write to log complete")

    elif user_input == "q":
        exit()
    
    else:
        print ("Try again")