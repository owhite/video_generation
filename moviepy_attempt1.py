#! /usr/bin/env python3

import moviepy.editor as mp

import sys, getopt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import parse_data # helper script

# {"adc1":740,"ehz":0.161,"error":0,"id":0.197,"iq":0.094,"iqreq":0.000,"TMOS":0.000,"TMOT":0.000,"vbus":72.481,"Vd":1.928,"Vq":0.586},

try:
    opts, args = getopt.getopt(sys.argv[1:],"i:",["ifile="])
except getopt.GetoptError:
    print ('program.py -i <inputfile>')
    sys.exit(2)

fname = ""

for opt, arg in opts:
    if opt in ("-i", "--infile"):
        fname = arg

the_page = parse_data.get_json_file(fname)
title = the_page['title']

data = parse_data.make_frame(the_page['data'])
df = pd.DataFrame(data)
df_scaled = df.copy()

df['phaseA'] = np.sqrt( (df['id'] * df['id']) + (df['iq'] * df['iq']) )

y = the_page['bar_displays']
for item in the_page['bar_displays']:
    max = the_page['max_vals'][item]
    min = the_page['min_vals'][item]
    df_scaled[item] = (df[item] - min) / (max - min) 

data_max_vals = df.max(axis = 0)

data_length = len(df) - 1

bar_width = .8

y = the_page['bar_displays']

video = mp.VideoFileClip("druid_hill_climb2.mp4")

inserts = [video]
time_point = 0
time_inc = 0.1
files = []

for row in list(range(data_length)):
    count = 0
    labels = []
    names = []
    values = []
    widths = []
    for item in the_page['bar_displays']:
        if the_page['bar_displays'][item]:
            widths.append(bar_width)
            names.append(item)
            values.append(df_scaled[item][row])
            labels.append(int(df[item][row]))
            count = count + 1

        fig, ax = plt.subplots(figsize=(2,3))
        ax.bar(names, values, width = widths)
        ax.set(ylabel='', title='', ylim=(0, 1))
        ax.set_axis_off()

    rects = ax.patches
    count = 0
    for rect in rects:
        label = labels[count]
        height = rect.get_height() + .02
        plt.text(count, height, label, ha = 'center', fontsize=12)
        n = names[count]
        if n == 'iqreq':
            n = 'req'
        if n == 'phaseA':
            n = 'amp'
        plt.text(count, -.1, n, ha = 'center', fontsize=12, color = 'black')
        count = count + 1

    n =  "image{:05d}.png".format(row)
    files.append(n)
    print (row, data_length, n)
    fig.savefig(n, transparent = True)

    insert = (mp.ImageClip(n)
             .set_start(time_point)
             .set_duration(time_inc)
             .resize(height=200) # if you need to resize...
             .margin(right=20, top=20, opacity=0) # (optional) logo-border padding
             .set_pos(("right","top")))

    time_point = time_point + time_inc
    inserts.append(insert)
    plt.close(fig)

for f in files:
    os.remove(f) 

print (inserts)
final = mp.CompositeVideoClip(inserts)

final.write_videofile("test.mp4")

