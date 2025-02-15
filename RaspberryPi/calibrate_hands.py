import config
from fileio import FileIO
from motor import Motor


hand_num = 0
fileIO = FileIO()
motor = Motor(config.MOTOR_PINS, config.MOTOR_DELAY)


while True:
    left_or_right = input("Enter (l)eft, (r)ight, (q)uit, or s(witch) to switch hands. ")

    if (left_or_right == "q"):
        exit()

    elif left_or_right == "s":
        if hand_num == len(config.MOTOR_PINS):
            hand_num = 0
        else:
            hand_num += 1

    elif left_or_right == "l":
        num_steps = input("Number of steps? ")
        motor.backwards(int(num_steps), hand_num)
        motor.set_step(hand_num, [0, 0, 0, 0])
    elif left_or_right == "r":
        num_steps = input("Number of steps? ")
        motor.forward(int(num_steps), hand_num)
        motor.set_step(hand_num, [0, 0, 0, 0])
