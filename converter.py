#!/usr/bin/python3

import os
import re
import sys
from datetime import datetime

def main():
    records = []

    if len(sys.argv) == 1:
        print("Wrong arguments!")
        return

    regex = re.compile('^"[0-9]*","[0-9,\-,:,\s]+",.*')
    lastLine = ""
    for arg in range(1, len(sys.argv)):
        with open(sys.argv[arg], "rt", encoding="iso-8859-1") as f:
            for line in f:
                if regex.match(line) and lastLine:
                    records.append(lastLine.strip()[1:-1].split('","'))
                    lastLine = ""
                lastLine += line

            if lastLine:
                records.append(lastLine[1:-1].split('","'))

    data = {}
    for record in records:
        if not record[0]:
            try:
                data[int(record[2])] = {
                    "timestamp": datetime.strptime(record[1], "%d-%m-%Y %H:%M:%S"),
                    "timestamp_str": record[1],
                    "title": record[3],
                    "content": record[4],
                    "messages": []
                }
            except Exception as e:
                print("Error on ", record)
                return

    for record in records:
        if record[0] and int(record[0]) in data:
            try:
                data[int(record[0])]["messages"].append({
                    "sequence": int(record[2]),
                    "timestamp": datetime.strptime(record[1], "%d-%m-%Y %H:%M:%S"),
                    "timestamp_str": record[1],
                    "user": record[3],
                    "message": record[5]
                })
                lastValue = record[1]
            except Exception as e:
                print("Error on ", record)
                return

    toc = []
    for itemKey in data:
        rootPath = os.path.join("%02d" % data[itemKey]["timestamp"].year, "%02d" % data[itemKey]["timestamp"].month)
        os.makedirs(rootPath, exist_ok=True)

        htmlFile = "%s.html" % os.path.join(rootPath, "%02d_%02d_%02d_%02d" % (data[itemKey]["timestamp"].day, data[itemKey]["timestamp"].hour, data[itemKey]["timestamp"].minute, data[itemKey]["timestamp"].second))

        toc.append({
            "timestamp_str": data[itemKey]["timestamp_str"],
            "timestamp": data[itemKey]["timestamp"],
            "title": data[itemKey]["title"],
            "file": htmlFile
        })

        with open(htmlFile, "w") as f:
            messages = data[itemKey]["messages"]
            messages.sort(key=lambda x: x["sequence"])

            f.write("<html><head><title>%s</title></head><body><h1>%s</h1><br>posted on: %s<br><br><table border=\"0\"><tr><td colspan=\"2\">%s</td></tr>" % (data[itemKey]["title"], data[itemKey]["title"], data[itemKey]["timestamp_str"], data[itemKey]["content"].replace("<tick>", "'").replace("\\n", "")))
            for message in messages:
                f.write("<tr><td colspan=\"2\"><b>%s</b> wrote on %s:</td></tr><tr><td>&nbsp;</td><td>%s</td></tr>" % (message["user"], message["timestamp_str"], message["message"].replace("\\n", "")))
            f.write("</table></body></html>")

    toc.sort(key=lambda x: x["timestamp"])

    with open("toc.html", "w") as f:
        f.write("<html><head><title>Table of content</title></head><body><table border=\"0\">")

        for item in toc:
            f.write("<tr><td>%s</td><td><a href=\"%s\" target=\"_blank\">%s</a></td></tr>" % (item["timestamp_str"], item["file"], item["title"]))

        f.write("</table></body></html>")

main()