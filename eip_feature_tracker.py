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
import time
import os

DB_PORT = int(os.environ.get('DB_PORT'))
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

print(DB_PORT,DB_HOST,DB_USER,DB_PASS,DB_NAME)



def generate_mysql():
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        charset='utf8',
        db=DB_NAME)
    cursor = conn.cursor()
    # delete_sql = 'drop table list_eips'
    # cursor.execute(delete_sql)

    sql = 'CREATE TABLE IF NOT EXISTS list_eips (ID INT(20) NOT NULL AUTO_INCREMENT ,Number INT(30) NOT NULL,EIP_URL VARCHAR(200),Title VARCHAR(100),Author VARCHAR(300),Release_info VARCHAR(200),Release_URL VARCHAR(200),Commit_info VARCHAR(200),Block_number VARCHAR(100), Iotex_supported VARCHAR(100),PRIMARY KEY (ID))'


    cursor.execute(sql)
    conn.close()

def write_eip_to_db(url):

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    dfs = pd.read_html(r.text)
    db = DB_NAME
    engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'.format(DB_USER,DB_PASS,DB_HOST,DB_PORT,DB_NAME))
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
        pattern = re.compile(r'[\s]?(EIP-?\d+).*?(\#\d{5}.*?)\)')
    #pattern = re.compile(r'^EIP(\d+).*(\#\d+\/a\)$)')
        result = pattern.findall(str(detail_rel_body))

        body_list.append(result)
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

def write_resinfo_to_db(resinfos,urlinfos):
    print("resinfos.................",resinfos)
    for key, value in resinfos.items():
        release_info = key.strip().replace('\n', '').replace('\r', '')
        pos = list(resinfos).index(key)
        URL_info = urlinfos[pos]
        for item in value:
            conn = pymysql.connect(
                host=DB_HOST,  # 本地服务器
                user=DB_USER,
                password=DB_PASS,  # 数据库密码
                port=DB_PORT,  # 默认端口
                charset='utf8',
                db=DB_NAME)
            cursor = conn.cursor()
            # print('exist_eip_list..............', exist_eip_list)

            # print("EIP %s  relases %s commit %s" % (eip_info, release_info, commit_info))
            # sql = "UPDATE list_eips SET Release_info %s,HF_scheduled =%s WHERE Number = %d"(release_info,commit_info,eip_info)
            print(value, len(value))
            if len(value) == 1:
                eip_tmp_info, commit_tmp_info = item
                commit_pat = re.compile(r'\#\d{5}')
                commit_info = "".join(commit_pat.findall(str(commit_tmp_info)))
                eip_info = int(re.match(r'EIP(-?)(\d+)', eip_tmp_info).group(2))
                exist_eip_sql = "select * from list_eips where Number = %d;"%(int(eip_info))
                cursor.execute(exist_eip_sql)
                exist_eip_list_tmp = cursor.fetchall()
                # print(exist_eip_list_tmp,eip_info)
                if exist_eip_list_tmp:
                    exist_eip_Release_info = exist_eip_list_tmp[-1][5]
                    exist_eip_Commit_info = exist_eip_list_tmp[-1][7]
                    exist_eip_Title_info = exist_eip_list_tmp[-1][3]
                    if exist_eip_Release_info is None:
                        sql = 'UPDATE list_eips SET Commit_info = "%s",Release_info="%s",Release_URL="%s"  WHERE Number = "%d";' % (
                            commit_info, release_info,URL_info,int(eip_info))
                    else:
                        if exist_eip_Release_info != release_info:
                            # print("exist_eip_Release_info=======",exist_eip_Release_info,release_info,eip_info)
                            sql = 'INSERT INTO list_eips(Number,Title,Release_info,Commit_info,Release_URL)  VALUES ("%d","%s","%s","%s","%s");' % (
                                int(eip_info),exist_eip_Title_info,release_info, commit_info,URL_info)
                        else:
                            sql = 'UPDATE list_eips SET Commit_info = "%s",Release_URL="%s" WHERE Number = "%d" and Release_info="%s";' % (
                                commit_info,URL_info,int(eip_info),release_info)
                    cursor.execute(sql)
                    conn.commit()
                    # print('%s;' % sql)

            else:
                eip_commit_val = ''
                print("muti_value.............",value,release_info)
                new_dict = {}
                for (eip_tmp_info, commit_tmp_info) in value:
                    eip_info = int(re.match(r'EIP(-?)(\d+)', eip_tmp_info).group(2))
                    commit_pat = re.compile(r'\#\d{5}')
                    commit_info = "".join(commit_pat.findall(str(commit_tmp_info)))
                    if eip_info not in new_dict.keys():
                        new_dict[eip_info] = commit_info
                    else:
                        eip_commit_val = new_dict[eip_info] + commit_info
                        new_dict[eip_info] = eip_commit_val
                exist_eip_sql = "select * from list_eips where Number = %d;" % (int(eip_info))
                # print(exist_eip_sql)
                cursor.execute(exist_eip_sql)
                exist_eip_list_tmp = cursor.fetchall()
                for eip_info,commit_info in new_dict.items():
                    # print(exist_eip_list_tmp,eip_info)
                    if exist_eip_list_tmp:
                        exist_eip_Release_info = exist_eip_list_tmp[-1][5]
                        exist_eip_Commit_info = exist_eip_list_tmp[-1][7]
                        exist_eip_Title_info = exist_eip_list_tmp[-1][3]
                        if exist_eip_Release_info is None:
                            sql = 'UPDATE list_eips SET Commit_info = "%s",Release_info="%s",Release_URL="%s" WHERE Number = "%d";' % (
                                commit_info,release_info,URL_info,int(eip_info))
                        else:
                            if exist_eip_Release_info != release_info:

                                # print("exist_eip_Release_info=======",exist_eip_Release_info,release_info,eip_info)
                                sql = 'INSERT INTO list_eips(Number,Title,Release_info,Commit_info,Release_URL)  VALUES ("%d","%s","%s","%s","%s");' % (
                                    int(eip_info),exist_eip_Title_info,release_info, commit_info,URL_info)
                            else:
                                sql = 'UPDATE list_eips SET Commit_info = "%s",Release_URL="%s" WHERE Number = "%d" and Release_info="%s";' % (
                                    commit_info,URL_info, int(eip_info),release_info)
                        print('%s;' % sql)
                        cursor.execute(sql)
                        conn.commit()
            conn.close()

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

    # type_Attrs = {'class': re.compile('SharedStyledComponents__Header3-sc')}
    res = soup.find_all('h3', {'class': re.compile('SharedStyledComponents__Header3-sc')})

    type_list = [item.get_text() for item in res]
    dest_str = ['London', 'Berlin']
    pos_list = []
    for i in dest_str:
        pos_list.append(type_list.index(i))

    res = soup.find_all('a', {'class': re.compile('Link__ExternalLink-sc-')})
    # res = soup.find_all('a', {'class': 'Link__ExternalLink-sc-e3riao-0 gABYms', 'rel': 'noopener noreferrer'})
    block_tmp_list = []
    block_dict_str = ''

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        charset='utf8',
        db=DB_NAME)
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

    # iotx support
    res = soup.find_all('a', {'class': 'Link__ExternalLink-sc-e3riao-0 gABYms', 'rel': 'noopener noreferrer'})
    block_tmp_list = []
    iotx_support = {'Istanbul': 'Iceland', 'Muir Glacier': 'Iceland', 'Constantinople': 'Greenland'}
    iotx_pos_list = []
    for i in iotx_support.keys():
        iotx_pos_list.append(type_list.index(i))

    for item in res:
        item_val = item.get_text()
        res = re.match(r'^\d+.*', item_val)
        if res:
            block_tmp_list.append(res.group())
            if len(block_tmp_list) in iotx_pos_list:
                block_num = res.group()
        else:
            eip_res = re.match(r'EIP-?(\d+).*', item_val)
            if len(block_tmp_list) in iotx_pos_list and eip_res:
                eip_info = eip_res.group(1)
                sql = 'UPDATE list_eips SET Iotex_supported = "Yes" WHERE Number = "%d";' % (int(eip_info))
                cursor.execute(sql)
                conn.commit()

    conn.close()

def export_data_to_md(eipurl):
    gen_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    file_path = './index.md'
    dict_file = open(file_path, 'w', encoding='UTF-8')
    dict_file.write('## Ethereum Feature Tracker')
    dict_file.write('\n %s updated \n' % (gen_time))
    dict_file.write('\n|EIP Number | Release info | Commit info |  Block number | Iotex supported |')
    dict_file.write('\n|:--- | :--- | :--- | :--- | :--- |')
    dict_file.close()

    dict_file = open(file_path, 'a', encoding='UTF-8')
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        charset='utf8',
        db=DB_NAME)
    cursor = conn.cursor()
    sql = ''

    sql = "select Number,Release_info,Commit_info,Block_number,Iotex_supported,Release_URL from %s.list_eips  ORDER BY Commit_info desc;"%DB_NAME
    cursor.execute(sql)
    fields = cursor.fetchall()
    for field in fields:
        eip_number = str(field[0])
        Release_info = str(field[1])
        Commit_info = str(field[2])
        Block_number = str(field[3])
        Iotx_sup = str(field[4])
        Release_url = str(field[5])
        info = ' | ' + '[' + eip_number + ']' + '(' + eipurl + ')' + ' | ' + '[' + Release_info + ']' + '(' + Release_url + ')' + ' | ' + Commit_info + ' | ' + Block_number + ' | ' + Iotx_sup + '|'
        dict_file.write('\n ' + info)

    conn.close()
    dict_file.close()

if __name__=="__main__":
    '''Create databases and tables;'''
    generate_mysql()

    ''' Crawler EIP info & Write to db'''
    eips_url = 'https://eips.ethereum.org/all'
    write_eip_to_db(url=eips_url)

    '''Get release info & Get commit info & Write to db'''
    url = "https://github.com/ethereum/go-ethereum/releases"
    RES_list_total = []
    EIP_list_total = []
    URL_list_total = []
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
        for i in range(0, len(RES_list_total)):
            URL_list_total.append(sub_url)
    RES_dict = dict(zip(RES_list_total, EIP_list_total))
    write_resinfo_to_db(resinfos=RES_dict,urlinfos = URL_list_total)

    '''Crewler london's info and wirte db'''
    block_url = 'https://ethereum.org/en/history'
    write_block_to_db(url = block_url)

    '''Export data to makedown'''
    export_data_to_md(eipurl=eips_url)

