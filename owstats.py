# importing the requests library
import requests
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


API_ENDPOINT = config.get("owstats", "API_ENDPOINT")
HEADER_AUTHORIZATION = config.get("owstats", "HEADER_AUTHORIZATION")

# Headers
headers = {
'Accept': 'application/json',
'Authorization': HEADER_AUTHORIZATION
}

# Response
r = ""

def send_to_owstats(data):
    r = requests.post(url = API_ENDPOINT, data = data, headers=headers)
    # extracting response text
    print(r.text)
