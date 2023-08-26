from abc import abstractmethod, ABC
from typing import List
from dataclasses import dataclass

import json
import random
import requests
import time


@dataclass
class Song:
    docid: str
    id: str
    mid: str
    name: str
    singer: str


class MusicInterface(ABC):
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.5; Win64; x64) AppleWebKit/547.36 (KHTML, like Gecko) Chrome/86.0.4280.66 Safari/537.36"
        }

    @abstractmethod
    def getSongInformation(self, music_name) -> List[Song]:
        """
        获取音乐列表
        :param music_name:
        :return:
        """
        pass

    @abstractmethod
    def getSongDownload(self, song: Song):
        pass

    @abstractmethod
    def convert_xml(self, song: Song):
        pass


class QQMusic(MusicInterface):

    def getSongDownload(self, song):
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        params = {
            '_': time.time() * 1000,
            'sign': 'zzakgej75pk8w36d82032784bdb9204d99bf6351acb7d',
            "data": '{"req":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"7469768631","songmid":["' + song.mid + '"],"songtype":[0],"uin":"1164153961","loginflag":1,"platform":"20"}}}'
        }
        response = self.session.get(url, params=params)
        data = json.loads(response.text)
        dataPro = data["req"]["data"]["midurlinfo"][0]

        songmid = dataPro["songmid"]
        filename = dataPro["filename"]
        vkey = dataPro["vkey"]
        purl = dataPro["purl"]
        audio = "http://dl.stream.qqmusic.qq.com/" + dataPro["purl"]

        result = {
            "dlSongMid": songmid,
            "dlFilename": filename,
            "dlVKey": vkey,
            "dlPurl": purl,
            "dlAudio": audio,
        }
        return result

    def getSongInformation(self, music_name):
        url = "https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg"
        params = {
            '_': int(time.mktime(time.localtime())) + random.randint(100, 900),
            'cv': '4747474',
            'ct': '24',
            'format': 'json',
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'notice': '0',
            'platform': 'yqq.json',
            'needNewCode': '1',
            'uin': '0',
            'g_tk_new_20200303': '5381',
            'g_tk': '5381',
            'hostUin': '0',
            'is_xml': '0',
            'key': music_name,
        }
        self.session.headers["Referer"] = 'http://y.qq.com'
        res = self.session.get(url, params=params)

        res_json = json.loads(res.text)

        data = res_json["data"]

        # mv
        # count     数量
        # itemlist  列表(docid, id, mid, name, singer, vid)
        mv = data["mv"]

        # 歌手&&歌曲&&专辑
        # count     数量
        # itemlist  列表(docid, id, mid, name, pic, singer)
        album = data["album"]
        singer = data["singer"]
        song = data["song"]

        if int(song["count"]) == 0:
            return False

        l = []
        for i in song["itemlist"]:
            l.append(Song(i["docid"], i["id"], i["mid"], i["name"], i["singer"]))
        return l

    def convert_xml(self, song):
        data = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><msg serviceID="2" templateID="1" action="web" brief="&#91;分享&#93; [title]" sourceMsgId="0" url="[url]" flag="0" adverSign="0" multiMsgFlag="0" ><item layout="2"><audio cover="[pic]" src="[audio]" /><title>[title]</title><summary>[singer]</summary></item><source name="QQ音乐" icon="https://i.gtimg.cn/open/app_icon/01/07/98/56/1101079856_100_m.png" url="http://web.p.qq.com/qqmpmobile/aio/app.html?id=1101079856" action="app"  a_actionData="com.tencent.qqmusic" i_actionData="tencent1101079856://" appid="1101079856" /></msg>'''
        data = data.replace("[singer]", "musicSinger")
        data = data.replace("[url]", "musicUrl")
        data = data.replace("[audio]", "musicAudio")
        data = data.replace("[title]", "musicName")
        data = data.replace("[pic]", "musicPic")
        return "[CQ:xml,data=%s]" % data


if __name__ == "__main__":
    music = QQMusic()
    items = music.getSongInformation("单车")
    print(items)
    for i in items:
        print(music.getSongDownload(i))
