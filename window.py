import json
import os
import re
import requests
import urllib3
import time
from tkinter import *
import threading

RELOAD_TIME = 2000


class Window:
    def __init__(self):
        self.root = Tk()  # create a root widget
        self.root.title("Tk Example")
        self.root.minsize(200, 200)  # width, height
        self.root.maxsize(500, 500)
        self.root.geometry("300x300+50+50")  # width x height + x + y

        self.reloadFlag = True

        # create a list box
        langs = ('Java', 'C#', 'C', 'C++', 'Python',
                 'Go', 'JavaScript', 'PHP', 'Swift')

        var = Variable(value=langs)

        self.listbox = Listbox(
            self.root,
            listvariable=var,
            height=6,
            selectmode=EXTENDED
        )

        self.listbox.pack(expand=True, fill=BOTH)

        status = self.reloadList()

        if status == 0:
            self.root.mainloop()


    def __del__(self):
        self.reloadFlag = False

    def reloadList(self):
        lobbydata = self.getData()

        if len(lobbydata) == 0:
            return -1

        champs = []
        for c in lobbydata:
            champs.append(c["id"])

        self.listbox.delete(0, END)
        for champ in champs:
            self.listbox.insert(END, champ)

        self.root.after(RELOAD_TIME, self.reloadList)

        return 0

    def getClientInfo(self):
        query = "wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline"
        result = os.popen(query).read()

        port_match = re.search("--app-port=([0-9]*)", result)
        pwd_match = re.search("--remoting-auth-token=([\w-]*)", result)

        if not port_match or not pwd_match:
            return {"port": None, "pwd": None}

        client_port = port_match.group().split("=")[1]
        client_pwd = pwd_match.group().split("=")[1]

        return {"port": client_port, "pwd": client_pwd}

    def getChampsIds(self):
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

    def executeLobbyRequest(self, client_info):
        # Set up session
        session = requests.session()
        session.verify = False

        res = session.get('https://127.0.0.1:' + client_info["port"] + '/lol-champ-select/v1/session', data={},
                          auth=requests.auth.HTTPBasicAuth('riot', client_info["pwd"]))

        return res.json()

    def parseLobbyData(self, dataMastery, dataLobby):
        bench = {}
        availableChamps = []
        availableData = []
        d = open('data.json')
        dataChamps = json.load(d)

        # Only for development, delete when release
        l = open('lobby.json')
        dataLobby = json.load(l)

        for i in dataLobby['benchChampions']:
            bench[i['championId']] = "bench"

        for i in dataLobby['myTeam']:
            bench[i['championId']] = "teammate"

        for champ in dataMastery:
            if champ['championId'] in bench:
                availableChamps.append(champ)

        for key, value in dataChamps['data'].items():
            if int(value['key']) in bench:
                availableData.append(value)

        availableChamps.sort(key=lambda x: x["championId"])
        availableData.sort(key=lambda x: int(x['key']))

        for i in range(len(availableChamps)):
            availableChamps[i].update(availableData[i])

        return availableChamps

    def executeMasteryRequest(self, client_info):
        # Set up session
        session = requests.session()
        session.verify = False

        res = session.get('https://127.0.0.1:' + client_info["port"] + '/lol-summoner/v1/current-summoner', params={},
                          auth=requests.auth.HTTPBasicAuth('riot', client_info["pwd"]))
        acc_data = res.json()

        res = session.get('https://127.0.0.1:' + client_info["port"] + '/lol-collections/v1/inventories/' + str(
            acc_data["summonerId"]) + '/champion-mastery', params={},
                          auth=requests.auth.HTTPBasicAuth('riot', client_info["pwd"]))
        return res.json()

    def orderLobbyData(self, availableChamps):

        sortorderlevel = {4: 0, 3: 1, 2: 2, 1: 3, 0: 4, 5: 5, 6: 6, 7: 7}
        sortordertoken = {2: 0, 1: 1, 0: 2}

        availableChamps.sort(key=lambda x: (sortorderlevel[x["championLevel"]], sortordertoken[x["tokensEarned"]]))

        return availableChamps

    def getData(self):

        availableChamps = []

        client_info = self.getClientInfo()
        if client_info["port"] == None or client_info["pwd"] == None:
            return availableChamps
        accMasteryData = self.executeMasteryRequest(client_info)
        accLobbyData = []
        # accLobbyData = self.executeLobbyRequest(client_info)
        availableChamps = self.parseLobbyData(accMasteryData, accLobbyData)
        orderedChamps = self.orderLobbyData(availableChamps)

        return availableChamps
