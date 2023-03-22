import os
import json
import sumolib
import numpy as np
import math
import copy

maxRate = 60

tasksEntertain = [
    {'cpu': 0.1, 'mem': 40, 'band': 12},
    {'cpu': 0.08, 'mem': 45, 'band': 15},
    {'cpu': 0.12, 'mem': 37, 'band': 10},
    {'cpu': 0.1, 'mem': 35, 'band': 9},
    {'cpu': 0.13, 'mem': 43, 'band': 13}
]
tasksTransPort = [
    {'cpu': 0.4, 'mem': 16, 'band': 6},
    {'cpu': 0.3, 'mem': 14, 'band': 5},
    {'cpu': 0.5, 'mem': 15, 'band': 5},
    {'cpu': 0.35, 'mem': 13, 'band': 7},
    {'cpu': 0.45, 'mem': 14, 'band': 4}
]
tasksWork = [
    {'cpu': 0.4, 'mem': 45, 'band': 6},
    {'cpu': 0.35, 'mem': 40, 'band': 6},
    {'cpu': 0.3, 'mem': 45, 'band': 5},
    {'cpu': 0.5, 'mem': 35, 'band': 7},
    {'cpu': 0.45, 'mem': 43, 'band': 4}
]
tasksHome = [
    {'cpu': 0.1, 'mem': 13, 'band': 15},
    {'cpu': 0.12, 'mem': 15, 'band': 12},
    {'cpu': 0.1, 'mem': 14, 'band': 10},
    {'cpu': 0.08, 'mem': 15, 'band': 13},
    {'cpu': 0.11, 'mem': 13, 'band': 11}
]


def RSUconfigRandom():
    RSUPos = []
    for i in range(9):
        for j in range(7):
            RSUPos.append([500 + i * 1000, 500 + j * 1000])
    print(RSUPos)

def calDistance(point, line_point1, line_point2):
    #对于两点坐标为同一点时,返回点与点的距离
    if line_point1 == line_point2:
        point_array = np.array(point )
        point1_array = np.array(line_point1)
        return np.linalg.norm(point_array -point1_array )
    #计算直线的三个参数
    A = line_point2[1] - line_point1[1]
    B = line_point1[0] - line_point2[0]
    C = (line_point1[1] - line_point2[1]) * line_point1[0] + \
        (line_point2[0] - line_point1[0]) * line_point1[1]
    #根据点到直线的距离公式计算距离
    distance = np.abs(A * point[0] + B * point[1] + C) / (np.sqrt(A**2 + B**2))
    return distance

if __name__ == "__main__":
    # for each rsu
    # for each road
    # for each connection
    rsuProfit = {}
    rsu2Road = {}
    cacheResult = {}
    net = sumolib.net.readNet('erlangen.net.xml')
    boundary = net.getBoundary()
    with open('RSUProperty.json', 'r', encoding='utf-8') as file:
        RSUProperty = json.loads(file.read())
    with open('serviceRoad.json', 'r', encoding='utf-8') as file:
        serviceRoad = json.loads(file.read())
    with open('roadConnection.json', 'r', encoding='utf-8') as file:
        roadConnection = json.loads(file.read())
    for road, item in serviceRoad.items():
        try:
            rsu2Road[item['RSU']].append(road)
        except:
            rsu2Road[item['RSU']] = [road]
    for i in range(9):
        for j in range(7):
            try:
                rsu2Road[str([500 + i * 1000, 500 + j * 1000])]
            except:
                rsu2Road[str([500 + i * 1000, 500 + j * 1000])] = []
    for rsuPos, property in RSUProperty.items():
        rsuPosList = list(map(int, rsuPos[1:-1].split(', ')))
        localProfit = [0] * 20
        connectionProfit = [0] * 20
        for road in rsu2Road[rsuPos]:
            if sum(list(serviceRoad[road]['poi'].values())) == 0:
                possibleEntertain = 0.25
                possibleTrans = 0.25
                possibleWork = 0.25
                possibleLiving = 0.25
            else:
                possibleEntertain = serviceRoad[road]['poi']['entertainment'] / sum(list(serviceRoad[road]['poi'].values()))
                possibleTrans = serviceRoad[road]['poi']['transportation'] / sum(list(serviceRoad[road]['poi'].values()))
                possibleWork = serviceRoad[road]['poi']['workstation'] / sum(list(serviceRoad[road]['poi'].values()))
                possibleLiving = serviceRoad[road]['poi']['livingArea'] / sum(list(serviceRoad[road]['poi'].values()))
            edge = net.getEdge(road)
            shape = edge.getShape()
            shape[0] = list(shape[0])
            shape[1] = list(shape[1])
            shape[0][1] = boundary[3] - shape[0][1]
            shape[1][1] = boundary[3] - shape[1][1]
            distance = calDistance(rsuPosList, shape[0], shape[1])
            bitrate = min(5 * math.log2(1 + 2500 / distance), maxRate)
            for i in range(len(tasksEntertain)):
                localProfit[i] += possibleEntertain * bitrate / tasksEntertain[i]['mem']
                if road in roadConnection.keys():
                    for road2 in roadConnection[road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleEntertain2 = 0.25
                        else:
                            possibleEntertain2 = serviceRoad[road2.replace('-', '')]['poi']['entertainment'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection[road][road2] / sum(list(roadConnection[road].values()))
                        connectionProfit[i] += possibleConnection * possibleEntertain2 * bitrate / tasksEntertain[i]['mem']
                if '-' + road in roadConnection.keys():
                    for road2 in roadConnection['-' + road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleEntertain2 = 0.25
                        else:
                            possibleEntertain2 = serviceRoad[road2.replace('-', '')]['poi']['entertainment'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection['-' + road][road2] / sum(list(roadConnection['-' + road].values()))
                        connectionProfit[i] += possibleConnection * possibleEntertain2 * bitrate / tasksEntertain[i]['mem']
            for i in range(len(tasksTransPort)):
                localProfit[i + 5] += possibleTrans * bitrate / tasksTransPort[i]['mem']
                if road in roadConnection.keys():
                    for road2 in roadConnection[road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleTrans2 = 0.25
                        else:
                            possibleTrans2 = serviceRoad[road2.replace('-', '')]['poi']['transportation'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection[road][road2] / sum(list(roadConnection[road].values()))
                        connectionProfit[i + 5] += possibleConnection * possibleTrans2 * bitrate / tasksTransPort[i]['mem']
                if '-' + road in roadConnection.keys():
                    for road2 in roadConnection['-' + road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleTrans2 = 0.25
                        else:
                            possibleTrans2 = serviceRoad[road2.replace('-', '')]['poi']['transportation'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection['-' + road][road2] / sum(list(roadConnection['-' + road].values()))
                        connectionProfit[i + 5] += possibleConnection * possibleTrans2 * bitrate / tasksTransPort[i]['mem']
            for i in range(len(tasksWork)):
                localProfit[i + 10] += possibleWork * bitrate / tasksWork[i]['mem']
                if road in roadConnection.keys():
                    for road2 in roadConnection[road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleWork2 = 0.25
                        else:
                            possibleWork2 = serviceRoad[road2.replace('-', '')]['poi']['workstation'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection[road][road2] / sum(list(roadConnection[road].values()))
                        connectionProfit[i + 10] += possibleConnection * possibleWork2 * bitrate / tasksWork[i]['mem']
                if '-' + road in roadConnection.keys():
                    for road2 in roadConnection['-' + road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleWork2 = 0.25
                        else:
                            possibleWork2 = serviceRoad[road2.replace('-', '')]['poi']['workstation'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection['-' + road][road2] / sum(list(roadConnection['-' + road].values()))
                        connectionProfit[i + 10] += possibleConnection * possibleWork2 * bitrate / tasksWork[i]['mem']
            for i in range(len(tasksHome)):
                localProfit[i + 15] += possibleLiving * bitrate / tasksHome[i]['mem']
                if road in roadConnection.keys():
                    for road2 in roadConnection[road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleLiving2 = 0.25
                        else:
                            possibleLiving2 = serviceRoad[road2.replace('-', '')]['poi']['livingArea'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection[road][road2] / sum(list(roadConnection[road].values()))
                        connectionProfit[i + 15] += possibleConnection * possibleLiving2 * bitrate / tasksHome[i]['mem']
                if '-' + road in roadConnection.keys():
                    for road2 in roadConnection['-' + road]:
                        if sum(list(serviceRoad[road2.replace('-', '')]['poi'].values())) == 0:
                            possibleLiving2 = 0.25
                        else:
                            possibleLiving2 = serviceRoad[road2.replace('-', '')]['poi']['livingArea'] / sum(list(serviceRoad[road2.replace('-', '')]['poi'].values()))
                        possibleConnection = roadConnection['-' + road][road2] / sum(list(roadConnection['-' + road].values()))
                        connectionProfit[i + 15] += possibleConnection * possibleLiving2 * bitrate / tasksHome[i]['mem']
            try:
                rsuProfit[rsuPos] = [localProfit[i] + connectionProfit[i] + rsuProfit[rsuPos][i] for i in range(20)]
            except:
                rsuProfit[rsuPos] = [localProfit[i] + connectionProfit[i] for i in range(20)]
    for rsuPos, profits in rsuProfit.items():
        resources = copy.deepcopy(RSUProperty[rsuPos])
        tmpDict = []
        for i in range(20):
            tmpDict.append((profits[i], i))
        tmpDict = sorted(tmpDict, key=lambda value: value[0], reverse=True)
        for value in tmpDict:
            if value[1] in range(5):
                if resources['cpu'] >= tasksEntertain[value[1]]['cpu'] and resources['mem'] >= tasksEntertain[value[1]]['mem'] and resources['band'] >= tasksEntertain[value[1]]['band']:
                    resources['cpu'] -= tasksEntertain[value[1]]['cpu']
                    resources['mem'] -= tasksEntertain[value[1]]['mem']
                    resources['band'] -= tasksEntertain[value[1]]['band']
                    try:
                        cacheResult[rsuPos].append('entertainment' + str(value[1]))
                    except:
                        cacheResult[rsuPos] = ['entertainment' + str(value[1])]
            elif value[1] in range(5, 10):
                if resources['cpu'] >= tasksTransPort[value[1] - 5]['cpu'] and resources['mem'] >= tasksTransPort[value[1] - 5]['mem'] and resources['band'] >= tasksTransPort[value[1] - 5]['band']:
                    resources['cpu'] -= tasksTransPort[value[1] - 5]['cpu']
                    resources['mem'] -= tasksTransPort[value[1] - 5]['mem']
                    resources['band'] -= tasksTransPort[value[1] - 5]['band']
                    try:
                        cacheResult[rsuPos].append('transportation' + str(value[1] - 5))
                    except:
                        cacheResult[rsuPos] = ['transportation' + str(value[1] - 5)]
            elif value[1] in range(10, 15):
                if resources['cpu'] >= tasksWork[value[1] - 10]['cpu'] and resources['mem'] >= tasksWork[value[1] - 10]['mem'] and resources['band'] >= tasksWork[value[1] - 10]['band']:
                    resources['cpu'] -= tasksWork[value[1] - 10]['cpu']
                    resources['mem'] -= tasksWork[value[1] - 10]['mem']
                    resources['band'] -= tasksWork[value[1] - 10]['band']
                    try:
                        cacheResult[rsuPos].append('workstation' + str(value[1] - 10))
                    except:
                        cacheResult[rsuPos] = ['workstation' + str(value[1] - 10)]
            elif value[1] in range(15, 20):
                if resources['cpu'] >= tasksHome[value[1] - 15]['cpu'] and resources['mem'] >= tasksHome[value[1] - 15]['mem'] and resources['band'] >= tasksHome[value[1] - 15]['band']:
                    resources['cpu'] -= tasksHome[value[1] - 15]['cpu']
                    resources['mem'] -= tasksHome[value[1] - 15]['mem']
                    resources['band'] -= tasksHome[value[1] - 15]['band']
                    try:
                        cacheResult[rsuPos].append('livingArea' + str(value[1] - 15))
                    except:
                        cacheResult[rsuPos] = ['livingArea' + str(value[1] - 15)]
    print(cacheResult)
    for rsu, caches in cacheResult.items():
        for cache in caches:
            if 'transportation' in cache:
                print(cache)
            if 'workstation' in cache:
                print(cache)
            if 'entertainment' in cache:
                print(cache)
    result = json.dumps(cacheResult, indent='\t')
    with open('cacheResult.json', 'w', newline='\r\n') as file:
        file.write(result)
    
    # for rsu in rsu2Road.keys():
    #     print(rsu)
    #     localProfit = 0
    #     for road in rsu2Road[rsu]:
    #         profit = []
    #         # for task in tasksEntertain:
