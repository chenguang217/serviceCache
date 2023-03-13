import xmltodict
import json

connectionNum = 5

if __name__ == "__main__":
    roadConnection = {}
    connectionResult = {}
    with open('erlangen.rou.xml', 'r', encoding='utf-8') as file:
        content_dict = xmltodict.parse(file.read())
    for vehicle in content_dict['routes']['vehicle']:
        vehId = vehicle['@id']
        routes = vehicle['route']['@edges'].split(' ')
        for i in range(len(routes) - 1):
            for j in range(i + 1, len(routes)):
                try:
                    roadConnection[routes[i]][routes[j]] += 1
                except:
                    try:
                        roadConnection[routes[i]][routes[j]] = 1
                    except:
                        roadConnection[routes[i]] = {routes[j]: 1}
    for sourceRoad, connections in roadConnection.items():
        for targetRoad, num in connections.items():
            if num >= connectionNum:
                try:
                    connectionResult[sourceRoad][targetRoad] = num
                except:
                    connectionResult[sourceRoad] = {targetRoad: num}
    result = json.dumps(connectionResult, indent='\t')
    with open('roadConnection.json', 'w', newline='\r\n') as file:
        file.write(result)

