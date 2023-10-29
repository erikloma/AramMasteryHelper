import json
import os
import re
import requests
import urllib3

def getClientInfo():
    query = "wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline"
    result = os.popen(query).read()

    port_match = re.search("--app-port=([0-9]*)", result)
    pwd_match = re.search("--remoting-auth-token=([\w-]*)", result)

    client_port = port_match.group().split("=")[1]
    client_pwd = pwd_match.group().split("=")[1]

    return {"port": client_port, "pwd": client_pwd}

def getChampsIds():
    # Version request
    url = 'https://ddragon.leagueoflegends.com/api/versions.json'
    r = requests.get(url=url)
    version = r.json()

    # Champs ids request
    url = 'https://ddragon.leagueoflegends.com/cdn/' + version[0] + '/data/en_US/champion.json'
    r = requests.get(url=url)
    champs = r.json()
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(champs, f, ensure_ascii=False, indent=4)

def executeLobbyRequest(client_info):
    # Set up session
    session = requests.session()
    session.verify = False

    res = session.get('https://127.0.0.1:' + client_info["port"] + '/lol-champ-select/v1/session', data={}, auth=requests.auth.HTTPBasicAuth('riot', client_info["pwd"]))
    print(res.json())
    '''with open('example.json', 'w', encoding='utf-8') as f:
        json.dump(res.json(), f, ensure_ascii=False, indent=4)'''

def parseData():
    bench = []
    f = open('example.json')
    dataLobby = json.load(f)

    b = open('data.json')
    dataChamps = json.load(b)

    for i in dataLobby['benchChampions']:
        bench.append(i['championId'])

    for key, value in dataChamps['data'].items():
        if int(value['key']) in bench:
            print(value['id'])


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #client_info = getClientInfo()
    #executeLobbyRequest(client_info)
    parseData()
