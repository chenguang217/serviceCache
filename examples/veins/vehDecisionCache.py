import json
import math
import mmap
import os
import random
import sys
from turtle import pos
from PythonParam import PythonParam


import sumolib

size = (2600, 3000)

theoryCPUMax = 2
theoryCPUMin = 1

#写入一次
def send(s, file_name):
    s=s+100*' '
    infosize=len(s)+1
    byte=s.encode(encoding='UTF-8')
    #从头读取内存，不然的话会接着上次的内存位置继续写下去，这里是从头覆盖。
    shmem=mmap.mmap(0,1000,file_name,mmap.ACCESS_WRITE)
    shmem.write(byte)

def recieve(file_name):
    shmem=mmap.mmap(0,100,file_name,mmap.ACCESS_READ)
    s=str(shmem.read(shmem.size()).decode("utf-8"))
    #vs2012早期版本会有截断符和开始符号，需要提取有用字符串
    es='\\x00'#字符条件截断，还没有设计开始endstring
    if s.find(es)==-1:
        print(s)
    else:
        sn=s[:s.index(ss)]
        print(sn)

def calETA(net, begin, target, externalID):
    fromLon, fromLat = net.convertXY2LonLat(begin[0], begin[1])
    toLon, toLat = net.convertXY2LonLat(target[0], target[1])
    # 通过经纬度计算ETA, 待获取数据并计算结果
    return random.randint(0, 30)

def relay(position, target):
    relay0 = []
    for i in range(round(size[0] / 1000)):
        for j in range(round(size[1] / 1000)):
            distance = math.sqrt((position[0] - i * 1000 - 500) ** 2 + (position[1] - j * 1000 - 500) ** 2)
            if distance <= 1000:
                relay0.append([i * 1000 + 500, j * 1000 + 500])
    minJump = 16000
    for point in relay0:
        if target[0] - point[0] + point[1] - point[1] < minJump:
            minJump = target[0] - point[0] + point[1] - point[1]
            relayStart = point
    xlength = relayStart[0] - target[0]
    ylength = relayStart[1] - target[1]
    # print(xlength, ylength)
    finalRelay = [relayStart]
    for i in range(abs(int(xlength / 1000))):
        finalRelay.append([finalRelay[-1][0] + 1000, finalRelay[-1][1]])
    for i in range(abs(int(ylength / 1000))):
        finalRelay.append([finalRelay[-1][0], finalRelay[-1][1] + 1000])
    return finalRelay

def baseLine_ShortestFirst(position):
    minimum = 10000
    rsuTarget = ''
    for rsu in RSUs:
        rsuX = float(rsu['rsuLocation'][1:-1].split(',')[0])
        rsuY = float(rsu['rsuLocation'][1:-1].split(',')[1])
        X = position[0]
        Y = position[1]
        distance = math.sqrt((rsuX - X) ** 2 + (rsuY - Y) ** 2)
        if minimum > distance:
            minimum = distance
            rsuTarget = rsu['rsuId']
    decision = ''
    for rsu in RSUs:
        decision += rsu['rsuId'] + '|' + rsu['rsuLocation'] + ':'
        if rsu['rsuId'] == rsuTarget:
            decision += 'true;'
        else:
            decision += 'false;'
    return decision

def vehDecision(param: PythonParam):
    try:
        externalID = param.getString("externalID")
        road = param.getString("road")
        position = param.getString("position")
        # cpuRequirement = param.getDouble("cpuRequirement")
        res = PythonParam()

        net = sumolib.net.readNet('erlangen.net.xml')
        begin = net.getEdge(road).getToNode().getCoord()
        roads = []
        if not os.path.exists('eta/' + externalID + '.csv'):
            print('no eta')
            res.set("name", "1")
            return res
        with open('eta/' + externalID + '.csv', 'r') as file:
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                roads.append(line.split(',')[0].strip())
        try:
            deadLinePosition = random.choice(roads[roads.index(road) + 3:])
            res.set("name", externalID + ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',5)))
        except:
            print('too short route')
            res.set("name", "1")
            return res

        if deadLinePosition[0] == '-':
            deadLinePosition = deadLinePosition[1:]

        with open('deadroad.txt', 'a') as ft:
            ft.write(deadLinePosition)
            ft.write('\n')
        ft.close

        with open('poiResult.json', 'r') as fout:
            data = json.load(fout)
            # print(data['0'])
            poi_information = data[deadLinePosition]
        fout.close()

        entertainment = poi_information['poi']['entertainment']
        livingArea = poi_information['poi']['livingArea']
        transportation = poi_information['poi']['transportation']
        workstation = poi_information['poi']['workstation']

        sum_weight = entertainment + livingArea + transportation + workstation
        s_weight = [entertainment, livingArea, transportation, workstation]
        print(s_weight)

        mid_weight = random.random() * sum_weight
        temp_weight = 0
        count = 0
        tasktype = 0
        subtasktype = 0
        cpu = 0
        mem = 0

        for i in s_weight:
            count += 1
            temp_weight += i
            if temp_weight >= mid_weight:
                break

        if count == 1:
            tasktype = 1
            subtasktype = random.randint(1, 5)
            if subtasktype == 1:
                cpu = 0.1
                mem = 40960
            elif subtasktype == 2:
                cpu = 0.08
                mem = 46080
            elif subtasktype == 3:
                cpu = 0.12
                mem = 37888
            elif subtasktype == 4:
                cpu = 0.1
                mem = 35840
            elif subtasktype == 5:
                cpu = 0.13
                mem = 44032

        elif count == 2:
            tasktype = 2
            subtasktype = random.randint(1, 5)
            if subtasktype == 1:
                cpu = 0.1
                mem = 13312
            elif subtasktype == 2:
                cpu = 0.12
                mem = 15360
            elif subtasktype == 3:
                cpu = 0.1
                mem = 14336
            elif subtasktype == 4:
                cpu = 0.08
                mem = 15360
            elif subtasktype == 5:
                cpu = 0.11
                mem = 13312

        elif count == 3:
            tasktype = 3
            subtasktype = random.randint(1, 5)
            if subtasktype == 1:
                cpu = 0.4
                mem = 16384
            elif subtasktype == 2:
                cpu = 0.3
                mem = 14336
            elif subtasktype == 3:
                cpu = 0.5
                mem = 15360
            elif subtasktype == 4:
                cpu = 0.35
                mem = 13312
            elif subtasktype == 5:
                cpu = 0.45
                mem = 14336

        elif count == 4:
            tasktype = 4
            subtasktype = random.randint(1, 5)
            if subtasktype == 1:
                cpu = 0.4
                mem = 46080
            elif subtasktype == 2:
                cpu = 0.35
                mem = 40960
            elif subtasktype == 3:
                cpu = 0.3
                mem = 46080
            elif subtasktype == 4:
                cpu = 0.5
                mem = 35840
            elif subtasktype == 5:
                cpu = 0.45
                mem = 44032

        deadPosition = net.getEdge(deadLinePosition).getFromNode().getCoord()
        boundaries = net.getBoundary()
        deadPosition = [deadPosition[0] - boundaries[0], boundaries[3] - deadPosition[1]]
        # -----------eta calculation-----------

        etaRaw = []
        etaFinal = []
        etaStart = 0
        with open('eta/' + externalID + '.csv', 'r') as file:
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                etaRaw.append(line.strip().split(','))
        flag = False
        for i in range(len(etaRaw)):
            tmpNode = net.getEdge(etaRaw[i][0]).getFromNode().getCoord()
            tmpNode = [tmpNode[0] - boundaries[0], boundaries[3] - tmpNode[1]]
            if etaRaw[i][0] == road:
                etaFinal.append([tmpNode, 0])
                etaStart = float(etaRaw[i][1])
                flag = True
            elif etaRaw[i][0] == deadLinePosition:
                etaFinal.append([tmpNode, float(etaRaw[i][1]) - etaStart])
                break
            elif flag:
                etaFinal.append([tmpNode, float(etaRaw[i][1]) - etaStart])

        # -----------decision process-----------

        position = [float(position.replace('(', '').replace(')', '').split(',')[0]), float(position.replace('(', '').replace(')', '').split(',')[1])]
        theroMinTime = cpu / theoryCPUMax
        for eta in etaFinal:
            if eta[1] > theroMinTime:
                possibleNearest = eta[0]
                break
        else:
            possibleNearest = etaFinal[-1][0]
        theoryMaxTime = cpu / theoryCPUMin
        for eta in etaFinal:
            if eta[1] > theoryMaxTime:
                possibleFarest = eta[0]
                break
        else:
            possibleFarest = etaFinal[-1][0]
        tmpRoads = [[net.getEdge(road).getFromNode().getCoord()[0] - boundaries[0], boundaries[3] - net.getEdge(road).getFromNode().getCoord()[1]] for road in roads]

        # -----------get possible RSU-----------

        with open('node2RSU.json', 'r') as file:
            node2RSU = json.loads(file.read().strip())
        usableRSUs = []
        for tmpPosition in tmpRoads[tmpRoads.index(possibleNearest):tmpRoads.index(deadPosition) + 1]:
            for tmpNode in node2RSU[str(tmpPosition)]:
                if tmpNode not in usableRSUs:
                    usableRSUs.append(tmpNode)
        possibleRSU = ''
        for rsu in usableRSUs:
            possibleRSU +='(' + str(rsu[0]) + ',' + str(rsu[1]) + ',3);'
        # send(externalID + ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',5)), externalID + 'global_share_memory')
        # send(possibleRSU, externalID + 'possibleRSU')
        res.set("deadLinePosX", deadPosition[0])
        res.set("deadLinePosY", deadPosition[1])
        res.set("cpu", cpu)
        res.set("mem", mem)
        res.set("tasktype", tasktype)
        res.set("subtasktype", subtasktype)
        res.set("possibleRSU", str(possibleRSU))
        return res
    except Exception as ex:
        with open('e.txt', 'a') as fout:
            print(str(ex))
            fout.write(str(ex))