import requests
from requests import get
import json
import datetime as dt
from datetime import datetime
import os
import sys
import shutil
from telethon import TelegramClient
import telegram
#from telegram.constants import ParseMode
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from sys import argv, stderr, exit
import eyed3

target_dd = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now().strftime("%Y%m%d")

def trace(msg):
    """
        메시지 앞에 시간 정보를 출력
        :param msg:
    """
    print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg)

def download(url, file_name):
    with open(file_name, "wb") as file:  # open in binary mode
        response = get(url)

        if response.status_code == 404:
            return False

        file.write(response.content)
        return True

def mime_type_check(file_name):
    parser = createParser(file_name)
    if not parser:
        print("Unable to parse file", file=stderr)
        exit(1)

    with parser:
        try:
            metadata = extractMetadata(parser)
        except Exception as err:
            print("Metadata extraction error: %s" % err)
            metadata = None
    if not metadata:
        print("Unable to extract metadata")
        exit(1)

    for line in metadata.exportPlaintext():
        print(line)

def set_tag(file_name, down_dd):
    """
    mp3 tag 설정
    :param file_name:
    :param down_dd:
    """
    news_tag = eyed3.load(file_name)
    if news_tag.tag is None: news_tag.initTag()

    weekday_dict = {0: '월', 1: '화', 2: '수', 3: '목', 4: '금', 5: '토', 6: '일'}
    dd = datetime.strptime(down_dd, "%Y-%m-%d")

    news_tag.tag.artist = "JTBC 뉴스룸"
    news_tag.tag.title = f"{down_dd} ({weekday_dict[dd.weekday()]})"
    news_tag.tag.save()

if __name__ == '__main__':
    trace("START")
    res = requests.get(f"https://news-api.jtbc.co.kr/v1/get/contents/program/aod-list?programIdx=NG10000002&searchDate={target_dd}")
    down_dd = res.json()["data"][0]['insertDate'][0:10]
    trace(res.json()["data"][0]['audioUrl'])
    os.chdir(f"/Users/chishum/PycharmProjects/toy-project")

    if not os.path.exists(f"./newsRoom"): os.mkdir(f"./newsRoom")

    news_room_file = f"newsRoom/{down_dd}-뉴스룸.mp3"
    trace(news_room_file)
    download(res.json()["data"][0]['audioUrl'], news_room_file)
    set_tag(news_room_file, down_dd)
    trace(f"tag처리 {news_room_file}")

    #Use your own values from my.telegram.org
    # api_id = 29192735
    # api_hash = '7da4edb11c97edbc89aca3a033fcb66d'
    # client = TelegramClient('anon', api_id, api_hash)
    #
    # async def main():
    #     # Getting information about yourself
    #     # me = await client.get_me()
    #
    #     # "me" is a user object. You can pretty-print
    #     # any Telegram object with the "stringify" method:
    #     # print(me.stringify())
    #
    #     # When you print something, you see a representation of it.
    #     # You can access all attributes of Telegram objects with
    #     # the dot operator. For example, to get the username:
    #     # username = me.username
    #     # print(username)
    #     # print(me.phone)
    #
    #     # You can print all the dialogs/conversations that you are part of:
    #     # async for dialog in client.iter_dialogs():
    #     #     print(dialog.name, 'has ID', dialog.id)
    #
    #     # You can send messages to yourself...
    #     # await client.send_message('me', 'Hello, myself!')
    #     # ...to some chat ID
    #     # await client.send_message(-1001293981836, 'Hello, group!')
    #     # ...to your contacts
    #     #await client.send_message('+34600123123', 'Hello, friend!')
    #     # ...or even to any username
    #     #await client.send_message('username', 'Testing Telethon!')
    #
    #     # Or send files, songs, documents, albums...
    #     trace("TELEGRAM 전송시작")
    #     await client.send_file(-1002377578524, news_room_file, parse_mode="html")
    #     trace("END")
    #
    # with client:
    #     client.loop.run_until_complete(main())