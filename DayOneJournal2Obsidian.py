import datetime
import dateutil.parser
import json
import pytz  # pip install pytz
import re
import os
import sys
import shutil
import time
from include.FindMovieInfo import get_movie_info


# Set this as the location where your Journal.json file is located
root = r"/Users/chishum/PycharmProjects/toy-project/dayone/Movie"
icons = True  # Set to true if you are using the Icons Plugin in Obsidian
# tagPrefix = "Movie/"  # This will append journal/ as part of the tag name for sub-tags ie. instead of #entry, it is #journal/entry. To exclude set to "". If you change journal to something else, make sure you keep the trailing /

journalFolder = os.path.join(root, "Movie2")  # name of folder where journal entries will end up
fn = os.path.join(root, "Movie.json")

# Clean out existing journal folder, otherwise each run creates new files
if os.path.isdir(journalFolder):
    print("Deleting existing folder: %s" % journalFolder)
    shutil.rmtree(journalFolder)

time.sleep(2)
# Give time for folder deletion to complete. Only a problem if you have the folder open when trying to run the script
if not os.path.isdir(journalFolder):
    print("Creating journal folder: %s" % journalFolder)
    os.mkdir(journalFolder)

if icons:
    print("Icons are on")
    dateIcon = "`fas:CalendarAlt` "
else:
    print("Icons are off")
    dateIcon = ""  # make 2nd level heading

print("Begin processing entries")
count = 0
with open(fn, encoding='utf-8') as json_file:
    data = json.load(json_file)
    for entry in data['entries']:
        prop = {}
        create_date = dateutil.parser.isoparse(entry['creationDate'])
        watch_date = create_date.strftime('%Y-%m-%d')
        prop['watch_date'] = watch_date

        try:
            newText = entry['text'].replace("\\", "")
            newText = newText.replace("\u2028", "\n")
            newText = newText.replace("\u1C6A", "\n\n")

            listText = newText.split("\n")

            review = ""
            i = -1
            first_line = True
            for t in listText:
                i += 1

                # 제목 추출
                if i == 0:
                    t = re.sub("^#+ ", "", t)
                    prop['title'] = t[:-6].strip()
                    prop['prod_year'] = t[-4:]
                    continue

                if t.startswith("![](dayone-moment:"):
                    if 'photos' in entry:
                        # Correct photo links. First we need to rename them. The filename is the md5 code, not the identifier
                        # subsequently used in the text. Then we can amend the text to match. Will only to rename on first run                # through as then, they are all renamed.                # Assuming all jpeg extensions.
                        for p in entry['photos']:
                            pfn = os.path.join(root, 'photos', f'{p['md5']}.{p['type']}')
                            if os.path.isfile(pfn):
                                newfn = os.path.join(root, 'photos', f'{p['identifier']}.{p['type']}')
                                os.rename(pfn, newfn)

                            prop['poster'] = f"{p['identifier']}.{p['type']}"
                    continue

                if first_line:
                    first_line = False
                    if t == "":
                        continue

                review += t + "\n"
        except KeyError:
            pass

        prop['review'] = review[2:] if review.startswith("# ") else review

        tags = []
        if 'tags' in entry:
            tags = []
            for t in entry['tags']:
                tags.append(t.replace(' ', '-').replace('---', '-'))
        prop['tags'] = tags

        # Save entries organised by year, year-month, year-month-day.md
        yearDir = os.path.join(journalFolder, str(create_date.year))

        if not os.path.isdir(yearDir):
            os.mkdir(yearDir)

        # Target filename to save to. Will be modified if already exists
        fnNew = os.path.join(yearDir, f"{prop['title']}, {prop['prod_year']}.md")

        # 다른 정보 얻기
        prop['query'] = prop['title']
        attr = get_movie_info(prop)

        print(prop)
        print(attr)

        with open(fnNew, 'w', encoding='utf-8') as f:
            poster = prop['poster'] if prop.get('poster') else attr.get("poster")
            poster = "" if poster is None else poster

            f.write("---\n")
            f.write("title: '" + prop['title'] + "'\n")
            f.write("prod_year: '" + prop['prod_year'] + "'\n")
            f.write("directors: [" + ','.join(attr.get('directors')) + "]\n")
            f.write("actors: [" + ','.join(attr.get('actors')) + "]\n")
            f.write("nation: '" + attr.get("nation") + "'\n")
            f.write("runtime: " + attr.get("runtime") + "\n")
            f.write("genre: '" + attr.get("genre") + "'\n")
            f.write("kmdb_url: " + attr.get("kmdb_url") + "\n")
            f.write("type: '" + attr.get("type") + "'\n")
            f.write("poster: '" + poster + "'\n")
            f.write("watch_date: " + prop.get('watch_date') + "\n")
            f.write("tags: [" + ','.join([x for x in prop.get('tags')]) + "]\n")
            f.write("---\n")

            f.write("## 포스터\n")
            if poster != "":
                f.write("![[" + poster + "]]\n")
            f.write("## 줄거리\n")
            f.write(attr.get('plot') + "\n")
            f.write("## 간단 리뷰\n")
            for line in prop['review'].split("\n"):
                f.write(line+"\n")

        count += 1

        print("Complete: %d entries processed." % count)
