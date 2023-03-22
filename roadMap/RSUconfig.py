import random
import json

if __name__ == "__main__":
    RSU = {}
    for i in range(9):
        for j in range(7):
            cpuTmp = round(random.uniform(1, 2), 2)
            memTmp = random.randint(160, 200)
            band = 60
            RSU[str([500 + i * 1000, 500 + j * 1000])] = {'cpu': cpuTmp, 'mem': memTmp, 'band': band}
    result = json.dumps(RSU, indent='\t')
    with open('RSUProperty.json', 'w', newline='\r\n') as file:
        file.write(result)
