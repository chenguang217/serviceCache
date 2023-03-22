import json
import math
import os
import shutil

import sumolib
import xmltodict

maxRate = 60
algorithm = 'Genetic1'

def calDistance(node1, node2):
    return math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)

def calQoS(src, dest):
    serviceDist = calDistance(src, dest)
    # print(serviceDist)
    return (5 * math.log2(1 + 2500 / serviceDist)) / maxRate

def qosEvaluation(algorithm):
    net = sumolib.net.readNet('erlangen.net.xml')
    boundaries = net.getBoundary()
    routes = xmltodict.parse(open('erlangen.rou.xml').read())
    vehicles = {}
    result = {}
    taskDes = {}
    for route in routes['routes']['vehicle']:
        vehicles[route['@id']] = route['route']['@edges'].split(' ')
    taskSet = set()
    receiveNotComplete = set()
    files = os.listdir(os.path.join(algorithm, 'finalTaskLog'))
    for name in files:
        if os.path.exists(os.path.join(algorithm, 'finalTaskLog', name.replace('.json', '').split('_')[0] + '.json')):
            with open(os.path.join(algorithm, 'finalTaskLog', name.replace('.json', '').split('_')[0] + '.json'), 'r') as file:
                if file.read().strip() == 'success':
                    taskSet.add(name.replace('.json', '').split('_')[0])
        else:
            receiveNotComplete.add(name.replace('.json', '').split('_')[0])    
    decisions = os.listdir(os.path.join(algorithm, 'decision'))
    for name in decisions:
        with open(os.path.join(algorithm, 'decision', name), 'r') as file:
            tmp = file.readline()
            if tmp == '1':
                # print(name)
                continue
            tmp = file.readline().strip()[:-1].split('|')
            taskDes[name] = []
            for part in tmp:
                try:
                    taskDes[name].append([part.split('*')[0], float(part.split('*')[1])])
                except:
                    taskDes[name].append([part.split('*')[0], 1])
    # handle receive complete task
    for task in taskSet:
        for name in [name for name in files if task in name]:
            if '_' in name:
                taskLog = json.load(open(os.path.join(algorithm, 'finalTaskLog', name)))
                position = [float(taskLog['position'][1:-1].split(',')[0]), float(taskLog['position'][1:-1].split(',')[1])]
                servicePos = [float(taskLog['servicePos'][1:-1].split(',')[0]), float(taskLog['servicePos'][1:-1].split(',')[1])]
                if taskLog['serviceMode'] == '0':
                    minEdge = ['0', 50]
                    edges = net.getNeighboringEdges(position[0] + boundaries[0], boundaries[3] - position[1], 50)
                    for edge in edges:
                        if edge[0].getID() in vehicles[task[:-5]] and edge[1] < minEdge[1]:
                            minEdge = [edge[0].getID(), edge[1]]
                    shapes = net.getEdge(minEdge[0]).getShape()
                    tmpSum = 0
                    for point in shapes:
                        tmpSum += calQoS([point[0] + boundaries[0], boundaries[3] - point[1]], servicePos)
                    qos = tmpSum / len(shapes)
                    try:
                        result[task] += qos * float(taskLog['ratio'])
                    except:
                        result[task] = qos * float(taskLog['ratio'])
                elif '2+' in taskLog['serviceMode']:
                    minEdge = ['0', 50]
                    edges = net.getNeighboringEdges(position[0] + boundaries[0], boundaries[3] - position[1], 50)
                    for edge in edges:
                        if edge[0].getID() in vehicles[task[:-5]] and edge[1] < minEdge[1]:
                            minEdge = [edge[0].getID(), edge[1]]
                    shapes = net.getEdge(minEdge[0]).getShape()
                    tmpNodeList = []
                    tmpLength = 0
                    tmpSum = 0
                    for i in range(len(shapes) - 1):
                        if calDistance(shapes[i], shapes[i + 1]) + tmpLength <= float(taskLog['serviceMode'][2:]):
                            tmpLength += calDistance(shapes[i], shapes[i + 1])
                            tmpNodeList.append(shapes[i])
                            tmpNodeList.append(shapes[i + 1])
                        else:
                            tmpNodeList.append(shapes[i])
                            tmpRatio = (float(taskLog['serviceMode'][2:]) - tmpLength) / calDistance(shapes[i], shapes[i + 1])
                            tmpNodeList.append([shapes[i][0] + tmpRatio * (shapes[i + 1][0] - shapes[i][0]), shapes[i][1] + tmpRatio * (shapes[i + 1][1] - shapes[i][1])])
                            tmpLength = float(taskLog['serviceMode'][2:])
                        if tmpLength == float(taskLog['serviceMode'][2:]):
                            break
                    if tmpLength < float(taskLog['serviceMode'][2:]):
                        for i in range(vehicles[task[:-5]].index(minEdge[0]) + 1, len(vehicles[task[:-5]])):
                            shapes = net.getEdge(vehicles[task[:-5]][i]).getShape()
                            for i in range(len(shapes) - 1):
                                if calDistance(shapes[i], shapes[i + 1]) + tmpLength <= float(taskLog['serviceMode'][2:]):
                                    tmpLength += calDistance(shapes[i], shapes[i + 1])
                                    tmpNodeList.append(shapes[i])
                                    tmpNodeList.append(shapes[i + 1])
                                else:
                                    tmpNodeList.append(shapes[i])
                                    tmpRatio = (float(taskLog['serviceMode'][2:]) - tmpLength) / calDistance(shapes[i], shapes[i + 1])
                                    tmpNodeList.append([shapes[i][0] + tmpRatio * (shapes[i + 1][0] - shapes[i][0]), shapes[i][1] + tmpRatio * (shapes[i + 1][1] - shapes[i][1])])
                                    tmpLength = float(taskLog['serviceMode'][2:])
                                if tmpLength == float(taskLog['serviceMode'][2:]):
                                    break
                            if tmpLength == float(taskLog['serviceMode'][2:]):
                                break
                    for point in tmpNodeList:
                        tmpSum += calQoS([point[0] + boundaries[0], boundaries[3] - point[1]], servicePos)
                    qos = tmpSum / len(tmpNodeList)
                    try:
                        result[task] += qos * float(taskLog['ratio'])
                    except:
                        result[task] = qos * float(taskLog['ratio'])
    # handle not receive complete tasks
    for task in receiveNotComplete:
        tmpRatioSum = 1
        tmpQos = 0
        tmpReceived = {}
        for name in [name for name in files if task in name]:
            taskLog = json.load(open(os.path.join(algorithm, 'finalTaskLog', name)))
            tmpRatioSum -= float(taskLog['ratio'])
            try:
                tmpReceived[taskLog['servicePos']].append(float(taskLog['ratio']))
            except:
                tmpReceived[taskLog['servicePos']] = [float(taskLog['ratio'])]
            position = [float(taskLog['position'][1:-1].split(',')[0]), float(taskLog['position'][1:-1].split(',')[1])]
            servicePos = [float(taskLog['servicePos'][1:-1].split(',')[0]), float(taskLog['servicePos'][1:-1].split(',')[1])]
            if taskLog['serviceMode'] == '0':
                minEdge = ['0', 50]
                edges = net.getNeighboringEdges(position[0] + boundaries[0], boundaries[3] - position[1], 50)
                for edge in edges:
                    if edge[0].getID() in vehicles[task[:-5]] and edge[1] < minEdge[1]:
                        minEdge = [edge[0].getID(), edge[1]]
                shapes = net.getEdge(minEdge[0]).getShape()
                tmpSum = 0
                for point in shapes:
                    tmpSum += calQoS([point[0] + boundaries[0], boundaries[3] - point[1]], servicePos)
                tmpQos += tmpSum / len(shapes) * float(taskLog['ratio'])
            elif '2+' in taskLog['serviceMode']:
                minEdge = ['0', 50]
                edges = net.getNeighboringEdges(position[0] + boundaries[0], boundaries[3] - position[1], 50)
                for edge in edges:
                    if edge[0].getID() in vehicles[task[:-5]] and edge[1] < minEdge[1]:
                        minEdge = [edge[0].getID(), edge[1]]
                shapes = net.getEdge(minEdge[0]).getShape()
                tmpNodeList = []
                tmpLength = 0
                tmpSum = 0
                for i in range(len(shapes) - 1):
                    if calDistance(shapes[i], shapes[i + 1]) + tmpLength <= float(taskLog['serviceMode'][2:]):
                        tmpLength += calDistance(shapes[i], shapes[i + 1])
                        tmpNodeList.append(shapes[i])
                        tmpNodeList.append(shapes[i + 1])
                    else:
                        tmpNodeList.append(shapes[i])
                        tmpRatio = (float(taskLog['serviceMode'][2:]) - tmpLength) / calDistance(shapes[i], shapes[i + 1])
                        tmpNodeList.append([shapes[i][0] + tmpRatio * (shapes[i + 1][0] - shapes[i][0]), shapes[i][1] + tmpRatio * (shapes[i + 1][1] - shapes[i][1])])
                        tmpLength = float(taskLog['serviceMode'][2:])
                    if tmpLength == float(taskLog['serviceMode'][2:]):
                        break
                if tmpLength < float(taskLog['serviceMode'][2:]):
                    for i in range(vehicles[task[:-5]].index(minEdge[0]) + 1, len(vehicles[task[:-5]])):
                        shapes = net.getEdge(vehicles[task[:-5]][i]).getShape()
                        for i in range(len(shapes) - 1):
                            if calDistance(shapes[i], shapes[i + 1]) + tmpLength <= float(taskLog['serviceMode'][2:]):
                                tmpLength += calDistance(shapes[i], shapes[i + 1])
                                tmpNodeList.append(shapes[i])
                                tmpNodeList.append(shapes[i + 1])
                            else:
                                tmpNodeList.append(shapes[i])
                                tmpRatio = (float(taskLog['serviceMode'][2:]) - tmpLength) / calDistance(shapes[i], shapes[i + 1])
                                tmpNodeList.append([shapes[i][0] + tmpRatio * (shapes[i + 1][0] - shapes[i][0]), shapes[i][1] + tmpRatio * (shapes[i + 1][1] - shapes[i][1])])
                                tmpLength = float(taskLog['serviceMode'][2:])
                            if tmpLength == float(taskLog['serviceMode'][2:]):
                                break
                        if tmpLength == float(taskLog['serviceMode'][2:]):
                            break
                for point in tmpNodeList:
                    tmpSum += calQoS([point[0] + boundaries[0], boundaries[3] - point[1]], servicePos)
                tmpQos += tmpSum / len(tmpNodeList) * float(taskLog['ratio'])
        # print(result, round(tmpRatioSum, 2), tmpReceived)
        # print(tmpReceived['(2500,4500,3)'])
        for part in taskDes[task]:
            if part[0].split(';')[0] not in tmpReceived.keys():
                # print(tmpRatioSum)
                tmpRatioSum -= part[1]
                servicePos = part[0].split(';')[0]
                servicePos = [float(servicePos[1:-1].split(',')[0]), float(servicePos[1:-1].split(',')[1])]
                with open(os.path.join(algorithm, 'sendbackLog', part[0]), 'r') as file:
                    while True:
                        line = file.readline().strip()
                        if len(line) == 0:
                            break
                        tmp = line.split(',')
                        if tmp[0] == task:
                            shapes = net.getEdge(tmp[-1]).getShape()
                            tmpSum = 0
                            for point in shapes:
                                tmpSum += calQoS([point[0] + boundaries[0], boundaries[3] - point[1]], servicePos)
                            tmpQos += tmpSum / len(shapes) * part[1]
                            break
                continue
            if len(tmpReceived[part[0].split(';')[0]]) == 4:
                continue
            # print(tmpReceived[part[0].split(';')[0]], part[1])
            if part[1] in tmpReceived[part[0].split(';')[0]]:
                tmpIndex = tmpReceived[part[0].split(';')[0]].index(part[1])
                tmpReceived[part[0].split(';')[0]] = tmpReceived[part[0].split(';')[0]][:tmpIndex] + tmpReceived[part[0].split(';')[0]][tmpIndex + 1:]
            else:
                tmpRatioSum -= part[1]
                servicePos = part[0].split(';')[0]
                servicePos = [float(servicePos[1:-1].split(',')[0]), float(servicePos[1:-1].split(',')[1])]
                with open(os.path.join(algorithm, 'sendbackLog', part[0]), 'r') as file:
                    while True:
                        line = file.readline().strip()
                        if len(line) == 0:
                            break
                        tmp = line.split(',')
                        if tmp[0] == task:
                            shapes = net.getEdge(tmp[-1]).getShape()
                            tmpSum = 0
                            for point in shapes:
                                tmpSum += calQoS([point[0] + boundaries[0], boundaries[3] - point[1]], servicePos)
                            tmpQos += tmpSum / len(shapes) * part[1]
                            break
        if round(tmpRatioSum, 2) == 0:
            result[task] = tmpQos
        else:
            print('task ' + task + ' is not finished')
    result = json.dumps(result, indent='\t')
    with open(os.path.join(algorithm, 'qosResult.json'), 'w', newline='\r\n') as file:
        file.write(result)

if __name__ == "__main__":
    if not os.path.exists(os.path.join(algorithm, 'finalTaskLog')):
        os.makedirs(os.path.join(algorithm, 'finalTaskLog'))
    sendbackFailed = []
    with open(os.path.join(algorithm, 'rsus.csv'), 'r') as file:
        while True:
            line = file.readline().strip()
            if len(line) == 0:
                break
            tmp = line.split(' ')
            for i in range(4):
                if tmp[i + 1] == '*':
                    continue
                tmpTask = tmp[i + 1].split(';')
                for task in tmpTask:
                    if task.split('(')[0] not in sendbackFailed:
                        sendbackFailed.append(task.split('(')[0])
    generateTaskSet = os.listdir(os.path.join(algorithm, 'decision'))
    received = os.listdir(os.path.join(algorithm, 'taskLog'))
    taskSet = []
    successReceive = []
    successSendback = []
    failDrop = []
    deadlineViolation = []
    unknown = []
    for task in generateTaskSet:
        with open(os.path.join(algorithm, 'decision', task), 'r') as file:
            tmp = file.readline()
            if tmp != '1':
                taskSet.append(task)
            else:
                failDrop.append(task)
    for task in taskSet:
        if os.path.exists(os.path.join(algorithm, 'taskLog', task + '.json')):
            with open(os.path.join(algorithm, 'taskLog', task + '.json'), 'r') as file:
                if file.read() == 'failed':
                    deadlineViolation.append(task)
                else:
                    successReceive.append(task)
                    successSendback.append(task)
        else:
            with open(os.path.join(algorithm, 'decision', task), 'r') as file:
                file.readline()
                taskDes = file.readline().strip()
                # print(taskDes)
                taskDes = [des.split('*')[0] for des in taskDes.split('|')[:-1]]
            tmpRatio = 0
            for des in taskDes:
                if not os.path.exists(os.path.join(algorithm, 'sendbackLog', des)):
                    continue
                with open(os.path.join(algorithm, 'sendbackLog', des)) as file:
                    while True:
                        line = file.readline().strip()
                        if len(line) == 0:
                            break
                        if line == task + ' time out, drop task.':
                            # print(task + 'operate time out')
                            if task not in failDrop:
                                failDrop.append(task)
                            break
                        tmp = line.split(',')
                        if tmp[0] == task:
                            # print(tmp)
                            tmpRatio += float(tmp[1])
            if tmpRatio == 1:
                successSendback.append(task)
                # print(successReceive, failDrop, successSendback)
            elif task not in failDrop:
                unknown.append(task)
                # if tmpRatio != 0:
                #     print(task)
                # print(task, taskDes)
                # exit()
    # print(unknown)
    with open(os.path.join(algorithm, 'successRate.txt'), 'w') as file:
        file.write(str([len(unknown), len(failDrop), len(successReceive), len(successSendback), len(deadlineViolation), len(sendbackFailed)]))
    print(len(unknown), len(failDrop), len(successReceive), len(successSendback), len(deadlineViolation), len(sendbackFailed))
    for task in successSendback:
        for name in received:
            if task in name:
                shutil.copyfile(os.path.join(algorithm, 'taskLog', name), os.path.join(algorithm, 'finalTaskLog', name))
    qosEvaluation(algorithm)