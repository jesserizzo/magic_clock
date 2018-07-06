Magic Clock

A Python program which reads locations from Home Assistant and controls
stepper motors, connected to a Raspberry Pi, to point clock hands at the
corresponding location on a clock face.




Sample config.txt

{
"password": "HOME_ASSISTANT_API_PASSWORD",
"trackers": ["DEVICE_TRACKER.TRACKER1", "DEVICE_TRACKER.TRACKER2"],
"proximities": ["PROXIMITY.PROXIMITY1", "PROXIMITY.PROXIMITY2"],
"url": "URL_AND_PORT_NUMBER_FOR_HOME_ASSISTANT",
"update_interval": NUMBER_OF_SECONDS_BETWEEN_UPDATES
}
