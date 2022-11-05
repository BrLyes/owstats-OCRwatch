# importing the requests library
import requests
import configparser
import json

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

def supported_characters():
    r = requests.get(url = API_ENDPOINT+'chars', headers=headers)
    characters = []
    json = r.json()
    for value in json:
            characters.append(value["name"])
    return characters

def send_to_owstats(data):
    r = requests.post(url = API_ENDPOINT+'games', data = data, headers=headers)
    print(r.text)

def is_character_supported(character):
    arr_supported_characters = supported_characters()
    print(arr_supported_characters)
    if character not in arr_supported_characters:
        return False
    else:
        return True
