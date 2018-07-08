Magic Clock

A Python program which reads locations from Home Assistant and controls
stepper motors, connected to a Raspberry Pi, to point clock hands at the
corresponding location on a clock face.


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

Sample config.json

{
"password": "HOME_ASSISTANT_API_PASSWORD",
"trackers": ["DEVICE_TRACKER.TRACKER1", "DEVICE_TRACKER.TRACKER2"],
"proximities": ["PROXIMITY.PROXIMITY1", "PROXIMITY.PROXIMITY2"],
"url": "URL_AND_PORT_NUMBER_FOR_HOME_ASSISTANT",
"update_interval": NUMBER_OF_SECONDS_BETWEEN_UPDATES,
"clock_hands": [0, 0, ...]
}
