import os
import json

if __name__ == "__main__":
    # for each rsu
    # for each road
    # for each connection
    rsu2Road = {}
    with open('serviceRoad.json', 'r', encoding='utf-8') as file:
        serviceRoad = json.loads(file.read())
    with open('roadConnection.json', 'r', encoding='utf-8') as file:
        roadConnection = json.loads(file.read())
    for road, item in serviceRoad.items():
        try:
            rsu2Road[item['RSU']].append(road)
        except:
            rsu2Road[item['RSU']] = [road]
    for rsu in rsu2Road.keys():
        localProfit = 0
        for road in rsu2Road[rsu]:
            print(serviceRoad[road]['poi'])