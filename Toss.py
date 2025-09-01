import requests
from requests import post
from bs4 import BeautifulSoup, Tag, NavigableString
import sqlite3
import re
import telegram
import asyncio
#from telegram.constants import ParseMode
from datetime import datetime, date


def trace(msg):
    """
        메시지 앞에 시간 정보를 출력
        :param msg:
    """
    print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg)

def get_quiz(link):
    """
        link로부터 토스 퀴즈와 정답을 추출
        :param link: bntnews 사이트
        :return: NOT_TOSS, NOT_TODAY, OK
    """
    quiz_res = requests.get("https://www.bntnews.co.kr" + link)
    if quiz_res.status_code == 200:
        quiz_soup = BeautifulSoup(quiz_res.text, 'html.parser')

        date_text = quiz_soup.select_one('#wrap_index > main > div > div:nth-child(1) > div > div.info_wrap > div.date')
        dd = date_text.text[0:10]
        if dd != date.today().strftime("%Y-%m-%d"):
            trace(f"퀴즈 날짜가 오늘이 아닙니다. {dd}")
            return "NOT_TODAY"

        title = quiz_soup.select_one('#wrap_index > main > div > div:nth-child(1) > div > div.title_wrap > h1')
        if title.text.find("토스") < 0:
            trace(f"토스 행운 퀴즈가 아닙니다. {title.text}")
            return "NOT_TOSS"

        quiz_content = quiz_soup.select_one('#wrap_index > main > div > div:nth-child(1) > div > div.din.din2-12.view_din > div:nth-child(2) > div.box.body_wrap > div.content')
        strongs = quiz_content.select('strong')

        i = 0
        quiz_name = ""
        quiz = {}
        for s in strongs:
            target = s.text
            if target.find("정답 - ") >= 0:
                if len(s.contents) == 1:
                    quiz[quiz_name] = target
                    quiz_name = ""
                else:
                    for c in s.contents:
                        if isinstance(c, NavigableString):
                            if c == '\xa0': continue

                            if quiz_name == "":
                                quiz_name = c
                            else:
                                quiz[quiz_name] = c
                                quiz_name = ""
            else:
                quiz_name = target

        for k in quiz.keys():
            trace(f"{dd} [{k}]: {quiz[k]}")
            db_write(dd, k, quiz[k])
    else:
        trace(f"get_quiz: {quiz_res.status_code}")
        return "NOT_OK"

    return "OK"

def create_db():
    """
        toss 테이블을 생성
    """
    connection = sqlite3.connect("toss/toss.db")
    cursor = connection.cursor()

    sql = "SELECT COUNT(*) FROM sqlite_master WHERE Name = 'toss';"
    cursor.execute(sql)
    toss_table_cnt = cursor.fetchone()

    if toss_table_cnt[0] == 0:
        sql = """  
            CREATE TABLE toss (
	            dd varchar(10) not null,
	            quiz_name varchar(250) not null,
	            quiz_answer varchar(250) not null,
	            create_dt DATETIME DEFAULT (DATETIME('now', 'localtime')),
	            CONSTRAINT UQ_dd_01 UNIQUE(dd, quiz_name)
	        );
	    """
        cursor.execute(sql)

    connection.close()

def db_write(dd, quiz_name, quiz_answer):
    """
    토스 문제와 정답을 toss 테이블에 기록
    :param dd:
    :param quiz_name:
    :param quiz_answer:
    """
    connection = sqlite3.connect("toss/toss.db")
    cursor = connection.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM toss WHERE dd = ? AND quiz_name = ?", [dd, quiz_name])
    event_cnt = cursor.fetchone()

    if event_cnt[0] == 0:
        cursor.execute(f"INSERT INTO toss(dd, quiz_name, quiz_answer) VALUES (?, ?, ?);", [dd, quiz_name, quiz_answer])
        connection.commit()

        # 텔레그램 전송
        send_telegram(f"*{quiz_answer}*\n{quiz_name}\n*{dd}*")

    connection.close()

def send_telegram(msg):
    """
    텔레그램에 문제와 정답 전송
    :param msg:
    """
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = '7940697546:AAGqx4au-RC0AyDXDUJPge0jBMVKb5PUGu8'

    # Replace 'CHAT_ID' with the ID of the chat you want to send the MP3 to
    chat_id = '-1002664272481'

    asyncio.run(send_message(bot_token, chat_id, msg))

def check_quiz(count):
    """
    bntnews 사이트에서 토스 행운퀴즈 링크를 추출
    :param count: 재실행 횟수
    :return:
    """
    if count == 0: return

    res = requests.get("https://www.bntnews.co.kr/article/search?searchText=%ED%86%A0%EC%8A%A4+%ED%96%89%EC%9A%B4%ED%80%B4%EC%A6%88",
                       headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        quiz_list = soup.select_one('#list')
        for article in quiz_list.contents:
            if isinstance(article, Tag):
                ret = get_quiz(article.select('a')[0].attrs['href'])
                if ret == "OK" or ret == "NOT_TODAY": return
    else:
        trace(f"check_quiz: {res.status_code}")
        count -= 1
        check_quiz(count)


if __name__ == '__main__':
    create_db()

    async def send_message(bot_token, chat_id, msg):
        bot = telegram.Bot(token=bot_token)
        async with bot:
            await bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

    check_quiz(5)
