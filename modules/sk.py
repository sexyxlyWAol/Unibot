import datetime
from urllib.parse import quote
from matplotlib.dates import DateFormatter, date2num
import pandas as pd
import ujson as json
import os.path
import sqlite3
import time
import traceback
from os import path
import pymysql

from modules.config import env, rank_query_ban_servers
from modules.getdata import QueryBanned, callapi
from modules.mysql_config import *
from PIL import Image, ImageFont, ImageDraw
import matplotlib
import pytz
import requests
import yaml
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

from modules.config import predicturl, proxies, ispredict

rankline = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000,
            10000, 20000, 30000, 40000, 50000, 100000, 100000000]
predictline = [10, 20, 30, 40, 50, 100, 100000000]

botpath = os.path.abspath(os.path.join(path.dirname(__file__), ".."))

def idtoname(musicid):
    with open('masterdata/musics.json', 'r', encoding='utf-8') as f:
        musics = json.load(f)
    for i in musics:
        if i['id'] == musicid:
            return i['title']
    return ''


def timeremain(time, second=True):
    if time < 60:
        return f'{int(time)}秒' if second else '0分'
    elif time < 60*60:
        return f'{int(time / 60)}分{int(time % 60)}秒' if second else f'{int(time / 60)}分'
    elif time < 60*60*24:
        hours = int(time / 60 / 60)
        remain = time - 3600 * hours
        return f'{int(time / 60 / 60)}小时{int(remain / 60)}分{int(remain % 60)}秒' if second else f'{int(time / 60 / 60)}小时{int(remain / 60)}分'
    else:
        days = int(time / 3600 / 24)
        remain = time - 3600 * 24 * days
        return f'{int(days)}天{timeremain(remain)}' if second else f'{int(days)}天{timeremain(remain, False)}'


def currentevent(server):
    if server == 'jp':
        with open('masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif server == 'tw':
        with open('../twapi/masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif server == 'en':
        with open('../enapi/masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif server == 'kr':
        with open('../krapi/masterdata/events.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    for i in range(0, len(data)):
        startAt = data[i]['startAt']
        endAt = data[i]['closedAt']
        assetbundleName = data[i]['assetbundleName']
        now = int(round(time.time() * 1000))
        remain = ''
        if not startAt < now < endAt:
            continue
        if data[i]['startAt'] < now < data[i]['aggregateAt']:
            status = 'going'
            remain = timeremain((data[i]['aggregateAt'] - now) / 1000)
        elif data[i]['aggregateAt'] < now < data[i]['aggregateAt'] + 600000:
            status = 'counting'
        else:
            status = 'end'
        return {'id': data[i]['id'], 'status': status, 'remain': remain,
                 'assetbundleName': assetbundleName, 'eventType': data[i]['eventType']}


def eventtrack():
    twurl = 'http://127.0.0.1:5004/tw/api'
    now = int(time.time())
    time_printer('开始抓取冲榜查询id')
    event = currentevent('jp')
    if event['status'] == 'going':
        eventid = event['id']
        if not os.path.exists(f'yamls/event/{eventid}'):
            os.makedirs(f'yamls/event/{eventid}')
        try:
            conn = sqlite3.connect('data/events.db')
            c = conn.cursor()
            ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?rankingViewType=top100', 'jp')
            with open('data/jptop100.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(ranking, sort_keys=True, indent=4))
            
            for rank in ranking['rankings']:
                targetid = rank['userId']
                score = rank['score']
                name= rank['name']
                try:
                    c.execute(f'insert into "{eventid}" (time, score, userid) values(?, ?, ?)', (now, score, str(targetid)))
                except sqlite3.OperationalError:
                    c.execute(f'''CREATE TABLE "{eventid}"
                               ("time"   INTEGER,
                                "score"  INTEGER,
                                "userid" TEXT);''')
                    c.execute(f'insert into "{eventid}" (time, score, userid) values(?, ?, ?)',
                              (now, score, str(targetid)))

                try:
                    c.execute(f'insert into names (userid, name) values(?, ?)', (str(targetid), name))
                except sqlite3.IntegrityError:
                    c.execute(f'update names set name=? where userid=?', (name, str(targetid)))

            conn.commit()
            conn.close()
            time_printer('抓取完成')
        except:
            traceback.print_exc()
    else:
        time_printer('无正在进行的活动')


    time_printer('开始抓取台服冲榜查询id')
    event = currentevent('tw')
    if event['status'] == 'going':
        eventid = event['id']
        if not os.path.exists(f'yamls/event/tw{eventid}'):
            os.makedirs(f'yamls/event/tw{eventid}')
        try:
            conn = sqlite3.connect('data/events.db')
            c = conn.cursor()
            ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank=1&lowerLimit=99', 'tw')
            for rank in ranking['rankings']:
                targetid = rank['userId']
                score = rank['score']
                name= rank['name']
                try:
                    c.execute(f'insert into "tw{eventid}" (time, score, userid) values(?, ?, ?)', (now, score, str(targetid)))
                except sqlite3.OperationalError:
                    c.execute(f'''CREATE TABLE "tw{eventid}"
                               ("time"   INTEGER,
                                "score"  INTEGER,
                                "userid" TEXT);''')
                    c.execute(f'insert into "tw{eventid}" (time, score, userid) values(?, ?, ?)',
                              (now, score, str(targetid)))

                try:
                    c.execute(f'insert into names (userid, name) values(?, ?)', (str(targetid), name))
                except sqlite3.IntegrityError:
                    c.execute(f'update names set name=? where userid=?', (name, str(targetid)))

            ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank=101&lowerLimit=99', 'tw')
            for rank in ranking['rankings']:
                targetid = rank['userId']
                score = rank['score']
                name = rank['name']
                c.execute(f'insert into "tw{eventid}" (time, score, userid) values(?, ?, ?)', (now, score, str(targetid)))
                try:
                    c.execute(f'insert into names (userid, name) values(?, ?)', (str(targetid), name))
                except sqlite3.IntegrityError:
                    c.execute(f'update names set name=? where userid=?', (name, str(targetid)))

            conn.commit()
            conn.close()
            time_printer('抓取完成')
        except:
            traceback.print_exc()
    else:
        time_printer('台服无正在进行的活动')


class Error(Exception):
   pass

class cheaterFound(Error):
   pass


def recordname(qqnum, userid, name, userMusicResults=None, masterscore=None, server='jp'):
    # return True
    if env != 'prod':
        return True
    try:
        mydb = pymysql.connect(host=host, port=port, user='username', password=password,
                            database='username', charset='utf8mb4')
    except pymysql.err.OperationalError:
        return True
    mycursor = mydb.cursor()

    # 审核游戏昵称
    mycursor.execute('SELECT * from examresult where name=%s', (name,))
    data = mycursor.fetchone()
    if data is not None:
        if data[2]:
            result = True
        else:
            result = False
    else:
        try:
            resp = requests.get(f'http://127.0.0.1:5000/exam/{quote(name.replace("/", " "), "utf-8")}')
            sql_add = 'insert into examresult (name, result) values(%s, %s)'
            result = resp.json()['conclusion']
        except:
            traceback.print_exc()
            result = True
        if result:
            mycursor.execute(sql_add, (name, 1))
        else:
            mycursor.execute(sql_add, (name, 0))

    # 记录游戏昵称
    mycursor.execute('SELECT * from names where qqnum=%s and userid=%s and name=%s', (str(qqnum), str(userid), name))
    data = mycursor.fetchone()
    if data is None:
        sql_add = f'insert into names (userid, name, qqnum, result) values(%s, %s, %s, %s)'
        text = '合规' if result else '不合规'
        mycursor.execute(sql_add, (str(userid), name, str(qqnum), text))

    # qqnum = getIdOwner(userid, server)
    # if userMusicResults is not None and server == 'jp':
    #     # 判断是否有36+FC/AP
    #     if masterscore[36][0] + masterscore[36][1] + masterscore[37][0] + masterscore[37][1] != 0:
    #         mycursor.execute('SELECT * from suspicious where qqnum=%s and userid=%s', (str(qqnum), str(userid)))
    #         data = mycursor.fetchone()
    #         if data is None:
    #             sql_add = f'insert into suspicious (userid, name, qqnum, reason) values(%s, %s, %s, %s)'
    #             mycursor.execute(sql_add, (str(userid), name, str(qqnum), '36+FC/AP'))
    #     alltext = ''
    #     # 判断是否有34+初见FC/AP
    #     for result in userMusicResults:
    #         if result["musicDifficulty"] == 'master' and result["musicId"] in masterscore['33+musicId']:
    #             if result["fullComboFlg"] or result["fullPerfectFlg"]:
    #                 if result["updatedAt"] == result["createdAt"]:
    #                     finish_time = datetime.datetime.fromtimestamp(result["updatedAt"] / 1000,
    #                                                            pytz.timezone('Asia/Shanghai')).strftime('%Y/%m/%d %H:%M')
    #                     reason = finish_time + ' ' + idtoname(result["musicId"]) + ' MASTER ' + result['playType'] + ' 初见' \
    #                              + ('AP' if result["fullPerfectFlg"] else 'FC')
    #                     alltext += reason + '、'
    #                     mycursor.execute('SELECT * from suspicious where qqnum=%s and userid=%s and reason=%s',
    #                                      (str(qqnum), str(userid), reason))
    #                     data = mycursor.fetchone()
    #                     if data is None:
    #                         sql_add = f'insert into suspicious (userid, name, qqnum, reason) values(%s, %s, %s, %s)'
    #                         mycursor.execute(sql_add, (str(userid), name, str(qqnum), reason))
                        
    #                     mycursor.execute('SELECT * from suspicious where userid=%s', (str(userid), ))
    #                     data = mycursor.fetchall()
    #                     if data is not None:
    #                         for _ in data:
    #                             if _[6] == 'whitelist':
    #                                 mydb.commit()
    #                                 mycursor.close()
    #                                 mydb.close()
    #                                 return result
    #     if alltext != '':
    #         mydb.commit()
    #         mycursor.close()
    #         mydb.close()
    #         raise cheaterFound(f'{name} - {userid}、' + alltext +
    #                            '由于监测到打歌数据有高度开挂嫌疑，该账号id已被bot记录，如确认开挂，24小时内该账号与绑定qq将会被bot永久拉黑、'
    #                            '如有异议可在群883721511内用充足的证据（账号交易记录，自证手元等）对上述成绩做出合理的解释')
    mydb.commit()
    mycursor.close()
    mydb.close()
    return result


def cheater_ban_reason(userid):
    from imageutils import text2image
    mydb = pymysql.connect(host=host, port=port, user='username', password=password,
                        database='username', charset='utf8mb4')
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * from suspicious where userid=%s', (str(userid), ))
    data = mycursor.fetchall()
    if data is None:
        return '挂哥数据库未找到该账号'
    try:
        text = f'{data[0][1]} - {data[0][2]}\n'
    except IndexError:
        return '挂哥数据库未找到该账号'
    found = False
    for reason in data:
        if reason[5] != '36+FC/AP':
            text += reason[5] + '\n'
            found = True
    if not found:
        return '挂哥数据库未找到该账号'
    text += '由于监测到打歌数据有高度开挂嫌疑，该账号与已被bot拉黑、如有异议可在群883721511内用充足的证据（账号交易记录，自证手元等）对上述成绩做出合理的解释'
    infopic = text2image(text=text, max_width=1000)
    now = time.time()
    infopic.save(f'piccache/{now}.png')
    return f"[CQ:image,file=file:///{botpath}/piccache/{now}.png,cache=0]"


def chafang(targetid=None, targetrank=None, private=False, server='jp'):
    if server == 'jp':
        prefix = ''
    elif server == 'en':
        prefix = 'en'
    elif server == 'tw':
        prefix = 'tw'
    event = currentevent(server)
    eventid = event['id']
    if targetid is None:
        ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}', server)
        targetid = ranking['rankings'][0]['userId']
        private = True
    if event['status'] == 'going':
        conn = sqlite3.connect('data/events.db')
        c = conn.cursor()
        cursor = c.execute(f'SELECT * from "{prefix}{eventid}" where userid=?', (targetid,))
        userscores = {}
        for raw in cursor:
            userscores[raw[0]] = raw[1]
        if userscores == {}:
            conn.close()
            return '你要查询的玩家未进入前200，暂无数据'
        lasttime = 0
        twentybefore = 0
        hourbefore = 0
        cursor = c.execute(f'SELECT * from names where userid=?', (targetid,))
        for raw in cursor:
            username = raw[1]
        conn.close()
        if private:
            text = f'{username}\n'
        else:
            text = f'{username} - {targetid}\n'
        for times in userscores:
            lasttime = times
        for times in userscores:
            if -10 < times - (lasttime - 20 * 60) < 10:
                twentybefore = times
        for times in userscores:
            if -10 < times - (lasttime - 60 * 60) < 10:
                hourbefore = times
        lastupdate = 0
        count = 0
        hourcount = 0
        pts = []
        for times in userscores:
            count += 1
            if count == 1:
                lastupdate = userscores[times]
            else:
                if userscores[times] != lastupdate:
                    if hourbefore != 0 and times > hourbefore:
                        hourcount += 1
                        # print(hourcount, datetime.datetime.fromtimestamp(times,
                        #                                       pytz.timezone('Asia/Shanghai')).strftime('%H:%M'))
                    pts.append(userscores[times]-lastupdate)
                    lastupdate = userscores[times]
        if len(pts) >= 10:
            ptsum = 0
            for i in range(len(pts)-10, len(pts)):
                ptsum += pts[i]
            text += f'近10次平均pt：{(ptsum / 10)/10000}W\n'
        if hourbefore != 0:
            text += f'时速: {(userscores[lasttime] - userscores[hourbefore])/10000}W\n'
        if twentybefore != 0:
            text += f'20min*3时速: {((userscores[lasttime] - userscores[twentybefore])*3)/10000}W\n'
        if hourcount != 0:
            text += f'本小时周回数: {hourcount}\n'
        stop = getstoptime(targetid, None, True, server=server)
        if len(stop) != 0:
            if stop[len(stop)]['end'] != 0:
                text += '周回中\n'
                text += f"连续周回时间: {timeremain(int(time.time()) - stop[len(stop)]['end'])}\n"
            else:
                text += '停车中\n'
                text += f"已停车: {timeremain(int(time.time()) - stop[len(stop)]['start'])}\n"
        else:
            for times in userscores:
                if times == 'name':
                    continue
                firsttime = times
                break
            text += '周回中\n'
            text += f"连续周回时间: {timeremain(int(time.time()) - firsttime)}\n"
            updatetime = datetime.datetime.fromtimestamp(lasttime,
                                       pytz.timezone('Asia/Shanghai')).strftime('%m/%d %H:%M')
            text += f"仅记录在200名以内时的数据，数据更新于{updatetime}"
        return text
    else:
        return '当前没有正在进行的活动'

def drawscoreline(targetid=None, targetrank=None, targetrank2=None, starttime=0, server='jp'):
    x1 = []
    x2 = []
    k1 = []
    k2 = []
    if server == 'jp':
        prefix = ''
    elif server == 'en':
        prefix = 'en'
    elif server == 'tw':
        prefix = 'tw'
    event = currentevent(server)
    eventid = event['id']
    if targetid is None:
        ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}', server)
        targetid = ranking['rankings'][0]['userId']

    conn = sqlite3.connect('data/events.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from "{prefix}{eventid}" where userid=?', (targetid,))
    userscores = {}
    for raw in cursor:
        userscores[raw[0]] = raw[1]
    if userscores == {}:
        conn.close()
        return False
    cursor = c.execute(f'SELECT * from names where userid=?', (targetid,))
    for raw in cursor:
        name = raw[1]
    
    if targetrank2 is not None:
        ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank2}', server)
        targetid2 = ranking['rankings'][0]['userId']
        cursor = c.execute(f'SELECT * from "{prefix}{eventid}" where userid=?', (targetid2,))
        userscores2 = {}
        for raw in cursor:
            userscores2[raw[0]] = raw[1]
        cursor = c.execute(f'SELECT * from names where userid=?', (targetid2,))
        for raw in cursor:
            name2 = raw[1]
        conn.close()
        for times in userscores2:
            if times > starttime:
                x2.append(times)
                k2.append(userscores2[times] / 10000)
    else:
        conn.close()

    for times in userscores:
        if times > starttime:
            x1.append(times)
            k1.append(userscores[times] / 10000)
    
    x1 = pd.to_datetime(x1, unit='s')
    df1 = pd.DataFrame({name: k1}, index=x1)
    # 创建新的时间序列，以防数据记录有空缺被直接连上，从x1的第一个时间戳开始，每60秒一个时间点
    new_index = pd.date_range(start=x1[0], end=x1[-1], freq='60S')
    # 使用新的时间序列重新索引原始数据
    df1 = df1.reindex(new_index)
    # 将时间戳转化为matplotlib可以处理的数字，否则会出现 OverflowError: int too big to convert 错误
    # 参考 https://stackoverflow.com/questions/66659928/overflowerror-int-too-big-to-convert-when-formatting-date-on-pandas-series-plot
    df1.index = date2num(df1.index.to_pydatetime())
    if targetrank2 is not None:
        x2 = pd.to_datetime(x2, unit='s')
        df2 = pd.DataFrame({name2: k2}, index=x2)
        df2 = df2.reindex(new_index)
        # 将时间戳转化为matplotlib可以处理的数字
        df2.index = date2num(df2.index.to_pydatetime())
        # 合并数据
        df_full = pd.concat([df1, df2], axis=1)
    else:
        df_full = df1

    fig_size = (12, 8)
    fig, ax = plt.subplots(1, 1, figsize=fig_size)
    df_full.plot(ax=ax)
    date_form = DateFormatter("%m-%d %H:%M", tz=pytz.timezone('Asia/Shanghai'))
    ax.xaxis.set_major_formatter(date_form)
    plt.xticks(rotation=20)
    font = FontProperties(fname="fonts/FOT-RodinNTLGPro-DB.ttf")
    if targetrank2 is not None:
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        plt.title(f"{name} vs {name2}", fontproperties=font)
        targetid = str(targetid) + str(targetid2)
    else:
        plt.title(name, fontproperties=font)
    plt.xlabel("時間", fontproperties=font)
    plt.ylabel("スコア / 万", fontproperties=font)
    ax.legend()
    plt.text(1, 0, 'Generated by Unibot', ha='right', va='bottom', transform=ax.transAxes)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.savefig(f'piccache/{targetid}.png', dpi=180)
    return f'piccache/{targetid}.png'

def time_printer(str):
    timeArray = time.localtime(time.time())
    Time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(Time, str)

def getstoptime(targetid=None, targetrank=None, returnjson=False, private=False, server='jp'):
    event = currentevent(server)
    eventid = event['id']
    if server == 'jp':
        prefix = ''
    elif server == 'en':
        prefix = 'en'
    elif server == 'tw':
        prefix = 'tw'
    if not returnjson:
        if targetid is None:
            ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}', server)
            targetid = ranking['rankings'][0]['userId']
            private = True
    conn = sqlite3.connect('data/events.db')
    c = conn.cursor()
    cursor = c.execute(f'SELECT * from "{prefix}{eventid}" where userid=?', (targetid,))
    userscores = {}
    for raw in cursor:
        userscores[raw[0]] = raw[1]
    if userscores == {}:
        conn.close()
        if returnjson:
            return {}
        return False
    cursor = c.execute(f'SELECT * from names where userid=?', (targetid,))
    for raw in cursor:
        username = raw[1]
    conn.close()
    lastupdate = 0
    count = 0
    stop = {}
    stopcount = 0
    stopping = False
    stoplength = 0
    for times in userscores:
        count += 1
        if count == 1:
            lastupdate = times
        else:
            if userscores[times] == userscores[lastupdate]:
                if times - lastupdate > 5 * 60:
                    if not stopping:
                        stopcount += 1
                        stopping = True
                        stop[stopcount] = {'start': 0, 'end': 0}
                        stop[stopcount]['start'] = lastupdate
            else:
                lastupdate = times
                if stopping:
                    stop[stopcount]['end'] = times
                    stopping = False

    if private:
        text = f'{username}\n停车时间段:\n'
    else:
        text = f'{username} - {targetid}\n停车时间段:\n'
    if returnjson:
        return stop
    if len(stop) != 0:
        for count in stop:
            start = stop[count]['start']
            starttime = datetime.datetime.fromtimestamp(start,
                                       pytz.timezone('Asia/Shanghai')).strftime('%m/%d %H:%M')
            end = stop[count]['end']
            endtime = datetime.datetime.fromtimestamp(end,
                                       pytz.timezone('Asia/Shanghai')).strftime('%m/%d %H:%M')
            if end == 0:
                endtime = ''
                end = int(time.time())
            stoplength += end - start
            text += f'{count}. {starttime} ~ {endtime} ({timeremain(end - start, False)})\n'
        text += f'总停车时间：{timeremain(stoplength, False)}\n'
        text += f"仅记录在200名以内时的数据"
        return text
    else:
        if returnjson:
            return stop
        return text + '未停车' + "\n仅记录在200名以内时的数据"

def getranks():
    time_printer('抓取时速')
    event = currentevent('jp')
    if event['status'] == 'going':
        eventid = event['id']
        if not os.path.exists(f'yamls/event/{eventid}'):
            os.makedirs(f'yamls/event/{eventid}')
        try:
            with open(f'yamls/event/{eventid}/ss.yaml') as f:
                ss = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            ss = {}
        now = int(time.time())
        ss[now] = {}
        for rank in rankline:
            if rank != 100000000:
                try:
                    ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={rank}', 'jp')
                    ss[now][rank] = ranking['rankings'][0]['score']
                except:
                    traceback.print_exc()
                    ss[now][rank] = 0
        with open(f'yamls/event/{eventid}/ss.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(ss, f)
        time_printer('时速抓取完成')
    else:
        time_printer('无正在进行的活动')

def ss():
    event = currentevent('jp')
    eventid = event['id']
    if event['status'] == 'going':
        try:
            with open(f'yamls/event/{eventid}/ss.yaml') as f:
                ss = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            return '暂无数据'
        text = ''
        hourago = 0
        for times in ss:
            lasttime = times
        for times in ss:
            if -120 < times - (lasttime - 60 * 60) < 120:
                hourago = times
                break
        if hourago != 0:
            for rank in rankline:
                if rank != 100000000:
                    speed = ss[lasttime][rank] - ss[hourago][rank]
                    text += f'{rank}: {speed/10000}W\n'
            Time = datetime.datetime.fromtimestamp(lasttime,
                                                   pytz.timezone('Asia/Shanghai')).strftime('%m/%d %H:%M:%S')
            return '一小时内实时时速\n' + text + '数据更新时间\n' + Time
        else:
            return '暂无数据'
    else:
        return '活动未开始'

def gettime(userid, server='jp'):
    if server == 'jp' or server == 'en':
        try:
            passtime = int(userid[:-3]) / 1024 / 4096
        except ValueError:
            return 0
        return 1600218000 + int(passtime)
    elif server == 'tw' or server == 'kr':
        try:
            passtime = int(userid) / 1024 / 1024 / 4096
        except ValueError:
            return 0
        return int(passtime)


def verifyid(userid, server='jp'):
    registertime = gettime(userid, server)
    now = int(time.time())
    if registertime <= 1601438400 or registertime >= now:
        return False
    else:
        return True


def ssyc(targetrank, eventid):
    raise QueryBanned
    try:
        with open('data/ssyc.yaml') as f:
            cachedata = yaml.load(f, Loader=yaml.FullLoader)
        cachetime = cachedata['cachetime']
        now = int(time.time())
        timepass = now - cachetime
        if timepass < 60 * 30 + 10:
            return cachedata[targetrank]
    except FileNotFoundError:
        cachedata = {}
    predict = json.loads(requests.get(predicturl, proxies=proxies).content)
    if predict['event']['id'] != eventid:
        for i in range(0, 16):
            cachedata[predictline[i]] = 0
        with open('data/ssyc.yaml', 'w') as f:
            yaml.dump(cachedata, f)
        return 0
    cachedata['cachetime'] = int(predict['data']['ts'] / 1000)
    for i in range(0, 16):
        cachedata[predictline[i]] = predict['data'][str(predictline[i])]
    with open('data/ssyc.yaml', 'w') as f:
        yaml.dump(cachedata, f)
    return predict['data'][str(targetrank)]

def skyc():
    text = '由于服务器限制，预测误差极大，请谨慎参考！\n'
    event = currentevent('jp')
    eventid = event['id']
    if event['status'] != 'going':
        return '预测暂时不可用'
    try:
        with open('data/ssyc.json', 'r', encoding='utf-8') as f:
            cachedata = json.load(f)
        cachetime = cachedata['data']['ts'] / 1000
        now = int(time.time())
        if now - cachetime < 60 * 30 + 10:
            # 本地缓存有效
            predict = cachedata
        else:
            # 本地缓存过期
            predict = json.loads(requests.get(predicturl, proxies=proxies).content)
    except FileNotFoundError:
        # 无本地缓存
        predict = json.loads(requests.get(predicturl, proxies=proxies).content)

    if predict['event']['id'] == eventid:
        for line in predict['data']:
            if line.isdigit():
                text = text + f'{line}名预测：{predict["data"][line]}\n'
        timeArray = time.localtime(predict['data']['ts'] / 1000)
        text = text + '\n预测线来自xfl03(3-3.dev)\n预测生成时间为' + time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        text = text + '\n预测的活动为' + predict['event']['name']
        with open('data/ssyc.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(predict, indent=4, ensure_ascii=False))
        return text
    else:
        return '预测暂时不可用'


def sk(targetid=None, targetrank=None, secret=False, server='jp', simple=False, qqnum='未知', ismain=True):
    # ismain是用来适配旧版分布式的 现在已停用没必要了 但很多代码懒得改就留着了
    event = currentevent(server)
    eventid = event['id']
    if server not in rank_query_ban_servers and event['status'] == 'counting':
        return '活动分数统计中，不要着急哦！'
    if server == 'jp':
        masterdatadir = 'masterdata'
    elif server == 'en':
        masterdatadir = '../enapi/masterdata'
    elif server == 'tw':
        masterdatadir = '../twapi/masterdata'
    elif server == 'kr':
        masterdatadir = '../krapi/masterdata'
    if targetid is not None:
        if not verifyid(targetid, server):
            bind = getqqbind(targetid, server)
            if bind is None:
                return '查不到捏'
            elif bind[2]:
                return '查不到捏，可能是不给看'
            else:
                targetid = bind[1]
        ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetUserId={targetid}', server)
    else:
        ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={targetrank}', server)
    try:
        name = ranking['rankings'][0]['name']
        rank = ranking['rankings'][0]['rank']
        score = ranking['rankings'][0]['score']
        userId = str(ranking['rankings'][0]['userId'])
        targetid = userId
        if server in rank_query_ban_servers:
            updateTime = ranking['updateTime']
        if not recordname(qqnum, userId, name):
            name = ''
    except IndexError:
        if server in rank_query_ban_servers:
            return '由于日服限制了查分api，只有排名前100可以使用该功能'
        else:
            return '查不到数据捏，可能这期活动没打'
    try:
        TeamId = ranking['rankings'][0]['userCheerfulCarnival']['cheerfulCarnivalTeamId']
        with open(f'{masterdatadir}/cheerfulCarnivalTeams.json', 'r', encoding='utf-8') as f:
            Teams = json.load(f)
        with open('yamls/translate.yaml', encoding='utf-8') as f:
            trans = yaml.load(f, Loader=yaml.FullLoader)
        try:
            translate = f"({trans['cheerfulCarnivalTeams'][TeamId]})"
        except KeyError:
            translate = ''
        if server == 'tw' or server == 'kr':
            translate = ''
        for i in Teams:
            if i['id'] == TeamId:
                teamname = i['teamName'] + translate
                assetbundleName = i['assetbundleName']
                break
    except KeyError:
        teamname = ''
        assetbundleName = ''
    img = Image.new('RGB', (600, 600), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    if server == 'kr':
        font = ImageFont.truetype('fonts/SourceHanSansKR-Medium.otf', 25)
    else:
        font = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 25)
    if not secret:
        userId = ' - ' + userId
    else:
        userId = ''
    pos = 20
    draw.text((20, pos), name + userId, '#000000', font)
    pos += 35
    if teamname != '':
        if server != 'kr':
            team = Image.open('data/assets/sekai/assetbundle/resources/ondemand/event/'
                            f'{event["assetbundleName"]}/team_image/{assetbundleName}.png')
            team = team.resize((45, 45))
            r, g, b ,mask = team.split()
            img.paste(team, (20, 63), mask)
            draw.text((70, 65), teamname, '#000000', font)
        else:  # 韩服添加了5v5队伍，使得编号与日服不一致
            draw.text((20, 65), teamname, '#000000', font)
            font = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 25)
        pos += 50
    msg = f'{name}{userId}\n{teamname}分数{score / 10000}W，排名{rank}'
    font2 = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 38)
    draw.text((20, pos), f'分数{score / 10000}W，排名{rank}', '#000000', font2)
    pos += 60
    if simple:
        return msg
    for i in range(0, 31):
        if rank < rankline[i]:
            break

    if rank > 1:
        if rank == rankline[i - 1]:
            upper = rankline[i - 2]
        else:
            upper = rankline[i - 1]
        try:
            ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={upper}', server)
            linescore = ranking['rankings'][0]['score']
        except IndexError:
            linescore = 0
        deviation = (linescore - score) / 10000
        draw.text((20, pos), f'{upper}名分数 {linescore/10000}W  ↑{deviation}W', '#000000', font)
        pos += 38
    if rank < 100000:
        if rank == rankline[i]:
            lower = rankline[i + 1]
        else:
            lower = rankline[i]
        try:
            ranking = callapi(f'/user/%7Buser_id%7D/event/{eventid}/ranking?targetRank={lower}', server)
            linescore = ranking['rankings'][0]['score']
        except IndexError:
            linescore = 0
        deviation = (score - linescore) / 10000
        draw.text((20, pos), f'{lower}名分数 {linescore / 10000}W  ↓{deviation}W', '#000000', font)
        pos += 38
    pos += 10
    if event['status'] == 'going' and ispredict and server == 'jp':
        for i in range(0, 17):
            if rank < predictline[i]:
                break
        linescore = 0
        if rank > 100:
            upper = predictline[i - 1]
            linescore = ssyc(upper, eventid)
            if linescore != 0:
                draw.text((20, pos), f'{upper}名 预测{linescore/10000}W', '#000000', font)
                pos += 38
        if rank < 100000:
            if rank == predictline[i]:
                lower = predictline[i + 1]
            else:
                lower = predictline[i]
            linescore = ssyc(lower, eventid)
            if linescore != 0:
                draw.text((20, pos), f'{lower}名 预测{linescore/10000}W', '#000000', font)
                pos += 38
        pos += 10
        font3 = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 16)
        draw.text((400, pos - 5), '预测线来自33（3-3.dev）\n     Generated by Unibot', (150, 150, 150), font3)
    if server in rank_query_ban_servers:
        font3 = ImageFont.truetype('fonts/SourceHanSansCN-Medium.otf', 16)
        draw.text((350, pos - 5), f'你的排名更新于{updateTime}\nGenerated by Unibot', (150, 150, 150), font3, align='right')
    if event['status'] == 'going':
        draw.text((20, pos), '活动还剩' + event['remain'], '#000000', font)
        pos += 38
    img = img.crop((0, 0, 600, pos + 20))
    img.save(f"piccache/{targetid}sk.png")
    return f"piccache/{targetid}sk.png"


def teamcount(server='jp'):
    server_directories = {
        'jp': 'masterdata',
        'en': '../enapi/masterdata',
        'tw': '../twapi/masterdata',
        'kr': '../krapi/masterdata'
    }
    masterdatadir = server_directories.get(server, 'masterdata')

    event = currentevent(server)
    eventid = event['id']
    data = callapi(f'/cheerful-carnival-team-count/{eventid}', server)
    
    try:
        with open(f'{masterdatadir}/cheerfulCarnivalTeams.json', 'r', encoding='utf-8') as f:
            Teams = json.load(f)
    except FileNotFoundError:
        Teams = []
        
    try:
        with open('yamls/translate.yaml', encoding='utf-8') as f:
            trans = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        trans = {}
    
    predictRates = {}
    timestamp_str = ''
    if server == 'jp':
        try:
            with open('masterdata/realtime/cheerful_predict.json', 'r', encoding='utf-8') as f:
                predictData = json.load(f)
            if eventid == predictData['eventId']:
                predictRates = predictData['predictRates']
                timestamp = datetime.datetime.fromtimestamp(predictData['timestamp']/1000, datetime.timezone(datetime.timedelta(hours=8)))
                timestamp_str = timestamp.strftime("预测于%Y/%m/%d %H:%M\n预测来自3-3.dev")
        except FileNotFoundError:
            pass
    
    text = ''
    for Counts in data['cheerfulCarnivalTeamMemberCounts']:
        TeamId = Counts['cheerfulCarnivalTeamId']
        memberCount = Counts['memberCount']
        translate = f"({trans['cheerfulCarnivalTeams'].get(TeamId, '')})" if TeamId in trans['cheerfulCarnivalTeams'] else ""
        team = next((i for i in Teams if i['id'] == TeamId), None)
        if team:
            predictRate = f" (预测胜率: {predictRates.get(str(TeamId), ''):.2%})" if server == 'jp' and str(TeamId) in predictRates else ""
            text += team['teamName'] + translate + " " + str(memberCount) + '人' + predictRate + '\n'
    if predictRates:
        text += timestamp_str
    return text if text != '' else '没有5v5捏'


def getqqbind(qqnum, server):
    mydb = pymysql.connect(host=host, port=port, user='pjsk', password=password,
                           database='pjsk', charset='utf8mb4')
    mycursor = mydb.cursor()
    if server == 'jp':
        mycursor.execute('SELECT * from bind where qqnum=%s', (qqnum,))
    elif server == 'tw':
        mycursor.execute('SELECT * from twbind where qqnum=%s', (qqnum,))
    elif server == 'en':
        mycursor.execute('SELECT * from enbind where qqnum=%s', (qqnum,))
    elif server == 'kr':
        mycursor.execute('SELECT * from krbind where qqnum=%s', (qqnum,))
    mycursor.close()
    mydb.close()
    data = mycursor.fetchone()
    try:
        return data[1:]
    except:
        return None

def getIdOwner(userid, server):
    mydb = pymysql.connect(host=host, port=port, user='pjsk', password=password,
                           database='pjsk', charset='utf8mb4')
    mycursor = mydb.cursor()
    if server == 'jp':
        mycursor.execute('SELECT * from bind where userid=%s', (userid,))
    elif server == 'tw':
        mycursor.execute('SELECT * from twbind where userid=%s', (userid,))
    elif server == 'en':
        mycursor.execute('SELECT * from enbind where userid=%s', (userid,))
    elif server == 'kr':
        mycursor.execute('SELECT * from krbind where userid=%s', (userid,))
    mycursor.close()
    mydb.close()
    data = mycursor.fetchall()
    if data is not None:
        return ','.join([raw[1] for raw in data])
    return ''


def bindid(qqnum, userid, server):
    if not verifyid(userid, server):
        return '你这ID有问题啊'
    mydb = pymysql.connect(host=host, port=port, user='pjsk', password=password,
        database='pjsk', charset='utf8mb4')
    mycursor = mydb.cursor()

    if server == 'jp':
        sqlname = 'bind'
    elif server == 'tw':
        sqlname = 'twbind'
    elif server == 'en':
        sqlname = 'enbind'
    elif server == 'kr':
        sqlname = 'krbind'

    sql = f"insert into {sqlname} (qqnum, userid, isprivate) values (%s, %s, %s) " \
          f"on duplicate key update userid=%s"
    val = (str(qqnum), str(userid), 0, str(userid))
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    mydb.close()
    return "绑定成功！\n请不要以任何目的绑定挂哥账号，这可能导致你的qq被bot拉黑（如果你在正常绑定自己的账号请忽略该提示）"

def setprivate(qqnum, isprivate, server):
    if server == 'jp':
        server = ''
    mydb = pymysql.connect(host=host, port=port, user='pjsk', password=password,
                           database='pjsk', charset='utf8mb4')
    mycursor = mydb.cursor()
    mycursor.execute(f'UPDATE {server}bind SET isprivate=%s WHERE qqnum=%s', (isprivate, qqnum))
    mydb.commit()
    mycursor.close()
    mydb.close()
    return True
