import access_token

# Put Home assistant access token in a file named access_token.py
# Make sure not to commit this file
ACCESS_TOKEN = access_token.ACCESS_TOKEN

# Max number of entries to save in magic_clock.log, on reaching this
# limit it will overwrite the oldest entries
MAX_LOG_LINES = 1000

# Number of seconds to wait between steps of the stepper motor
# The lower this number the faster the motor will turn
MOTOR_DELAY = 0.004

# The pin numbers of the Raspberry Pi that are connected to each stepper motor
MOTOR_PINS = [[6, 13, 19, 26], [12, 16, 20, 21]]

# URLs for the travelling sensors
TRAVELLING_URLS = ["http://192.168.1.20:8123/api/states/proximity.jesse_home", "http://192.168.1.20:8123/api/states/proximity.megan_home"]

# Urls to query to get the latitude / longitude coordinates, should be one url per clock hand
URLS = ["http://192.168.1.20:8123/api/states/device_tracker.google_maps_115948204649955307306", "http://192.168.1.20:8123/api/states/device_tracker.google_maps_103614229965349669808"]

# Time to wait between API queries
UPDATE_INTERVAL = 10

# List of Zone objects 
# OR string URL to query
# Must return [ { friendly_name: string, radius: int, latitude: float, longitude: float } ]
ZONES = "http://192.168.1.20:8123/api/states"



