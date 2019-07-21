import magic_clock
from fileio import FileIO
import motor
import RPi.GPIO as GPIO
import time

fileIO = FileIO()
motor = motor.Motor(fileIO.dict["motor_pins"], fileIO.dict["motor_delay"], fileIO.dict["clock_hands"])

print("starting test")
fileIO.write_log("testing write to log")

print("moving clock hand 0 to position 3")
motor.move_clock_hand(0,3)

print("wait for five seconds")
time.sleep(5)

print("moving clock hand 0 to position 4")
motor.move_clock_hand(0,4)

print("test complete")
