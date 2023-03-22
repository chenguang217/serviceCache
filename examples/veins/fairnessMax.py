import os
import numpy as np

# 增加一下未生成任务计算，针对Nearest
if __name__ == "__main__":
    algorithm = 'Genetic5'
    rsuWaits = {}
    minSimTime = 400
    rsus = os.listdir(os.path.join(algorithm, 'RSUlog'))
    maxFairness = 0
    for rsu in rsus:
        rsuWaits[rsu] = []
        with open(os.path.join(algorithm, 'RSUlog', rsu), 'r') as file:
            while True:
                line = file.readline()
                if len(line) == 0:
                    break
                waits = [float(t) for t in line.split(';')[1].split(',')[4:8]]
                rsuWaits[rsu].append(waits)
    for k, v in rsuWaits.items():
        if len(v) < minSimTime:
            minSimTime = len(v)
    for i in range(minSimTime):
        tmpWaits = []
        for k in rsuWaits.keys():
            tmpWaits.extend(rsuWaits[k][i])
        # print(np.var(tmpWaits), len(tmpWaits))
        if np.var(tmpWaits) > maxFairness:
            maxFairness = np.var(tmpWaits)
    print(maxFairness)
