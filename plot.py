#! /usr/bin/env python3

import sys, getopt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import parse_data # helper script

# URL = input()
# URL = 'https://raw.githubusercontent.com/owhite/ebike_data/main/datasets/first_set'
# page = parse_data.get_web_page(URL)

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

# {"adc1":740,"ehz":0.161,"error":0,"id":0.197,"iq":0.094,"iqreq":0.000,"TMOS":0.000,"TMOT":0.000,"vbus":72.481,"Vd":1.928,"Vq":0.586},

df['phaseA'] = np.sqrt( (df['id'] * df['id']) + (df['iq'] * df['iq']) )

t = np.arange(len(df['ehz']))

fig, host = plt.subplots()
fig.subplots_adjust(right=0.75)
ax1 = host.twinx()
ax2 = host.twinx()
ax3 = host.twinx()
ax2.spines.right.set_position(("axes", 1.1))
ax3.spines.right.set_position(("axes", 1.2))

fig.suptitle(title, fontsize=16)
color = 'tab:red'
host.set_ylim(0, 740)
host.set_xlabel("Samples", color='black')
host.tick_params(axis='y', labelcolor=color)
host.set_ylabel("ehz", color=color)
host.plot(t, df['ehz'], color=color, label = 'ehz')
fig.legend(loc = "upper left")

color = 'tab:blue'
datatype = 'phaseA'
ax1.set_ylabel(datatype, color=color)  
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 300)
ax1.plot(t, df[datatype], color=color, label = datatype)
fig.legend(loc = "upper left")

datatype = 'iqreq'
color = 'tab:green'
ax2.set_ylabel(datatype, color=color)  
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 400)
ax2.plot(t, df[datatype], color=color, label = datatype)
fig.legend(loc = "upper left")

datatype = 'adc1'
color = 'black'
ax3.set_ylabel(datatype, color=color)  
ax3.tick_params(axis='y', labelcolor=color)
ax3.set_ylim(700, 4200)
ax3.plot(t, df[datatype], color=color, label = datatype)
fig.legend(loc = "upper left")


# plt.show()
plt.draw()
plt.pause(1)
input()
plt.close(fig)
