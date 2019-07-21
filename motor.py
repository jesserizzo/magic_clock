import RPi.GPIO as GPIO
from fileio import FileIO
import time


class Motor:
    def __init__(self, motor_pins, motor_delay, clock_hands):
        self.motor_pins = motor_pins
        self.motor_delay = motor_delay
        self.clock_hands = clock_hands
        self.setup_GPIO()


    def setup_GPIO(self):
        """Set up the GPIO pins on the Raspberry Pi to outputs"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self.motor_pins:
            GPIO.setup(pin, GPIO.OUT)

    def cleanup_GPIO(self):
        """Clean up GPIO"""
        GPIO.cleanup()


    def set_step(self, motor_num, pins_to_power):
        """Set to high the specified pins to switch each step of the motor,
        see the arrays in backwards and forwards functions."""
        for i in range(4):
            GPIO.output(
                self.motor_pins[motor_num][i], pins_to_power[i]
            )


    def backwards(self, steps, motor_num):
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
                self.set_step(motor_num, backwards[j])
                time.sleep(self.motor_delay)


    def forward(self, steps, motor_num):
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
                self.set_step(motor_num, forwards[j])
                time.sleep(self.motor_delay)

    def move_clock_hand(self, hand_num, num_steps):
        """Calculate how many steps to move the hand, move it,
        and store the new hand position to file"""
        # It's num_steps * 51 because the motor has 512 steps in a full
        # revolution, and I've got 10 locations on my clock face
        if num_steps > 0:
            self.forward(num_steps * 51, hand_num)
            # So the motor doesn't draw power when not moving
            self.set_step(hand_num, [0, 0, 0, 0])
        elif num_steps < 0:
            self.backwards(abs(num_steps * 51), hand_num)
            self.set_step(hand_num, [0, 0, 0, 0])