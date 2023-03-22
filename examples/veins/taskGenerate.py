import collections
import copy
import json
import math
import mmap
import os
import random
import sys
import time
from turtle import pos

import numpy as np
import sumolib
from PythonParam import PythonParam


if __name__ == "__main__":
    net = sumolib.net.readNet('erlangen.net.xml')
    with open('poiResult.json', 'r') as fout:
        data = json.load(fout)
        print(data['64'])
        poi_information = data['64']
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

    # print([tasktype, subtasktype, cpu, mem])


