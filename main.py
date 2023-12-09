import json
import os
import re
import requests
import urllib3
import shutil
import time
from tkinter import *
import threading

from window import Window

def downloadImages(champ_name, version):

    print(champ_name)
    url = "https://ddragon.leagueoflegends.com/cdn/" + version + "/img/champion/" + champ_name + ".png"
    filename = "D:\Images\\" + champ_name + ".png"

    res = requests.get(url, stream=True)

    if res.status_code == 200:
        with open(filename, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retrieved')

def getChampsIds():
        # Version request
        url = 'https://ddragon.leagueoflegends.com/api/versions.json'
        r = requests.get(url=url)
        version = r.json()

        # Champs ids request
        url = 'https://ddragon.leagueoflegends.com/cdn/' + version[0] + '/data/en_US/champion.json'
        r = requests.get(url=url)
        champs = r.json()

        for champ in champs['data']:
            downloadImages(champ, version[0])


        '''with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(champs, f, ensure_ascii=False, indent=4)'''
if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    window = Window()

