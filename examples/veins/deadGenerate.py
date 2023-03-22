import json
import math
import mmap
import os
import random
import sys
from turtle import pos
from PythonParam import PythonParam


import sumolib


def deadGenerate(param: PythonParam):
    try:
        externalID = param.getString("externalID")
        road = param.getString("road")
        res = PythonParam()

        net = sumolib.net.readNet('erlangen.net.xml')
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

        deadPosition = net.getEdge(deadLinePosition).getFromNode().getCoord()
        boundaries = net.getBoundary()
        deadPosition = [deadPosition[0] - boundaries[0], boundaries[3] - deadPosition[1]]

        res.set("deadRoad", deadLinePosition)
        res.set("deadLinePosX", deadPosition[0])
        res.set("deadLinePosY", deadPosition[1])
        return res
    except Exception as ex:
        with open('re.txt', 'a') as fout:
            print(str(ex))
            fout.write(str(ex))