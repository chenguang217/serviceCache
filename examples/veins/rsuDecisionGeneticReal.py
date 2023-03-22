import collections
import copy
import json
import math
import mmap
import os
import random
import sys
from turtle import pos
from datetime import datetime
from typing import List, Iterable
from operator import itemgetter
from func_timeout import func_set_timeout, exceptions
import time


import pandas as pd
import numpy as np
import sumolib
from PythonParam import PythonParam


size = (2600, 3000)
maxRate = 60
maxTime = 200
start_bestallocation = []
resultserviceRoad = {}


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


def Random_generation(nlength):
    all_list = []
    for i in range(nlength):
        cur = random.randint(0,2)
        all_list.append(cur)
    return all_list


def CalMetric(serviceRate, waits):
    if calVariance(waits) == 0:
        return 0.7 * serviceRate
    else:
        metric = 0.7 * serviceRate + 0.3 * (1 / calVariance(waits))
        return metric


class Gene:
    def __init__(self, **data):
        self.__dict__.update(data)
        self.size = len(data['data'])


class GA:
    def __init__(self, parameter):
        self.parameter = parameter
        self.CXPB = self.parameter[0]
        self.MUTPB = self.parameter[1]
        self.NGEN = self.parameter[2]
        self.popsize = self.parameter[3]
        self.rsuList = self.parameter[4]
        self.cpu = self.parameter[5]
        self.mem = self.parameter[6]
        self.boundaries = self.parameter[7]
        self.serviceRoadList = self.parameter[8]
        self.etaRoad = self.parameter[9]
        self.etaFinal = self.parameter[10]
        self.rsuWaits = self.parameter[11]
        self.proxyPos = self.parameter[12]
        self.transTime = self.parameter[13]
        self.net = self.parameter[14]
        self.maxmem = self.parameter[15]

        pop = []

        count = 0
        nlength = len(self.rsuList)

        while count < self.popsize:
            temp = Random_generation(nlength)
            fitness = self.evaluate(temp)
            pop.append({'Gene': Gene(data=copy.deepcopy(temp)), 'fitness': fitness})
            count += 1
        self.pop = pop
        self.bestindividual = self.selectBest(self.pop)


    def evaluate(self, geneinfo):
        rsunum = len(self.rsuList)
        sumpiece = 0
        relayTime = 0
        allserviceRoad = {}

        for i in range(rsunum):
            sumpiece += geneinfo[i]

        # Judge whether the individual meets the constraints
        if sumpiece == 0:
            allcost = 100
            return 1 / allcost
        for i in range(rsunum):
            curmem = geneinfo[i] / sumpiece
            if self.maxmem[i] < curmem:
                allcost = 100
                return 1 / allcost

        # parse and calculate the fitness
        tmpWait = []
        serviceRate = 0
        for items in self.rsuWaits.values():
            # print("item is " + str(items))
            tmpWait.append(items)

        for i in range(rsunum):
            if geneinfo[i] == 0:
                continue
            rsuPos = list(self.rsuList.keys())[i].replace('(', '').replace(')', '')
            rsuPos = [int(rsuPos.split(',')[0]), int(rsuPos.split(',')[1])]
            cpuTmp = self.rsuList[list(self.rsuList.keys())[i]]['cpu']
            operationTime = self.cpu / (cpuTmp * sumpiece / geneinfo[i]) + self.rsuList[list(self.rsuList.keys())[i]]['wait']
            relays = relay(self.proxyPos, rsuPos)
            for j in range(len(relays) - 1):
                relayTime += self.mem * 8 / 1000 / maxRate
            for eta in range(len(self.etaFinal)):
                if self.etaFinal[eta][1] > operationTime + self.transTime + relayTime:
                    # print("transTime is " + str(transTime))
                    serviceRoad = self.etaRoad[eta - 1][0]
                    break
            else:
                serviceRoad = self.etaRoad[-1][0]
            allserviceRoad[list(self.rsuList.keys())[i]] = (i, serviceRoad)
            tmpWait[int(list(self.rsuWaits.keys()).index(list(self.rsuList.keys())[i]))] += (self.cpu * geneinfo[i]) / (cpuTmp * sumpiece)
        for rsu, property in allserviceRoad.items():
            tmpPos = rsu.replace('(', '').replace(')', '')
            tmpPos = [int(tmpPos.split(',')[0]), int(tmpPos.split(',')[1])]
            serviceRate += calIntegralServiceRate(getRoadLength(property[1], self.net, self.boundaries), tmpPos) * geneinfo[property[0]] / sumpiece
        metric = CalMetric(serviceRate, tmpWait)

        return metric


    def getserviceRoad(self, geneinfo):
        rsunum = len(self.rsuList)
        sumpiece = 0
        relayTime = 0
        allserviceRoad = {}

        for i in range(rsunum):
            sumpiece += geneinfo[i]

        for i in range(rsunum):
            if geneinfo[i] == 0:
                continue
            rsuPos = list(self.rsuList.keys())[i].replace('(', '').replace(')', '')
            rsuPos = [int(rsuPos.split(',')[0]), int(rsuPos.split(',')[1])]
            # print("rsuPos is " + str(rsuPos))
            cpuTmp = self.rsuList[list(self.rsuList.keys())[i]]['cpu']
            operationTime = self.cpu / (cpuTmp * sumpiece / geneinfo[i]) + self.rsuList[list(self.rsuList.keys())[i]]['wait']
            relays = relay(self.proxyPos, rsuPos)
            # print("self.etaFinal is " + str(self.etaFinal))
            for j in range(len(relays) - 1):
                relayTime += self.mem * 8 / 1000 / maxRate
            for eta in range(len(self.etaFinal)):
                if self.etaFinal[eta][1] > operationTime + self.transTime + relayTime:
                    # print("transTime is " + str(transTime))
                    serviceRoad = self.etaRoad[eta - 1][0]
                    break
            else:
                serviceRoad = self.etaRoad[-1][0]
            allserviceRoad[list(self.rsuList.keys())[i]] = (i, serviceRoad)
        # print("allserviceRoad is " + str(allserviceRoad))
        return allserviceRoad


    def selectBest(self, pop):
        s_inds = sorted(pop, key=itemgetter("fitness"), reverse=True)
        return s_inds[0]


    def selection(self, individuals, k):
        # print("k is " + str(k))
        # print("individuals is " + str(len(individuals)))
        s_inds = sorted(individuals, key=itemgetter("fitness"), reverse=True)
        sum_fits = sum(ind['fitness'] for ind in individuals)
        # print("s_inds is " + str(len(s_inds)))
        # print("sum_fits is " + str(sum_fits))

        chosen = []
        for i in range(k):
            u = random.random() * sum_fits
            sum_ = 0
            for ind in s_inds:
                sum_ += ind['fitness']
                if sum_ >= u:
                    chosen.append(ind)
                    break
        chosen = sorted(chosen, key=itemgetter("fitness"), reverse=False)
        # print("chosen is " + str(len(chosen)))
        return chosen


    def crossoperate(self, offspring):
        newoff1 = Gene(data=[])
        newoff2 = Gene(data=[])

        geninfo1 = offspring[0]['Gene'].data
        geninfo2 = offspring[1]['Gene'].data

        nlength = len(geninfo1)

        pos1 = random.randint(0, nlength)
        pos2 = random.randint(0, nlength)

        temp1 = []
        temp2 = []

        # print(geninfo1)
        # print(geninfo2)
        for i in range(nlength):
            if min(pos1, pos2) <= i < max(pos1, pos2):
                temp2.append(geninfo2[i])
                temp1.append(geninfo1[i])
            else:
                temp2.append(geninfo1[i])
                temp1.append(geninfo2[i])

        newoff1.data = temp1
        newoff2.data = temp2
        return newoff1, newoff2


    def mutation(self, crossoff):
        nlength = len(crossoff.data)

        if nlength == 1:
            mutelocation = 0
        else:
            mutelocation = random.randint(0, nlength - 1)
        mute_core = random.randint(0, 2)

        crossoff.data[mutelocation] = mute_core

        return crossoff


    def GA_main(self):
        popsize = self.parameter[3]
        # print(popsize)
        # best_individual = []
        # max_fit = 0
        # print("Start of evolution")
        # Begin the evolution
        for g in range(self.NGEN):
            # print("############### Generation {} ###############".format(g))

            # Apply selection based on their converted fitness
            # elite_individual1 = self.selectBest(self.pop)
            # self.pop.remove(elite_individual1)
            # print(len(self.pop))
            # elite_individual2 = self.selectBest(self.pop)
            # self.pop.remove(elite_individual2)
            selectpop = self.selection(self.pop, popsize)
            # print(len(selectpop))
            # print(len(self.pop))
            nextoff = []
            # nextoff.append(elite_individual1)
            # nextoff.append(elite_individual2)

            while len(nextoff) != popsize:
                # Apply crossover and mutation on the offspring

                # Select two individuals
                # print("selectpop is " + str(len(selectpop)))
                # print("nextoff is " + str(len(nextoff)))
                offspring = [selectpop.pop() for _ in range(2)]
                if random.random() < self.CXPB:  # cross two individuals with probability CXPB
                    crossoff1, crossoff2 = self.crossoperate(offspring)
                    if random.random() < self.MUTPB:  # mutate an individual with probability MUTPB
                        muteoff1 = self.mutation(crossoff1)
                        muteoff2 = self.mutation(crossoff2)
                        fit_muteoff1 = self.evaluate(muteoff1.data)  # Evaluate the individuals
                        fit_muteoff2 = self.evaluate(muteoff2.data)  # Evaluate the individuals
                        nextoff.append({'Gene': muteoff1, 'fitness': fit_muteoff1})
                        nextoff.append({'Gene': muteoff2, 'fitness': fit_muteoff2})
                    else:
                        fit_crossoff1 = self.evaluate(crossoff1.data)  # Evaluate the individuals
                        fit_crossoff2 = self.evaluate(crossoff2.data)  # Evaluate the individuals
                        nextoff.append({'Gene': crossoff1, 'fitness': fit_crossoff1})
                        nextoff.append({'Gene': crossoff2, 'fitness': fit_crossoff2})

                else:
                    nextoff.extend(offspring)

            # The population is entirely replaced by the offspring
            self.pop = nextoff

            # Gather all the fitnesses in one list and print the stats
            fits = [ind['fitness'] for ind in self.pop]

            best_ind = self.selectBest(self.pop)

            if best_ind['fitness'] > self.bestindividual['fitness']:
                self.bestindividual = best_ind

            # print("Best individual found is {}, {}".format(self.bestindividual['Gene'].data,
            #                                            self.bestindividual['fitness']))
            # print("  Max fitness of current pop: {}".format(max(fits)))
            # print("  Min value of aim_func: {}".format(1 / max(fits)))
            # if max_fit < max(fits):
            #     best_individual = self.bestindividual['Gene'].data
        # print("------ End of (successful) evolution ------")
        '''
        with open('best_individual1.txt', 'w') as ft:
            ft.write(str(best_individual))
            ft.close()
        '''
        if self.bestindividual['fitness'] != 0.01:
            tmpserviceRoad = self.getserviceRoad(self.bestindividual['Gene'].data)
            # resultserviceRoad = tmpserviceRoad.copy()
            for key, value in tmpserviceRoad.items():
                resultserviceRoad[key] = value
            # print("resultserviceRoad is " + str(resultserviceRoad))
            for num in self.bestindividual['Gene'].data:
                start_bestallocation.append(num)


def relay(position, target):
    relayStart = position
    xlength = relayStart[0] - target[0]
    ylength = relayStart[1] - target[1]
    finalRelay = [relayStart]
    for i in range(abs(int(xlength / 1000))):
        if xlength > 0:
            finalRelay.append([finalRelay[-1][0] - 1000, finalRelay[-1][1]])
        else:
            finalRelay.append([finalRelay[-1][0] + 1000, finalRelay[-1][1]])
    for i in range(abs(int(ylength / 1000))):
        if ylength > 0:
            finalRelay.append([finalRelay[-1][0], finalRelay[-1][1] - 1000])
        else:
            finalRelay.append([finalRelay[-1][0], finalRelay[-1][1] + 1000])
    # print("the finalRelay is " + str(finalRelay))
    return finalRelay


def calDistance(node1, node2):
    return math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)


def calVariance(data):
    return np.var(data)


def calFairnessGain(rsu, rsuWaits, operationTime, variance):
    tmpWait = []
    for k, v in rsuWaits.items():
        if k == rsu.split(';')[0]:
            tmpWait.append(v + operationTime)
        else:
            tmpWait.append(v)
    tmpVariance = calVariance(tmpWait)
    return 1 / tmpVariance


def calServiceRate(target, rsuPos):
    serviceDist = calDistance(target, rsuPos)
    return (5 * math.log2(1 + 2500 / serviceDist)) / maxRate


def getRoadLength(roadId, net, boundaries):
    road = net.getEdge(roadId)
    shapeNodes = []
    for node in road.getShape():
        shapeNodes.append([node[0] - boundaries[0], boundaries[3] - node[1]])
    return shapeNodes


def calIntegralServiceRate(shapeNodes, rsuPos):
    xSum = 0
    ySum = 0
    for point in shapeNodes:
        xSum += point[0]
        ySum += point[1]
    servicePoint = [xSum / len(shapeNodes), ySum / len(shapeNodes)]
    return calServiceRate(servicePoint, rsuPos)


def rsuDecision(param: PythonParam):
    try:
        rsuInfo = param.getString("rsuInfo")[:-1].split(';')
        vehPos = param.getString("vehPos").replace('(', '').replace(')', '')
        vehPos = [float(vehPos.split(',')[0]), float(vehPos.split(',')[1])]
        deadLinePos = param.getString("deadLinePos").replace('(', '').replace(')', '')
        deadLinePos = [float(deadLinePos.split(',')[0]), float(deadLinePos.split(',')[1])]

        cpu = param.getDouble("cpu")
        mem = param.getDouble("mem")
        externalId = param.getString("externalId")
        roadId = param.getString("roadId")
        proxyPos = param.getString("proxyPos").replace('(', '').replace(')', '')
        proxyPos = [float(proxyPos.split(',')[0]), float(proxyPos.split(',')[1])]
        taskName = param.getString("taskName")
        simTime = param.getDouble("simTime")
        rparam = PythonParam()

        net = sumolib.net.readNet('erlangen.net.xml')
        boundaries = net.getBoundary()

        # -----------rsuInfo parse-----------

        rsuList = {}
        rsuWaits = {}
        with open('rsus.csv', 'r') as file:
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                line = line.strip().split(' ')
                if line[0] in rsuInfo:
                    rsuList[line[0] + ';1'] = {
                        'cpu': float(line[5]),
                        'mem': float(line[6]),
                        'wait': max(0, float(line[10]) - simTime),
                    }
                    rsuList[line[0] + ';2'] = {
                        'cpu': float(line[5]),
                        'mem': float(line[7]),
                        'wait': max(0, float(line[11]) - simTime),
                    }
                    rsuList[line[0] + ';3'] = {
                        'cpu': float(line[5]),
                        'mem': float(line[8]),
                        'wait': max(0, float(line[12]) - simTime),
                    }
                    rsuList[line[0] + ';4'] = {
                        'cpu': float(line[5]),
                        'mem': float(line[9]),
                        'wait': max(0, float(line[13]) - simTime),
                    }
                for i in range(10, len(line)):
                    rsuWaits[line[0] + ';' + str(i - 9)] = (float(line[i]))

        with open('length.txt', 'a') as fout:
            fout.write(str(len(rsuList)))
            fout.write('\n')

        # -----------eta calculation-----------
        etaRoad = []

        etaRaw = []
        etaFinal = []
        etaStart = 0
        with open('eta/' + externalId + '.csv', 'r') as file:
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                etaRaw.append(line.strip().split(','))
        flag = False
        for i in range(len(etaRaw)):
            tmpNode = net.getEdge(etaRaw[i][0]).getFromNode().getCoord()
            tmpNode = [tmpNode[0] - boundaries[0], boundaries[3] - tmpNode[1]]
            if etaRaw[i][0] == roadId:
                etaFinal.append([tmpNode, 0])
                etaRoad.append([etaRaw[i][0], 0])
                etaStart = float(etaRaw[i][1])
                flag = True
            elif abs(tmpNode[0] - deadLinePos[0]) < 0.05 and abs(tmpNode[1] - deadLinePos[1]) < 0.05:
                etaFinal.append([tmpNode, float(etaRaw[i][1]) - etaStart])
                etaRoad.append([etaRaw[i][0], float(etaRaw[i][1]) - etaStart])
                rparam.set("dead", etaRaw[i][0])
                break
            elif flag:
                etaFinal.append([tmpNode, float(etaRaw[i][1]) - etaStart])
                etaRoad.append([etaRaw[i][0], float(etaRaw[i][1]) - etaStart])

        # ---------------get rsu task list----------------

        distance = calDistance(proxyPos, vehPos)
        transRate = min(5 * math.log2(1 + 2500 / distance), maxRate)
        transTime = mem * 8 / 1000 / transRate

        # ----------------decision process----------------
        # -------here is a genetic algorithm-------
        serviceRoadList = {}
        for rsu, property in rsuList.items():
            operationTime = cpu / property['cpu'] + property['wait']
            rsuPos = rsu.replace('(', '').replace(')', '')
            rsuPos = [float(rsuPos.split(',')[0]), float(rsuPos.split(',')[1])]
            core = int(rsu.split(';')[1])
            relays = relay(proxyPos, rsuPos)
            relayTime = 0
            for i in range(len(relays) - 1):
                relayTime += mem * 8 / 1000 / maxRate
            for eta in range(len(etaFinal)):
                if etaFinal[eta][1] > operationTime + transTime + relayTime:
                    # print("transTime is " + str(transTime))
                    target = etaFinal[eta - 1][0]
                    serviceRoad = etaRoad[eta - 1][0]
                    serviceRoadList[rsu] = serviceRoad
                    break
            else:
                target = etaFinal[-1][0]
                serviceRoad = etaRoad[-1][0]
                serviceRoadList[rsu] = serviceRoad
        # print("serviceRoadList is " + str(serviceRoadList))

        maxmem = []
        for rsu, property in rsuList.items():
            maxmem.append(rsuList[rsu]['mem'] / mem)

        CXPB, MUTPB, NGEN, popsize = 0.9, 0.2, 400, 40
        # all_list = num_pieces(allpiece, corenum)
        # print(all_list)
        para1 = [CXPB, MUTPB, NGEN, popsize, rsuList, cpu, mem, boundaries, serviceRoadList, etaRoad, etaFinal,
                 rsuWaits, proxyPos, transTime, net, maxmem]

        if len(rsuList) == 0:
            # print("Genetic algorithm couldn't find any answer!")
            decision = ''
            resultRelay = ''
            serviceRoad = ''
            with open("decision/" + taskName, 'w') as file:
                file.write('1')
            start_bestallocation.clear()
            resultserviceRoad.clear()
            rparam.set("decision", decision[:-1])
            rparam.set("relay", resultRelay[:-1])
            rparam.set("service", serviceRoad[:-1])
            return rparam

        run = GA(para1)
        run.GA_main()

        tmpLines = []
        with open('rsus.csv', 'r') as file:
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                tmp = line.split(' ')
                tmpLines.append(tmp)

        decision = ''
        resultRelay = ''
        serviceRoad = ''

        # print("length of start_bestallocation is " + str(len(start_bestallocation)))
        # print("length of rsuList is " + str(len(rsuList.keys())))

        if len(start_bestallocation) == 0:
            # print("Genetic algorithm couldn't find any answer!")
            decision = ''
            resultRelay = ''
            serviceRoad = ''
            with open("decision/" + taskName, 'w') as file:
                file.write('1')
            start_bestallocation.clear()
            resultserviceRoad.clear()
            rparam.set("decision", decision[:-1])
            rparam.set("relay", resultRelay[:-1])
            rparam.set("service", serviceRoad[:-1])
            return rparam

        tlength = len(start_bestallocation)
        sumpiece1 = 0

        for i in range(tlength):
            sumpiece1 += start_bestallocation[i]

        for k in range(len(start_bestallocation)):
            if start_bestallocation[k] != 0:
                tmpResultRelay = ''
                rsuPos = list(rsuList.keys())[k].replace('(', '').replace(')', '')
                rsuPos = [float(rsuPos.split(',')[0]), float(rsuPos.split(',')[1])]
                midPos = list(rsuList.keys())[k]
                tmpPos = list(rsuList.keys())[k]
                tmpPos = tmpPos.split(';')[0]
                tmpcore = list(rsuList.keys())[k]
                tmpcore = tmpcore.split(';')[1]
                decision += str(list(rsuList.keys())[k]) + '*' + str(start_bestallocation[k] / sumpiece1) + '|'
                tmpRelay = relay(proxyPos, rsuPos)
                for node in tmpRelay:
                    if node != rsuPos and node != proxyPos:
                        tmpResultRelay += '(' + str(int(node[0])) + ',' + str(int(node[1])) + ',3);'
                if len(tmpResultRelay) == 0:
                    tmpResultRelay += 'NULL'
                resultRelay += tmpResultRelay + '|'
                for tmp in tmpLines:
                    if tmp[0] == tmpPos:
                        core = int(tmpcore)
                        tmpRelayTime = len(tmpRelay[1:]) * mem * float(start_bestallocation[k]) * 8 * (1 / sumpiece1) / 1024 / maxRate
                        tmpOperationTime = cpu * (float(start_bestallocation[k]) / sumpiece1) / rsuList[midPos]['cpu']
                        if tmp[core] == '*':
                            tmp[core] = taskName + '(0(' + str(int(transTime + tmpRelayTime + simTime + 7)) + ';'
                        else:
                            tmp[core] += taskName + '(0(' + str(int(transTime + tmpRelayTime + simTime + 7)) + ';'
                        tmp[core + 5] = str(float(tmp[core + 5]) - round(mem * float(start_bestallocation[k]) / sumpiece1, 2))
                        tmp[core + 9] = str(rsuList[midPos]['wait'] + transTime + tmpRelayTime + tmpOperationTime + simTime)
                        if core == 4:
                            tmp[core + 9] += '\n'
                        break

        for key, value in resultserviceRoad.items():
            serviceRoad += value[1] + '|'
        with open('rsus.csv', 'w') as file:
            file.write(''.join([' '.join(tmp) for tmp in tmpLines]))

        with open("decision/" + taskName, 'w') as file:
            file.write(str(proxyPos) + '\n' + decision + '\n' + resultRelay + '\n' + serviceRoad)
        print("decision is " + str(decision))
        print("relay is " + str(resultRelay))
        print("service is " + str(serviceRoad))
        rparam.set("decision", decision[:-1])
        rparam.set("relay", resultRelay[:-1])
        rparam.set("service", serviceRoad[:-1])
        start_bestallocation.clear()
        resultserviceRoad.clear()
        del run
        return rparam
    except Exception as ex:
        with open('tx1.txt', 'a') as fout:
            fout.write(str(ex) + '\n')
        fout.close()