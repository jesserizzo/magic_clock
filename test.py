import requests
import json

"""PWD = "GOQzhm1YT8b4ssxP81bA"
TRACKERS = ["device_tracker.google_maps_115948204649955307306"]
PROXIMITIES = ["proximity.home"]


url = "http://192.168.1.11:8123/api/states/{}?api_password={}".format(TRACKERS[0], PWD)
try:
    response = requests.get(url, timeout=5)
    print (json.loads(response.text)["state"])
except (requests.exceptions.RequestException, ValueError):
    print("error getting location for {}".format(tracker))


url = "http://192.168.1.11:8123/api/states/{}?api_password={}".format(PROXIMITIES[0], PWD)
try:
    response = requests.get(url, timeout=5)
    print (json.loads(response.text)["attributes"]["dir_of_travel"])
except (requests.exceptions.RequestException, ValueError):
    print("error getting travelling status for {}".format(proximity))"""


with open("config.txt") as file:
    text = file.readline()

    x = json.loads(text)
    print(x["password"])
