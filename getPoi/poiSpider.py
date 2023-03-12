import requests
import json
import time

if __name__ == "__main__":
    lonMin = 114.023002
    latMin = 22.512003
    lonMax = 114.109998
    latMax = 22.574998
    # 1000m网格搜索
    lonGap = 0.0097207301114583
    latGap = 0.0090664635952381
    point = [(lonMin * 2 + lonGap) / 2, (latMin * 2 + latGap) / 2]
    session = requests.session()
    count = 0
    with open('currentCount.txt', 'r') as file:
        currentCount = int(file.read())
    with open('currentResult.json', 'r', encoding='utf-8') as file:
        result = json.loads(file.read().strip())
    while point[0] < lonMax:
        while point[1] < latMax:
            url = 'https://restapi.amap.com/v3/place/around?key=0e4a0ae3dcfd08118860cb2aa7cd7bbb&location=' + str(round(point[0], 6)) + ',' + str(round(point[1], 6)) + '&keywords=&types=&radius=1000&offset=20&page=1&extensions=all'
            if count > currentCount:
                print(count)
                response = session.get(url)
                response.encoding = 'utf-8'
                for poi in response.json()['pois']:
                    if poi['location'] not in result.keys():
                        result[poi['location']] = poi['type']
                with open('currentResult.json', 'w', encoding='utf-8') as file:
                    file.write(json.dumps(result, indent='\t', ensure_ascii=False))
                with open('currentCount.txt', 'w') as file:
                    file.write(str(count))
                time.sleep(1)
            point[1] += latGap
            count += 1
        point[0] += lonGap
        point[1] = (latMin * 2 + latGap) / 2
    print(count)