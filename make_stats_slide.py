#! /usr/bin/env python3

import json
import sys
import getopt
import subprocess
import parse_data # helper script

def manage_files():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"d:o:c:",["datafile=", "outputfile=", "config="])
    except getopt.GetoptError:
        print ('program.py -d <datafile> -o <output> -c <config>')
        sys.exit(2)

    dname = ""
    oname = ""
    cname = ""

    for opt, arg in opts:
        if opt in ("-d", "--datafile"):
            dname = arg
        if opt in ("-o", "--outputfile"):
            oname = arg
        if opt in ("-c", "--configfile"):
            cname = arg

    page = parse_data.get_json_file(dname)

    with open(cname, 'r') as fcc_file:
        config = json.load(fcc_file)

    return(page, config, oname)
    
# to run:
#   % ./make_stats_slide.py -d scrap.json -c config.json -o out4.mp4
# This grabs information from data, and from the config file
#   to create two still images, one with title and the other with stats. 
#   then it uses two pics fades them in and out to create a movie

def main():
    (page, config, output_file) = manage_files()

    blob = parse_data.load_get_response(page['blob'])
    values = ('curr_max', 'fw_curr', 'fw_ehz', 'i_max', 'p_max')

    tmp_file1 = output_file + '_1.png'
    tmp_file2 = output_file + '_2.png'

    str = ""
    str = 'convert -background black -fill yellow  -size {0} -pointsize 60 -gravity Center label:\"{1}\" {2}'.format(config['movie_size'], config['movie_title'], tmp_file1)

    print("RUNNING: " + str)
    cp = subprocess.run([str], shell=True)

    caption = ""
    for v in values:
        e = blob[v]
        e['desc'] = e['desc'].replace('weakenning', 'weakening')
        e['desc'] = e['desc'].replace('eHz under field weakening', 'field weakening eHz')
        e['desc'] = e['desc'].replace('max', 'Max')

        caption = caption + ('{} = {:d} ({})').format(e['desc'], int(float(e['value'])), v) + "\\n"

    caption = "\"" + caption + "\""

    str = 'convert -background black -fill yellow  -size {0} -pointsize 30 -gravity Center label:{1} {2}'.format(config['movie_size'], caption, tmp_file2)

    print("RUNNING: " + str)
    
    cp = subprocess.run([str], shell=True)

    str = 'ffmpeg -loop 1 -t 5 -i  {0} -loop 1 -t 5 -i {1} -filter_complex \"[0:v]fade=t=out:st=4:d=1[v0]; [1:v]fade=t=in:st=0:d=1,fade=t=out:st=4:d=1[v1]; [v0][v1]concat=n=2:v=1:a=0,format=yuv420p[v]\" -map \"[v]\" {2}.mp4'.format(tmp_file1, tmp_file2, output_file)

    print("RUNNING: " + str)
    cp = subprocess.run([str], shell=True)

if __name__ == "__main__":
    main()







