import sumolib
import json
import numpy as np

poiDistance = 1000
entertainment = ['糕饼店', '餐饮相关场所', '共享设备', '快餐厅', '中餐厅', '摄影冲印店', '外国餐厅', '咖啡厅', '茶艺馆', '冷饮店', '家电电子卖场', '彩票彩券销售点', '甜品店', '专卖店', '购物相关场所', '娱乐场所', '售票处']
transportation = ['丧葬设施', '维修站点', '普通地名', '物流速递', '家居建材市场']
workstation = ['中介机构', '楼宇', '产业园区', '人才市场', '政府及社会团体相关', '电讯营业厅', '旅行社', '邮局', '社会团体', '公司企业', '自来水营业厅']
livingArea = ['住宅区', '洗浴推拿场所', '洗衣店', '生活服务场所', '婴儿服务场所', '美容美发店', '旅馆招待所', '商务住宅相关']

def calDistance(point, line_point1, line_point2):
    #对于两点坐标为同一点时,返回点与点的距离
    if line_point1 == line_point2:
        point_array = np.array(point )
        point1_array = np.array(line_point1)
        return np.linalg.norm(point_array -point1_array )
    #计算直线的三个参数
    A = line_point2[1] - line_point1[1]
    B = line_point1[0] - line_point2[0]
    C = (line_point1[1] - line_point2[1]) * line_point1[0] + \
        (line_point2[0] - line_point1[0]) * line_point1[1]
    #根据点到直线的距离公式计算距离
    distance = np.abs(A * point[0] + B * point[1] + C) / (np.sqrt(A**2 + B**2))
    return distance

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
    # print(result)
    for k, v in result.items():
        print(len(v['poi']))
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
