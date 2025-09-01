import requests
from requests import get
import json
import datetime as dt
from datetime import datetime
from pydub import AudioSegment
import os
import sys
import shutil
from telethon import TelegramClient
import eyed3
import requests
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


targetDd = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now().strftime("%Y%m%d")
targetMm = targetDd[0:6]
resultFile = f"{targetDd}.mp3"
weekday_dict = {0: '월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}

def trace(msg):
    print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg)

def init():
    trace(f"[{targetMm}/{targetDd}] 작업 시작")

    # 폴더 정리
    if not os.path.exists(f"./english/{targetMm}"): os.mkdir(f"./english/{targetMm}")
    if os.path.exists(f"./english/{targetMm}/{targetDd}"): shutil.rmtree(f"./english/{targetMm}/{targetDd}")
    os.mkdir(f"./english/{targetMm}/{targetDd}")
    os.chdir(f"./english/{targetMm}/{targetDd}")

def naver_file_search():
    for i in range(2, 20):
        file_name = f"{targetDd}_{i:02d}.mp3"
        res = requests.get(
            f"https://learn.dict.naver.com/dictPronunciation.dict?filePaths=/wordbook/mew/sentence/{file_name}")
        data = json.loads(res.content)
        if not download(data['url'][0], f"./{file_name}"):
            break

def zero_length_file_clear():
    for file in os.listdir("."):
        if os.path.getsize(file) == 0: os.remove(file)

def download(url, file_name):
    with open(file_name, "wb") as file:  # open in binary mode
        response = get(url)

        if response.status_code == 404:
            return False

        file.write(response.content)
        return True

def merge_full():
    result = None
    silence = AudioSegment.silent(duration=500)

    for file in sorted(os.listdir(".")):
        if not file.endswith("mp3"): continue
        if file == resultFile: continue

        if result is None:
            result = AudioSegment.from_mp3(file) + silence
        else:
            f_to_add = AudioSegment.from_mp3(file)
            result += f_to_add + silence

    for i in range(2): result += result + silence

    result.export(resultFile, format="mp3")

def merge_each():
    result = AudioSegment.from_mp3(resultFile)
    silence = AudioSegment.silent(duration=500)

    for file in sorted(os.listdir(".")):
        if not file.endswith("mp3"): continue
        if file == resultFile: continue

        f_to_add = AudioSegment.from_mp3(file)
        for i in range(4): result += f_to_add + silence

    result.export(resultFile, format="mp3")

def merge_10_times():
    result = AudioSegment.from_mp3(resultFile)

    for file in sorted(os.listdir(".")):
        if not file.endswith("mp3"): continue
        if file == resultFile: continue

        f_to_add = AudioSegment.from_mp3(file)
        duration = f_to_add.duration_seconds * 1000 * 1.1
        for i in range(10): result += f_to_add + AudioSegment.silent(duration=duration)

    result.export(resultFile, format="mp3")

def set_tag():
    fileTag = eyed3.load(resultFile)
    if fileTag.tag is None: fileTag.initTag()

    dd = datetime.strptime(targetDd, "%Y%m%d")
    fileTag.tag.artist = "NAVER 영어회화"
    fileTag.tag.title = f"{dd.strftime('%Y-%m-%d')} ({weekday_dict[dd.weekday()]})"
    fileTag.tag.album = dd.strftime('%Y-%m')
    fileTag.tag.save()

if __name__ == '__main__':
    init()
    naver_file_search()
    zero_length_file_clear()

    # 일요일은 쉰덴다
    if len(os.listdir(".")) == 0:
        shutil.rmtree(f"../{targetDd}")
        trace(f"[{targetDd}]은 파일이 없습니다.")
        exit(0)

    merge_full()  # 연속 재생
    merge_each()  # 각각 재생
    merge_10_times()  # 10번 따라하기

    # tag 설정
    set_tag()

    # Month 폴더로 이동
    shutil.copy2(f"./{resultFile}", f"../../{targetMm}/{resultFile}")

    # Telegram에 업로드
    os.chdir("../../..")
    #Use your own values from my.telegram.org
    api_id = 29192735
    api_hash = '7da4edb11c97edbc89aca3a033fcb66d'
    client = TelegramClient('anon', api_id, api_hash)

    async def main():
        trace(f"[{targetDd}] TELEGRAM 전송시작")
        await client.send_file(-1002377578524, f"english/{targetMm}/{resultFile}", parse_mode="html")
        trace(f"[{targetDd}] TELEGRAM 전송완료")
    with client:
        client.loop.run_until_complete(main())

    trace(f"[{targetDd}] 작업완료")
