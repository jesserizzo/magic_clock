import access_token

# Put Home assistant access token in a file named access_token.py
# Make sure not to commit this file
ACCESS_TOKEN = access_token.ACCESS_TOKEN

# Accessor function to get latitude and longitude from LOCATION_URLS response
# For example, if the api returns 
# { "entity_id": "example_entity", attributes": { "latitude": 10, longitude: 100, accuracy: 123 } }
# Then see below functions
def latitude_accessor(response):
    return response["attributes"]["latitude"]
def longitude_accessor(response):
    return response["attributes"]["longitude"]

# Urls to query to get the latitude / longitude coordinates, one url per clock hand
LOCATION_URLS = ["http://192.168.1.20:8123/api/states/device_tracker.jesse_motox4", "http://192.168.1.20:8123/api/states/device_tracker.megan_motog4"]

# Max number of entries to save in magic_clock.log, on reaching this
# limit it will overwrite the oldest entries
MAX_LOG_LINES = 1000

# Number of seconds to wait between steps of the stepper motor
# The lower this number the faster the motor will turn
MOTOR_DELAY = 0.004

# The pin numbers of the Raspberry Pi that are connected to each stepper motor
MOTOR_PINS = [[6, 13, 19, 26], [12, 16, 20, 21]]

# Time to wait between API queries
UPDATE_INTERVAL = 10

# List of Zone objects OR string URL to query
# Must return [ { friendly_name: string, radius: int, latitude: float, longitude: float } ]
ZONES = "http://192.168.1.20:8123/api/states"

# Accessor function to get the list of zones from the response
# for the ZONES api call
def zones_accessor(response):
    zones = list(filter(lambda x: x["state"] == "zoning", response))
    zones_attributes = list(map(lambda y: y["attributes"], zones))
    return zones_attributes



