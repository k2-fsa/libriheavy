import gzip
import json
import re
import sys

selected_speakers = set()
with open("v1/selected_speakers.txt", "r") as f:
    for line in f:
        selected_speakers.add(line.strip())
selected_books = set()
with open("v1/selected_books.txt", "r") as f:
    for line in f:
        selected_books.add(line.strip())

ifile = gzip.open(sys.argv[1],"r")
kfile = gzip.open(sys.argv[2], "w")
tfile = gzip.open(sys.argv[3], "w")

for lines in ifile:
    line = json.loads(lines)
    speaker = line["id"].split("/")[1]
    book = line["custom"]["text_path"].split("/")[-2]
    if book in selected_books or speaker in selected_speakers:
        tfile.write(lines)
    else:
        kfile.write(lines)
ifile.close()
kfile.close()
tfile.close()

