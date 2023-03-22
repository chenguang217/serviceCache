import json
import os

# 增加一下未生成任务计算，针对Nearest
if __name__ == "__main__":
    algorithm = 'Genetic5'
    with open(os.path.join(algorithm, 'qosResult.json'), 'r') as file:
        qos = json.loads(file.read())
    print(sum(qos.values()) / len(qos))