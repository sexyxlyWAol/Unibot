import os
import time
import ujson as json
import traceback
from ujson import JSONDecodeError

import requests
from requests import ReadTimeout

from modules.config import apiurls, enapiurls, twapiurls, krapiurls, proxies, \
                            rank_query_ban_servers, suite_uploader_path


class maintenanceIn(Exception):
   pass

class userIdBan(Exception):
   pass

class apiCallError(Exception):
    pass

class serverNotSupported(Exception):
    pass

class QueryBanned(Exception):
    pass

def callapi(url, server='jp', query_type='unknown', is_force_update=False):
    global twapiurls
    global krapiurls

    if server == 'jp':
        urlroots = apiurls
    elif server == 'en':
        urlroots = enapiurls
    elif server == 'tw':
        urlroots = twapiurls
    elif server == 'kr':
        urlroots = krapiurls
    else:
        raise serverNotSupported
    
    if server in rank_query_ban_servers:
        if '/ranking?targetRank' in url:
            targetRank = int(url[url.find('targetRank=') + len('targetRank='):])
            with open('data/jptop100.json', 'r', encoding='utf-8') as f:
                jptop100 = json.load(f)
            updatetime = time.localtime(os.path.getmtime('data/jptop100.json'))
            for single in jptop100["rankings"]:
                if single["rank"] == targetRank:
                    return {
                        "rankings": [single],
                        'updateTime': time.strftime("%m-%d %H:%M:%S", updatetime)
                    }
            else:
                return {
                        "rankings": []
                    }
        if '/ranking?targetUserId=' in url:
            targetUserId = int(url[url.find('targetUserId=') + len('targetUserId='):])
            with open('data/jptop100.json', 'r', encoding='utf-8') as f:
                jptop100 = json.load(f)
            updatetime = time.localtime(os.path.getmtime('data/jptop100.json'))
            for single in jptop100["rankings"]:
                if single["userId"] == targetUserId:
                    return {
                        "rankings": [single],
                        'updateTime': time.strftime("%m-%d %H:%M:%S", updatetime)
                    }
            else:
                return {
                        "rankings": []
                    }
        if '/profile' in url and query_type != 'daibu' and not is_force_update:
            userid = url[url.find('user/') + 5:url.find('/profile')]
            if os.path.exists(f'{suite_uploader_path}{userid}.json'):
                with open(f'{suite_uploader_path}{userid}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data
            elif query_type in ['b30', 'jindu', 'rank']:
                raise QueryBanned
    

    for urlroot in urlroots:
        try:
            if 'https' in urlroot:
                resp = requests.get(urlroot + url, timeout=10, proxies=proxies)
            else:
                resp = requests.get(urlroot + url, timeout=10)
            data = json.loads(resp.content)
            if data == {'status': 'maintenance_in'}:
                raise maintenanceIn
            elif data == {'status': 'user_id_ban'}:
                raise userIdBan
            if server in ['tw', 'kr'] and len(urlroots) > 1 and urlroot == urlroots[1]:
                # 台服api不明原因容易卡死 卡死后切换到备用服务器
                twapiurls[0], twapiurls[1] = twapiurls[1], twapiurls[0]
                krapiurls[0], krapiurls[1] = krapiurls[1], krapiurls[0]
                print('交换外服主从服务器次序，新地址:', twapiurls[0])
            return data
        except (requests.exceptions.ConnectionError, JSONDecodeError, ReadTimeout):
            print(urlroot, '请求失败')
            pass

    raise apiCallError
