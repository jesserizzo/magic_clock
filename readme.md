Magic Clock

A Python program which reads locations from Home Assistant and controls
stepper motors, connected to a Raspberry Pi, to point clock hands at the
corresponding location on a clock face.

Install:
From the command line of your Raspberry Pi run the following commands
$ mkdir magic_clock
$ cd magic_clock
$ sudo apt-get install git
$ git clone https://github.com/jesserizzo/magic_clock
$ ./install_requirements.sh

To run the program:
$ python3 magic_clock.py


Hardware setup

See https://www.raspberrypi.org/documentation/usage/gpio/ for pin numbers
on the Raspberry Pi. For the 28BYJ-48 motors and ULN2003 driver boards
that I used, you need 4 gpio pins, a 5 volt, and a ground for each motor.


Config

The config is saved in a config.json file. All parameters except "clock_hands"
and "update_interval" are required.
Parameters:
Password: The Home Assistant Api password. Leave as an empty string if you don't have a password set.
Trackers: A list of the entity ids for all the device trackers you want to use.
Proximities: A list of the entity ids for all the proximities you want to use.
Url: The Url or IP address, and port number of your Home Assistant server.
Update Interval: The interval in seconds between queries of your Home Assistant. If not included it defaults to 60 seconds
Clock Hands: A list of integers corresponding to the starting position of the clock hands. If not included it will set them all to 0.
Motor Delay: The time in seconds between each phase of the motor step. The lower this number the faster the motor will turn.
Motor Pins: A list of lists of the pins you have connected to your motor driver boards. They need to be listed as
            [motor 0 phase A, 0 phase B, 0 phase C, 0 phase D], [motor 1 phase A, 1 phase B, 1 phase C, 1 phase D], etc.
            There's no logical limit to the number of motors you can have, but you can only connect 6 to the Raspberry Pi.

Sample config.json

{
"password": "HOME_ASSISTANT_API_PASSWORD",
"trackers": ["DEVICE_TRACKER.TRACKER1", "DEVICE_TRACKER.TRACKER2"],
"proximities": ["PROXIMITY.PROXIMITY1", "PROXIMITY.PROXIMITY2"],
"url": "URL_AND_PORT_NUMBER_FOR_HOME_ASSISTANT",
"update_interval": NUMBER_OF_SECONDS_BETWEEN_UPDATES,
"clock_hands": [0, 0, ...],
"motor_delay": 0.01,
"motor_pins":[[1, 2, 3, 4], [5, 6, 7, 8], ...]
}
