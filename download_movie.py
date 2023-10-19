#! /usr/bin/env python3

import getopt, sys, json
from pytube import YouTube 

try:
    opts, args = getopt.getopt(sys.argv[1:],"c:o:",["config=", "output="])
except getopt.GetoptError:
    print ('program.py -c <config> -o <outputfile>')
    sys.exit(2)

cname = ""
oname = ""

for opt, arg in opts:
    if opt in ("-c", "--config"):
        cname = arg
    if opt in ("-o", "--output"):
        oname = arg

with open(cname, 'r') as fcc_file:
    config = json.load(fcc_file)

link = config['movie_URL']

try:

    print(("attempting download of: {} to {}").format(link, oname))
    yt = YouTube(link)
    mp4_files = yt.streams.filter(file_extension="mp4")
    mp4_720p_files = mp4_files.get_by_resolution("720p")
    mp4_720p_files.download(filename=oname)

except Exception as e: 
    print("ERROR: ", e)
