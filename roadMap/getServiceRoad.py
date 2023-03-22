import sumolib
import json
import numpy as np

poiDistance = 500
entertainment = ['糕饼店', '餐饮相关场所', '共享设备', '快餐厅', '中餐厅', '摄影冲印店', '外国餐厅', '咖啡厅', '茶艺馆', '冷饮店', '甜品店', '专卖店', '购物相关场所', '娱乐场所']
transportation = ['丧葬设施', '维修站点', '普通地名', '物流速递', '家居建材市场', '售票处', '家电电子卖场', '彩票彩券销售点']
workstation = ['中介机构', '楼宇', '产业园区', '人才市场', '政府及社会团体相关', '电讯营业厅', '旅行社', '邮局', '社会团体', '公司企业', '自来水营业厅']
livingArea = ['住宅区', '洗浴推拿场所', '洗衣店', '生活服务场所', '婴儿服务场所', '美容美发店', '旅馆招待所', '商务住宅相关']

def getFootPoint(point, line_p1, line_p2):
    x0 = point[0]
    y0 = point[1]

    x1 = line_p1[0]
    y1 = line_p1[1]

    x2 = line_p2[0]
    y2 = line_p2[1]

    k = -((x1 - x0) * (x2 - x1) + (y1 - y0) * (y2 - y1)) / \
           ((x2 - x1) ** 2 + (y2 - y1) ** 2) * 1.0
    xn = k * (x2 - x1) + x1
    yn = k * (y2 - y1) + y1

    return (xn, yn)

def calDistance(point, line_point1, line_point2):
    footP = getFootPoint(point, line_point1, line_point2)
    #对于两点坐标为同一点时,返回点与点的距离
    if line_point1 == line_point2:
        point_array = np.array(point )
        point1_array = np.array(line_point1)
        return np.linalg.norm(point_array -point1_array )
    #计算直线的三个参数
    if ((footP[0] - line_point1[0]) > 0) ^ ((footP[0] - line_point2[0]) > 0):
        dist = np.linalg.norm((footP[0] - point[0], footP[1] - point[1]))
    else:
        dist = min(np.linalg.norm((line_point1[0] - point[0], line_point1[1] - point[1])), 
            np.linalg.norm((line_point2[0] - point[0], line_point2[1] - point[1])))
    #根据点到直线的距离公式计算距离
    return dist

if __name__ == "__main__":
    RSUPos = []
    poiList = []
    poiResult = {}
    road2RSU = {}
    result = {}
    net = sumolib.net.readNet('erlangen.net.xml')
    boundary = net.getBoundary()
    for i in range(9):
        for j in range(7):
            RSUPos.append([500 + i * 1000, 500 + j * 1000])
    with open('currentResult.json', 'r', encoding='utf-8') as file:
        poiRaw = json.loads(file.read())
    for pos, detail in poiRaw.items():
        location = net.convertLonLat2XY(float(pos.split(',')[0]), float(pos.split(',')[1]))
        if '|' in detail:
            if detail.split('|')[1].split(';')[1] in entertainment:
                poiList.append([location, 'entertainment'])
            elif detail.split('|')[1].split(';')[1] in transportation:
                poiList.append([location, 'transportation'])
            elif detail.split('|')[1].split(';')[1] in workstation:
                poiList.append([location, 'workstation'])
            elif detail.split('|')[1].split(';')[1] in livingArea:
                poiList.append([location, 'livingArea'])
        else:
            if detail.split(';')[1] in entertainment:
                poiList.append([location, 'entertainment'])
            elif detail.split(';')[1] in transportation:
                poiList.append([location, 'transportation'])
            elif detail.split(';')[1] in workstation:
                poiList.append([location, 'workstation'])
            elif detail.split(';')[1] in livingArea:
                poiList.append([location, 'livingArea'])
    for edge in net.getEdges():
        if '-' not in edge.getID():
            shape = edge.getShape()
            shape[0] = list(shape[0])
            shape[1] = list(shape[1])
            shape[0][1] = boundary[3] - shape[0][1]
            shape[1][1] = boundary[3] - shape[1][1]
            minDis = 1000000
            closeRSU = [0, 0]
            for rsu in RSUPos:
                tmp = calDistance(rsu, shape[0], shape[1])
                if tmp < minDis:
                    closeRSU = rsu
                    minDis = tmp
            result[edge.getID()] = {'RSU': str(closeRSU)}
            for poi in poiList:
                tmp = calDistance(poi[0], shape[0], shape[1])
                # print(tmp)
                if tmp <= poiDistance:
                    try:
                        result[edge.getID()]['poi'][poi[1]] += 1
                        # poiResult[edge.getID()][poi[1]] += 1
                    except:
                        try:
                            result[edge.getID()]['poi'][poi[1]] = 1
                        except:
                            try:
                                result[edge.getID()]['poi'] = {poi[1]: 1}
                            except:
                                result[edge.getID()] = {'poi': {poi[1]: 1}}
                        # poiResult[edge.getID()] = {poi[1]: 1}
    for rsu, property in result.items():
        if 'poi' not in property.keys():
            property['poi'] = {'entertainment': 0, 'livingArea': 0, 'transportation': 0, 'workstation': 0}
        if 'entertainment' not in property['poi'].keys():
            property['poi']['entertainment'] = 0
        if 'livingArea' not in property['poi'].keys():
            property['poi']['livingArea'] = 0
        if 'transportation' not in property['poi'].keys():
            property['poi']['transportation'] = 0
        if 'workstation' not in property['poi'].keys():
            property['poi']['workstation'] = 0
    result = json.dumps(result, indent='\t')
    with open('serviceRoad.json', 'w', newline='\r\n') as file:
        file.write(result)
    # for k, v in result.items():
    #     print(len(v['poi']))
        # if detail.split(';')[1] not in poiType:
        #     poiType.append(detail.split(';')[1])
        # try:
        #     if detail.split('|')[1].split(';')[1] not in poiType:
        #         poiType.append(detail.split('|')[1].split(';')[1])
        #         print(detail.split('|'))
        # except:
        #     pass
        # if detail.split(';')[1] == '社会团体':
        #     print(detail)
