#! /usr/bin/env python3

import sys, getopt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib as mpl
import numpy as np
import parse_data # helper script
import random
import time


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

# 1920x1080

fig, host = plt.subplots(figsize=(16,9), dpi=1920/16)

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

# N = 21
# cmap = plt.get_cmap("jet", N)
# sm = plt.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(vmin=0, vmax=N))
# sm.set_array([])
# ticks = np.linspace(0, N - 1, int((N + 1) / 2))
# labels = np.linspace(0, 2, int((N + 1) / 2))
# boundaries = np.linspace(0, N, N + 1) - 0.5
# cbar = plt.colorbar(sm, ticks=ticks, boundaries=boundaries, shrink=0.9, pad=0.1, location="left")

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

np.random.seed(19680801)

# Throttle
# ax5 = fig.add_axes([0.1, 0.6, 0.20, 0.20], polar=True)
# ax5.set_rticks([])
# ax5.set_xticklabels(['E', '', 'Throttle', '2',])
# ax5.set_thetamin(90)
# ax5.set_thetamax(-30)
# ax5.grid(False)
# ax5.tick_params(axis='y', pad=0, left=True, length=6, width=1, direction='inout')

# Elevation
# ax6 = fig.add_axes([0.6, 0.6, 0.20, 0.20], polar=True)
# ax6.set_rticks([])
# ax6.set_thetamin(90)
# ax6.set_thetamax(-30)
# ax6.grid(False)
# ax6.tick_params(axis='y', pad=0, left=True, length=6, width=1, direction='inout')


def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def animate(i, vl, t2, axis1, axis2, array1, array2):
    degree = random.randint(-30, 30)
    rad = np.deg2rad(degree)

    rad = np.deg2rad(map_range(array2[i], 740, 3994, -30, 90))
    # axis1.clear() # each time this is called you have to reset everything else: ticks, etc. 
    # axis1.set_rticks([])
    # axis1.set_xticklabels(['E', '', 'Throttle', '2',])
    # axis1.set_thetamin(90)
    # axis1.set_thetamax(-30)
    # axis1.grid(False)
    # axis1.plot([rad,rad], [0,1], color="black", linewidth=2)

    # for key, spine in axis2.spines.items():
    #     spine.set_visible(False)

    # for r_label in axis2.get_yticklabels():
    #   r_label.set_text('thing')

    # axis2.set_yticklabels([])
    # axis2.get_yaxis().set_visible(False)

    # rad = np.deg2rad(map_range(array2[i], 740, 3994, -30, 90))
    # axis2.clear() 
    # axis2.set_rticks([])
    # axis2.set_thetamin(90)
    # axis2.set_thetamax(-30)
    # axis2.grid(False)
    # axis2.plot([rad,rad], [0,1], color="black", linewidth=2)

    print (len(df['ehz']), i)

    vl.set_xdata([i,i])
    # interval is in millisecs, and seems to be working okay
    #  to test, uncomment:
    # print (int((time.perf_counter() - t2) * 100))
    return vl,

vl = ax1.axvline(0, ls='-', color='r', lw=1, zorder=10)

# number of rows of data we got
frames = len(df['ehz']) # should be generalized, not ehz
freq = 10 # Hz

start = time.perf_counter()

ani = animation.FuncAnimation(fig, animate, frames=frames,
                              fargs=(vl, start, ax1, ax1, df['adc1'], df['adc1']),
                              interval=100, repeat=False) 

# writervideo = animation.FFMpegWriter(fps=8.18)
# ani.save('dummy.mp4', writer=writervideo)
plt.show()
# plt.close()

