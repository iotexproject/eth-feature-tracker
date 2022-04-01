#!/usr/bin/python3

"""
This script used to  track the latest status of Ethereum: codebase, EIP, release, etc., to help us achieve:
1. Gain more understanding of the Ethereum features
2. Respond quickly on critical bugs/hotfixes
3. Correctly and accurately implement EIP in our Ethereum fork
"""


import urllib.request as urllib2
import re
from bs4 import BeautifulSoup
from random import randint
import random
import time
import pymysql
import requests
import pandas as pd
from sqlalchemy import create_engine


def generate_mysql():
    conn = pymysql.connect(
        host='localhost',  # 本地服务器
        user='eip',
        password='123456',  # 你的数据库密码
        port=3306,  # 默认端口
        charset='utf8',
        db='eipinfos')
    cursor = conn.cursor()

    sql = 'CREATE TABLE IF NOT EXISTS list_eips (ID INT(20) NOT NULL AUTO_INCREMENT ,Number INT(30) NOT NULL,Title VARCHAR(100),Author VARCHAR(300),Release_info VARCHAR(200),Commit_info VARCHAR(200),Iotex_supported VARCHAR(100),PRIMARY KEY (ID))'
    # 	sql = 'CREATE TABLE IF NOT EXISTS list_eips (Number INT(30) NOT NULL,eip_number INT(30) NOT NULL,eip_type VARCHAR(100),title_content VARCHAR(100) ,PRIMARY KEY (serial_number))'
    # listed_company是要在wade数据库中建立的表，用于存放数据

    cursor.execute(sql)
    conn.close()

def write_eip_to_db(url):

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    dfs = pd.read_html(r.text)
    db = 'eipinfos'
    engine = create_engine('mysql+pymysql://eip:123456@localhost:3306/{0}?charset=utf8'.format(db))
    try:
        dfs[0].to_sql('list_eips',con = engine,if_exists='append',index=False)
        dfs[1].to_sql('list_eips',con = engine,if_exists='append',index=False)
    except Exception as e:
    	print(e)


def get_releases_infos(url):
    res_list = []
    body_list = []
    USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    i = 1
    while i < 40:
        try:
            random_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
            # print('.....',random_agent)
            time.sleep(random.random() * i)
            headers = {
                'User-Agent': random_agent,
            }
            request = urllib2.Request(url, headers=headers)
            data = urllib2.urlopen(request, timeout=20).read().decode('UTF-8')
            break
        except Exception as e:
            print("Error:%s"%i,e)
            i = i + 1

    soup = BeautifulSoup(data, 'lxml')
    # for item in soup.select('<div class="d-flex flex-column flex-md-row my-5 flex-justify-center">'):
    #     detail_url = item.get('href')
    myAttrs = {'class':'d-flex flex-column flex-md-row my-5 flex-justify-center'}
    detail_rel = soup.find_all(name='div',attrs=myAttrs)
    subAttrs = {'class':'Link--primary'}
    # detail_rel_name = detail_rel[0].find(name='a',attrs=subAttrs).get_text()

    res_list=[]
    for i in range(0,len(detail_rel)):
        detail_rel_name = detail_rel[i].find(name='a',attrs=subAttrs).get_text()
        res_list.append(detail_rel_name)

    body_list = []
    for i in range(0,len(detail_rel)):
        bodyAttrs = {'class':'markdown-body my-3'}
        detail_rel_body = detail_rel[i].find(name='div',attrs=bodyAttrs)
        pattern = re.compile(r'[\s](EIP-?\d+).*(\#\d{5})')
    #pattern = re.compile(r'^EIP(\d+).*(\#\d+\/a\)$)')
        result = pattern.findall(str(detail_rel_body))
        body_list.append(result)
    # print("test........",type(detail_rel))
    print(res_list)
    print(body_list)
    return res_list,body_list

def get_pages_num(url):
    USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]

    # print('.....',random_agent)
    i = 1
    while i <= 20:
        try:
            time.sleep(random.random() * i)
            random_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
            headers = {
                'User-Agent': random_agent,
            }
            request = urllib2.Request(url, headers=headers)
            data = urllib2.urlopen(request, timeout=20).read().decode('UTF-8')
            break
        except Exception as e:
            print(e)
            i = i + 1

    soup = BeautifulSoup(data, 'lxml')
    myAttrs = {'class': 'pagination'}
    page_num = int(soup.find(name='div', attrs=myAttrs).find_all('a')[-2].get_text())
    return page_num

def write_resinfo_to_db(resinfos):
    resinfos = {'Ploitari (v1.10.17)': [], 'Osun (v1.10.16)': [('EIP712', '#24220')], 'Faryar (v1.10.15)': [],
                'Hourglass Nebula (v1.10.14)': [('EIP-3670', '#24017')], 'Far Rim (v1.10.13)': [],
                'Vallhallan Threshold (v1.10.12)': [('EIP-1559', '#23840')], 'Xathorron (v1.10.11)': [],
                'Sytau (v1.10.10)': [], 'Attican Beta (v1.10.9)': [], 'Hades Gamma (v1.10.8)': [],
                'Styx Theta (v1.10.7)': [], 'Terra Nova (v1.10.6)': [],
                'Exodus Cluster (v1.10.5)': [('EIP-1559', '#22898'), ('EIP-1559', '#23038')],
                'Voyager Cluster (v1.10.4)': [('EIP-1559', '#22898'), ('EIP-1559', '#23038'), ('EIP-1559', '#23039'),
                                              ('EIP-1559', '#22966'), ('EIP-1559', '#23050'), ('EIP-1559', '#22842'),
                                              ('EIP-1559', '#22930')],
                'Maroon Sea (v1.10.3)': [('EIP-2929', '#22702'), ('EIP-2930', '#22585')],
                'Kepler Verge (v1.10.2)': [('EIP-2718', '#22604'), ('EIP-2718', '#22491'), ('EIP-2718', '#22480'),
                                           ('EIP-712', '#22378'), ('EIP-2718', '#22457')], 'Gemini Sigma (v1.10.1)': [],
                'Pangaea Expanse (v1.10.0)': [('EIP-2364', '#21930'), ('EIP-155', '#21686'), ('EIP-2930', '#21502')],
                'Marljeh (v1.9.25)': [], 'Akantha (v1.9.24)': [], 'Tupari (v1.9.23)': [], 'Noverian Rum (v1.9.22)': [],
                'Tavum (v1.9.21)': [], 'Paragade (v1.9.20)': [], 'Red Janey (v1.9.19)': [],
                'Illium Elite (v1.9.18)': [], 'Mount Milgrom (v1.9.17)': [], 'Ryncol (v1.9.16)': [],
                'Dextro Heat Sink (v1.9.15)': [], 'Pink Marble (v1.9.14)': [], 'Drossix Blue (v1.9.13)': [],
                'Tall Moose (v1.9.12)': [], 'Weeping Heart (v1.9.11)': [], 'Rojo Loco (v1.9.10)': [],
                'Serrice Ice (v1.9.9)': [], 'Thessian Temple (v1.9.8)': [], 'Quad Kicker (v1.9.7)': [],
                'Elasa (v1.9.6)': [('EIP-1898', '#19491')], 'Memory Stealer (v1.9.5)': [], 'Frozen Pyjak (v1.9.4)': [],
                'Tasty Tankard (v1.9.3)': [], 'Blue Thessia (v1.9.2)': [], 'Lucky Leprechaun (v1.9.1)': [],
                'Full Biotic Kick (v1.9.0)': [], 'Punisher (v1.8.27)': [], 'Light Ball (v1.8.26)': [],
                'White Ball (v1.8.25)': [], 'Pointy Eightball (v1.8.24)': [], 'Xircus (v1.8.23)': [],
                "Can'tstantinople (v1.8.22)": [('EIP-1283', '#18486')], 'Byzantium Revert (v1.8.21)': [],
                'Constant (v1.8.20)': [], 'No Nick (v1.8.19)': [], 'Devcon Delay (v1.8.18)': [],
                'Shoutingstone (v1.8.17)': [], 'Budapest (v1.8.16)': [], 'Khazad-dûm² (v1.8.15)': [],
                'Khazad-dûm (v1.8.14)': [], 'Swarming (v1.8.13)': [], 'Waggle Dance (v1.8.12)': [],
                'Streamline (v1.8.11)': [], 'Sacrosancter (v1.8.10)': [], 'Sacrosanct (v1.8.9)': [],
                'Coffice (v.1.8.8)': [], 'Titanium (v1.8.7)': [], 'Third Derivative (v1.8.6)': [],
                'Second Derivative (v1.8.5)': [], 'Dirty Derivative (v1.8.4)': [],
                'Supreme Gardening Equipment (v1.8.3)': [], 'Frost (v1.8.2)': [], 'Iceberg² (v1.8.1)': [],
                'Iceberg¹ (v1.8.0)': [], 'Weir (v1.7.3)': [], 'Urgent Update (v1.7.2)': [], 'Ptolemy (v1.7.1)': [],
                'Megara (v1.7.0)': [], 'AYTABTU (v1.6.7)': [], 'lgtm on mobile (v1.6.6)': [], 'Hat Trick (v1.6.5)': [],
                'Coverage (v1.6.4)': [], 'Covfefe (v1.6.3)': [], 'Nonce, Inc. (v1.6.2)': [],
                'Deripors of Ohratuu (v1.6.1)': [], 'Puppeth Master (v1.6.0)': [], "Davy Jones' Locker (v1.5.9)": [],
                'Peachest (v1.5.8)': [], 'Peacher (v1.5.7)': [], 'Peach (v1.5.6)': [],
                "Doesn't look like anything to me (1.5.5)": [], 'Stat it (v1.5.4)': [], 'Touch Revert (v1.5.3)': [],
                'Cry uncle (v1.5.2)': [], 'Let There Be Less Typos (v1.5.1)': [], 'Let There Be Light (v1.5.0)': [],
                'Garbage Man (v1.4.19)': [], 'Note 7 (v1.4.18)': [], 'Poolaid (v1.4.17)': [],
                'Dear Diary (v1.4.16)': [], 'Come at me Bro (1.4.15)': [], 'What else should we rewrite? (1.4.14)': [],
                'Into the Woods (1.4.13)': [], 'From Shanghai, with love (1.4.12)': [], 'Minor Text Fixes (1.4.11)': [],
                'Return of the ETH (1.4.10)': [], 'The network strikes back (1.4.9)': [], 'DAO Wars (1.4.8)': [],
                'Colourise (1.4.7)': [], 'EDGE (1.4.6)': [], 'drop table users (1.4.5)': [], 'Gethasaurus (1.4.4)': [],
                'Gethy McGethface (1.4.3)': [], 'Gethy McGethface (1.4.2 final)': [], 'Knoxjonesi (1.4.1)': [],
                'Bursarius (1.4.0)': [], 'Release 1.3.6': [], 'Release 1.3.5': [], 'Homestead (1.3.4)': [],
                'Breviceps (1.3.3)': [], 'Attwater (1.3.2)': [], 'Arenarius (1.3.1)': [],
                'Bugfoot (1.2.3) hotfix 2': [], 'Bugfoot (1.2.2) hotfix 1': [], 'Bugfoot  (1.2.1)': [],
                'Liquid Fairies (1.1.0) Hotfix 3': [], 'Liquid Fairies (1.1.0) Hotfix 2': [],
                'Liquid Fairies (1.1.0) Hotfix 1': [], 'v1.0.3': [], 'Liquid Fairies (1.1.0)': [], 'v1.0.2': [],
                'Thawing (1.0.1) Hotfix 1': [], 'Frontier (1.0.0)': [], 'Release 0.9.38 - RC2': [],
                'Release 0.9.36 - Frozen': [], 'Hotfix release 0.9.34-1': [], 'Release 0.9.34': [],
                'Release 0.9.32': [], 'Release 0.9.30 - Consolation': [], 'Release 0.9.28': [],
                'Fork slayer (0.9.26)': [], 'Olympic Release (0.9.25)': [], 'Olympic Release (0.9.24)': [],
                'Olympic Release (0.9.23)': [], 'Olympic Release (0.9.21.1)': [], 'Olympic Release (0.9.21)': [],
                'Olympic Release (0.9.20)': [], 'Olympic Release': [], 'Proof of concept 8': [],
                'Proof of concept 7': [], 'Mist 0.6.8': [], 'Mist 0.6.7': [], 'Mist 0.6.6': [], 'Mist 0.6.5': [],
                '0.6.0 - Adrastea': [], 'PoC5 Release (v0.5.19)': [], 'PoC5 Release (v0.5.18)': []}

    for key, value in resinfos.items():
        release_info = key
        for item in value:
            conn = pymysql.connect(
                host='localhost',  # 本地服务器
                user='eip',
                password='123456',  # 数据库密码
                port=3306,  # 默认端口
                charset='utf8',
                db='eipinfos')
            cursor = conn.cursor()
            exist_eip_sql = "select Number from list_eips;"
            cursor.execute(exist_eip_sql)
            exist_eip_list_tmp = cursor.fetchall()
            exist_eip_list = [str(item) for item in list(exist_eip_list_tmp)]
            # print('exist_eip_list..............', exist_eip_list)

            # print("EIP %s  relases %s commit %s" % (eip_info, release_info, commit_info))
            # sql = "UPDATE list_eips SET Release_info %s,HF_scheduled =%s WHERE Number = %d"(release_info,commit_info,eip_info)
            print(value, len(value))
            if len(value) == 1:
                eip_tmp_info, commit_info = item
                eip_info = int(re.match(r'EIP(-?)(\d+)', eip_tmp_info).group(2))
                if eip_info in exist_eip_list:
                    sql = 'INSERT INTO list_eips(Number,Release_info,Commit_info)  VALUES ("%d","%s","%s");' % (
                        release_info, commit_info, int(eip_info))
                else:
                    sql = 'UPDATE list_eips SET Release_info = "%s",Commit_info = "%s" WHERE Number = "%d";' % (
                        release_info, commit_info, int(eip_info))

            else:
                eip_commit_val = ''
                for (eip_tmp_info, commit_tmp_info) in value:
                    eip_info = int(re.match(r'EIP(-?)(\d+)', eip_tmp_info).group(2))
                    eip_commit_val = eip_commit_val + commit_tmp_info
                    if eip_info in exist_eip_list:
                        sql = 'INSERT INTO list_eips(Number,Release_info,Commit_info)  VALUES ("%d","%s","%s");' % (
                            release_info, eip_commit_val, int(eip_info))
                    else:
                        sql = 'UPDATE list_eips SET Release_info = "%s",Commit_info = "%s" WHERE Number = "%d";' % (
                            release_info, eip_commit_val, int(eip_info))
            cursor.execute(sql)
            conn.commit()
            print('%s;' % sql)
            conn.close()

                #       sql = 'CREATE TABLE IF NOT EXISTS list_eips (Number INT(30) NOT NULL,eip_number INT(30) NOT NULL,eip_type VARCHAR(100),title_content VARCHAR(100) ,PRIMARY KEY (serial_number))'
                # listed_company是要在wade数据库中建立的表，用于存放数据


def write_block_to_db(url):
    USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]

    random_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
    # print('.....',random_agent)
    headers = {
        'User-Agent': random_agent,
    }

    request = urllib2.Request(url, headers=headers)
    data = urllib2.urlopen(request).read().decode('UTF-8')
    soup = BeautifulSoup(data, 'lxml')

    type_Attrs = {'class': 'SharedStyledComponents__Header3-sc-1cr9zfr-24 fWQpXW'}
    res = soup.find_all('h3', {'class': 'SharedStyledComponents__Header3-sc-1cr9zfr-24 fWQpXW'})

    type_list = [item.get_text() for item in res]
    dest_str = ['London', 'Berlin']
    pos_list = []
    for i in dest_str:
        pos_list.append(type_list.index(i))

    res = soup.find_all('a', {'class': 'Link__ExternalLink-sc-e3riao-0 gABYms', 'rel': 'noopener noreferrer'})
    block_tmp_list = []
    block_dict_str = ''

    conn = pymysql.connect(
        host='localhost',  # 本地服务器
        user='eip',
        password='123456',  # 数据库密码
        port=3306,  # 默认端口
        charset='utf8',
        db='eipinfos')
    cursor = conn.cursor()

    for item in res:

        item_val = item.get_text()
        res = re.match(r'^\d+.*', item_val)
        if res:
            block_tmp_list.append(res.group())
            if len(block_tmp_list) in pos_list:
                block_num = res.group()
        else:
            eip_res = re.match(r'EIP-?(\d+).*', item_val)
            if len(block_tmp_list) in pos_list and eip_res:
                eip_info = eip_res.group(1)
                sql = 'UPDATE list_eips SET Block_number = "%s" WHERE Number = "%d";' % (block_num, int(eip_info))
                cursor.execute(sql)
                conn.commit()
                print('%s;' % sql)
    conn.close()


if __name__=="__main__":
    '''Create Databases and tables;'''
    generate_mysql()

    ''' Crawler EIP info,write to db'''
    eips_url = 'https://eips.ethereum.org/all'
    write_eip_to_db(url=eips_url)

    '''Crawler release and commit info,write to db'''
    url = "https://github.com/ethereum/go-ethereum/releases"
    RES_list_total = []
    EIP_list_total = []
    RES_dict = {}
    page_num = get_pages_num(url)
    for i in range(1,page_num+1):
        RES_list_tmp = []
        EIP_list_tmp = []
        time.sleep(random.random() * 2)
        sub_url = url+ "?page=%s"%str(i)
        print("URL.......",sub_url)
        RES_list_tmp,EIP_list_tmp = get_releases_infos(url=sub_url)
        RES_list_total = RES_list_total + RES_list_tmp
        EIP_list_total = EIP_list_total + EIP_list_tmp
    RES_dict = dict(zip(RES_list_total, EIP_list_total))
    write_resinfo_to_db(resinfos=RES_dict)

    '''Crewler london's info and wirte db'''
    london_url = 'https://ethereum.org/en/history'
    write_block_to_db(url = london_url)

