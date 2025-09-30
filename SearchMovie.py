from os import remove
from include.FindMovieInfo import get_movie_info
import requests
from requests import get
from datetime import date
import os
import sys
import urllib.request
import urllib.parse
import pyclip

if __name__ == '__main__':
    # print(sys.argv)
    kmdb_url =  pyclip.paste(text=True).split("/")
    #print(kmdb_url)
    movie_id = ""
    movie_seq = ""
    if len(kmdb_url) > 6:
        movie_id = kmdb_url[7]
        movie_seq = kmdb_url[8]
    title = sys.argv[1] if len(sys.argv) > 1 else ""

    #title = urllib.parse.quote(pyclip.paste().decode('utf-8'))
    #title = urllib.parse.quote("원더풀 라디오")
    param = {"query": pyclip.paste(text=True), "movieId": movie_id, "movieSeq": movie_seq}
    #print(param)
    #exit(0)

    attr = get_movie_info(param)
    # print(attr)

    movieInfo = ""
    if attr:
        prop = "---\n"
        prop += "title: '" + attr["title"] + "'\n"
        prop += "prod_year: " + attr["prod_year"] + "\n"
        prop += "directors: [" + ','.join(attr['directors']).replace(" !HS ","").replace(" !HE ","") + "]\n"
        prop += "actors: [" + ','.join(attr['actors']).replace(" !HS ","").replace(" !HE ","") + "]\n"
        prop += "nation: '" + attr["nation"] + "'\n"
        prop += "runtime: " + attr["runtime"] + "\n"
        prop += "genre: '" + attr["genre"] + "'\n"
        prop += "kmdb_url: " + attr["kmdb_url"] + "\n"
        prop += "type: '" + attr["type"] + "'\n"
        prop += "poster: '" + attr.get('poster') + "'\n"
        prop += "watch_date: " + date.today().strftime("%Y-%m-%d") + "\n"

        prop += "---\n"

        movieInfo += prop
        movieInfo += "## 포스터\n"
        if attr.get('poster') != "":
            movieInfo += "![["+ attr.get('poster') + "]]\n"
        movieInfo += "## 줄거리\n"
        movieInfo += attr['plot'] + "\n"
        movieInfo += "## 간단 리뷰\n"

    pyclip.copy(movieInfo)
