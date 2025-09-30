import requests
from requests import get
import os
import urllib.request
import urllib.parse
from settings import MySetting


def download_poster(url, file_name):
    os.chdir("/Users/chishum/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Attatchments")
    with open(file_name, "wb") as file:  # open in binary mode
        response = get(url)

        if response.status_code == 404:
            return False

        file.write(response.content)
        return True

def get_movie_info(prop):
    query = prop['query']
    # print(prop)
    service_key = MySetting.KMDB_SERVICE_KEY
    if prop.get("movieSeq"):
        res = requests.get(f"http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=Y&ServiceKey={service_key}&sort=prodYear,1&movieId={prop['movieId']}&movieSeq={prop['movieSeq']}")
    else:
        res = requests.get(f"http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=Y&ServiceKey={service_key}&sort=prodYear,1&query={urllib.parse.quote(query)}")
    # print(res.json())

    attr = {
        "poster" : "",
        "title" : "",
        "prod_year" : "",
        "directors" : [],
        "actors" : [],
        "nation" : "",
        "runtime" : "",
        "genre" : "",
        "kmdb_url" : "",
        "type" : "",
        "plot" : ""
    }

    if res.json()["TotalCount"] > 0 and res.json()["Data"][0]["Result"][0]:
        r = res.json()["Data"][0]["Result"][0]
        title = r['title'].replace(" !HS ","").replace(" !HE ","").strip()
        # 포스터 로컬 다운로드
        if (prop.get("poster") is None or prop.get("poster") == "") and r["posters"] > "":
            posterFileNm = title.replace(" ", "_") + "_" + r["prodYear"] + ".jpg"
            download_poster(r["posters"].split("|", 1)[0], posterFileNm)
            attr["poster"] = posterFileNm

        attr["title"] = title
        attr["prod_year"] = prop.get("prod_year") if prop.get("prod_year") else r["prodYear"]
        attr["directors"] = [x['directorNm'] for x in r["directors"]['director']]
        attr["actors"] = [x['actorNm'] for x in r["actors"]['actor'][:4]]
        attr["nation"] = r["nation"]
        attr["runtime"] = r["runtime"]
        attr["genre"] = r["genre"]
        attr["kmdb_url"] = r["kmdbUrl"]
        attr["type"] = r["type"]
        attr["plot"] = r['plots']['plot'][0]['plotText']

    return attr
