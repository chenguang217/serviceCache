import os
import shutil

if __name__ == "__main__":
    algorithm = 'Genetic1'
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
                if not os.path.exists('sendbackLog/' + des):
                    continue
                with open('sendbackLog/' + des) as file:
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
        

