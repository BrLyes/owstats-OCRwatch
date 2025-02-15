import configparser
import csv
import time
import datetime
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from tabulate import tabulate

from util import write_json
from owstats import send_to_owstats,is_character_supported
from usertimezone import time_to_utc

config = configparser.ConfigParser()
config.read("config.ini")


def write_output(result):
    if config.getboolean("output", "json"):
        write_to_json(result)
    if config.getboolean("output", "csv"):
        append_to_csv(result)
    if config.getboolean("output", "influx"):
        write_to_influx(result)
    if config.getboolean("output", "owstats"):
        write_to_owstats(result)


def write_rank(rank, ranks):
    if config.getboolean("output", "influx"):
        write_rank_to_influx(rank, ranks)


def write_to_json(result):
    write_json('latest.json', result)

def write_to_owstats(result):
    game = []

    #Find the player stats within players.allies
    print("looking for")
    print(result["self"]["name"])
    print("in")
    print(result)
    for i in range(0, 5):
        if result["players"]["allies"][i]["name"] == result["self"]["name"]:
            game = result["players"]["allies"][i]
    print("found game:")
    print(game)

    #Get character name and capitalize first letter to pass API validation
    print("Getting character name and capitalize it")
    strCharacterName = result["self"]["hero"].capitalize()
    print(strCharacterName)

    #Check if character is supported
    print("checking if character is supported by the API")
    if is_character_supported(strCharacterName):
        print("Character supported")
        print("Payload")
        payload = {
            'name': strCharacterName,
            'kill':game["elims"],
            'death':game["deaths"],
            'assist':game["assists"],
            'damage':game["dmg"],
            'heal':game["heal"],
            'mitigate':game["mit"],
            'match_date':time_to_utc(),
        }
        print(payload)
        send_to_owstats(payload)
        return True
    else :
        print("Unsupported characters "+strCharacterName)
        return False



def append_to_csv(result):
    fields = [result['time'], result['match']['mode'], result['match']['map'], result['match']['time'], result['self']['hero']]

    for i in range(0, 5):
        fields.append(result['players']['allies'][i]['name'])
        fields.append(result['players']['allies'][i]['elims'])
        fields.append(result['players']['allies'][i]['assists'])
        fields.append(result['players']['allies'][i]['deaths'])
        fields.append(result['players']['allies'][i]['dmg'])
        fields.append(result['players']['allies'][i]['heal'])
        fields.append(result['players']['allies'][i]['mit'])

    for i in range(0, 5):
        fields.append(result['players']['enemies'][i]['name'])
        fields.append(result['players']['enemies'][i]['elims'])
        fields.append(result['players']['enemies'][i]['assists'])
        fields.append(result['players']['enemies'][i]['deaths'])
        fields.append(result['players']['enemies'][i]['dmg'])
        fields.append(result['players']['enemies'][i]['heal'])
        fields.append(result['players']['enemies'][i]['mit'])

    with open(r'log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)


influx_client = InfluxDBClient.from_config_file("config.ini")
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)


def write_to_influx(result):
    parsed_time = datetime.strptime(result['match']['time'], "%M:%S")
    duration = timedelta(minutes=parsed_time.minute, seconds=parsed_time.second)

    print("")
    print("")
    print("")

    print(result['match']['mode'] + " - " + ("Competitive" if result['match']['competitive'] else "Quick Play") + " | " + result['match']['map'])
    print("Time: " + result['match']['time'])

    print("")

    headers = ["Name", "E", "A", "D", "Damage", "Heal", "MIT"]

    ally_total_elims = 0
    ally_total_assists = 0
    ally_total_deaths = 0
    ally_total_dmg = 0
    ally_total_heal = 0
    ally_total_mit = 0

    ally_table = []

    for i in range(0, 5):
        ally_total_elims += result['players']['allies'][i]['elims']
        ally_total_assists += result['players']['allies'][i]['assists']
        ally_total_deaths += result['players']['allies'][i]['deaths']
        ally_total_dmg += result['players']['allies'][i]['dmg']
        ally_total_heal += result['players']['allies'][i]['heal']
        ally_total_mit += result['players']['allies'][i]['mit']

        row = []
        row.append(result['players']['allies'][i]['name'])
        row.append(result['players']['allies'][i]['elims'])
        row.append(result['players']['allies'][i]['assists'])
        row.append(result['players']['allies'][i]['deaths'])
        row.append(result['players']['allies'][i]['dmg'])
        row.append(result['players']['allies'][i]['heal'])
        row.append(result['players']['allies'][i]['mit'])
        ally_table.append(row)

    ally_table.append(["=> TOTAL", ally_total_elims, ally_total_assists, ally_total_deaths, ally_total_dmg, ally_total_heal, ally_total_mit])
    print("Allies:")
    print(tabulate(ally_table, headers=headers, tablefmt="grid"))

    print("")

    enemy_total_elims = 0
    enemy_total_assists = 0
    enemy_total_deaths = 0
    enemy_total_dmg = 0
    enemy_total_heal = 0
    enemy_total_mit = 0

    enemy_table = []

    for i in range(0, 5):
        enemy_total_elims += result['players']['enemies'][i]['elims']
        enemy_total_assists += result['players']['enemies'][i]['assists']
        enemy_total_deaths += result['players']['enemies'][i]['deaths']
        enemy_total_dmg += result['players']['enemies'][i]['dmg']
        enemy_total_heal += result['players']['enemies'][i]['heal']
        enemy_total_mit += result['players']['enemies'][i]['mit']

        row = []
        row.append(result['players']['enemies'][i]['name'])
        row.append(result['players']['enemies'][i]['elims'])
        row.append(result['players']['enemies'][i]['assists'])
        row.append(result['players']['enemies'][i]['deaths'])
        row.append(result['players']['enemies'][i]['dmg'])
        row.append(result['players']['enemies'][i]['heal'])
        row.append(result['players']['enemies'][i]['mit'])
        enemy_table.append(row)

    enemy_table.append(["=> TOTAL", enemy_total_elims, enemy_total_assists, enemy_total_deaths, enemy_total_dmg, enemy_total_heal, enemy_total_mit])
    print("Enemies:")
    print(tabulate(enemy_table, headers=headers, tablefmt="grid"))

    print("")
    print(">", result['state'])

    print("")
    print("")
    print("")

    p = Point("match_stats") \
        .tag("mode", result['match']['mode']) \
        .tag("map", result['match']['map']) \
        .tag("hero", result['self']['hero']) \
        .tag("competitive", 'true' if result['match']['competitive'] else 'false') \
        .tag("state", result['state']) \
        .field("duration", duration.total_seconds()) \
        .field("total_ally_elims", ally_total_elims) \
        .field("total_enemy_elims", enemy_total_elims) \
        .field("total_ally_deaths", ally_total_deaths) \
        .field("total_enemy_deaths", enemy_total_deaths) \
        .field("total_ally_assists", ally_total_assists) \
        .field("total_enemy_assists", enemy_total_assists)
    print(p)
    influx_write_api.write(bucket="overwatch", record=p)


def write_rank_to_influx(rank, ranks):
    ind = ranks.index(rank)
    p = Point("rank") \
        .tag("rank", rank) \
        .field("rank", ind)
    print(p)
    influx_write_api.write(bucket="overwatch", record=p)
