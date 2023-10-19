#! /usr/bin/env python3

import json
import sys, getopt, os, glob, datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import gridspec
import numpy as np
import parse_data # helper script

# this program takes data like this:
#  {"adc1":740,"ehz":0.161,"error":0,"id":0.197,"iq":0.094,"iqreq":0.000,"TMOS":0.000,"TMOT":0.000,"vbus":72.481,"Vd":1.928,"Vq":0.586},
# and makes a series of images that will be used in an overlay for a movie


def create_bargraph(ax, row, t, data, df, df_scaled, specs, place_box):
    labels = []
    values = []
    widths = []
    names = []
    count = 0

    duration = 200

    # groom these
    data_types = {}
    for n in specs['bar_displays']:
        data_types[n] = n
        if n == 'iqreq':
            data_types[n] = 'req'
        if n == 'phaseA':
            data_types[n] = 'amp'

    ax.clear() 
    ax.set_title(t, y=1.0, pad=-14, fontsize=16, color = 'yellow')
    for item in specs['bar_displays']:
        if specs['bar_displays'][item]:
            widths.append(0.8)
            names.append(data_types[item])
            values.append(df_scaled[item][row])
            labels.append(int(df[item][row]))
            count = count + 1

    b = ax.bar(names, values, width = widths, color = 'black', edgecolor='yellow', linewidth=3)
    ax.set(ylabel='', title='', ylim=(0, 1))
    ax.set_axis_off()

    rects = ax.patches
    count = 0
    for rect in rects:
        label = labels[count]
        height = rect.get_height() + .02
        ax.text(count, height, label, ha = 'center', fontsize=12)
        ax.text(count, -.1, names[count], ha = 'center', fontsize=12, color = 'black')
        count = count + 1
    if place_box:
        bound_box(ax)


def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def create_throttle(ax, value, place_box):
    rad = np.deg2rad(map_range(value, 740, 3994, -30, 90))
    ax.set_theta_zero_location('SE')
    ax.xaxis.set_tick_params(labelbottom=False)
    ax.set_rticks([])
    ax.set_thetamin(120)
    ax.set_thetamax(0)
    ax.grid(False)
    q = 20
    bars = ax.bar(rad/2, q, width=rad, color='red')

    # ax.plot([rad,rad], [0,1], color='black', linewidth=2)
    ax.set_title("Throttle")
    if place_box:
        bound_box(ax)
    
def create_temp(ax, temp, min, max, place_box):
    array = []
    rows = 25
    for i in np.arange(0, 1, 1 / rows):
        x = []
        x=[i]
        array.append(x)

    cmap=plt.cm.jet

    ax.set_yticks((0, rows))
    ax.set_yticklabels((min, max))

    p = map_range(temp, min, max, 0, rows)

    ax.pcolor(array , cmap = cmap )
    t = ax.text(-0.1, p, " ",
                ha="center", va="center", rotation=0, size=10,
                bbox=dict(boxstyle="rarrow,pad=0.3",
                          fc="lightblue", ec="steelblue", lw=2))   
    ax.set_title('MOS')
    ax.xaxis.set_tick_params(labelbottom=False)
    if place_box:
        bound_box(ax)


def create_elevation(ax, value, place_box):
    rad = np.deg2rad(value)
    ax.set_theta_zero_location('E')
    # ax.xaxis.set_tick_params(labelbottom=False)
    ax.set_rticks([])
    ax.set_thetamin(30)
    ax.set_thetamax(-30)
    ax.grid(False)
    ax.set_title("Elevation")
    arr2 = ax.arrow(rad, 0.5, 0, 1, alpha = 0.5, width = 0.15,
                     edgecolor = 'yellow', facecolor = 'green', lw = 2, zorder = 5)
    if place_box:
        bound_box(ax)

def bound_box(ax):
    bbox = ax.get_tightbbox(fig.canvas.get_renderer())
    x0, y0, width, height = bbox.transformed(fig.transFigure.inverted()).bounds
    # slightly increase the very tight bounds:
    xpad = 0.05 * width
    ypad = 0.05 * height
    fig.add_artist(plt.Rectangle((x0-xpad, y0-ypad), width+2*xpad, height+2*ypad, edgecolor='red', linewidth=3, fill=False))

def animate(i, total, a0, a1, a2, a3, title, data, specs, show_box):
    df = pd.DataFrame(data)
    df_scaled = df.copy()
    df['phaseA'] = np.sqrt( (df['id'] * df['id']) + (df['iq'] * df['iq']) )

    y = specs['bar_displays']
    for item in specs['bar_displays']:
        max = specs['max_vals'][item]
        min = specs['min_vals'][item]
        df_scaled[item] = (df[item] - min) / (max - min) 

    data_max_vals = df.max(axis = 0)

    data_length = len(df) - 1

    create_bargraph(a0, i, title, data, df, df_scaled, specs, show_box)
    create_temp(a1, 75, specs['min_vals']['TMOS'], specs['max_vals']['TMOS'], show_box)
    create_throttle(a2, df['adc1'][i], show_box)
    create_elevation(a3, 20, show_box)

def manage_files():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"d:c:",["datafile=", "config="])
    except getopt.GetoptError:
        print ('program.py -d <datafile> -c <config>')
        sys.exit(2)

    dname = ""
    cname = ""

    for opt, arg in opts:
        if opt in ("-d", "--datafile"):
            dname = arg
        if opt in ("-c", "--config"):
            cname = arg

    page = parse_data.get_json_file(dname)

    with open(cname, 'r') as fcc_file:
        config = json.load(fcc_file)

    return(page, config)
    
def main():
    (page, config) = manage_files()

    data = parse_data.make_frame(page['data'])
    x = parse_data.pad_data_set(data,
                                config['data_collection_period'], 
                                config['start_sec'],
                                config['movie_duration'])
    data = x['data']

    key = list(data.keys())[0]
    frames = len(data[key])

    # matplotlib animation doesnt work -- it bombs after  200 images or so. 
    #   the workaround is to send a pile of images to disk and make video using 
    #   ffmpeg. here we go..
    # this may be unnecessary, ffmpeg probably has a work around to combine videoes
    #   at a certain start point. 
    for i in range(frames):
        fig = plt.figure()
    
        t = str(datetime.timedelta(seconds=i/10))

        fig.set_figheight(config['fig_height'])
        fig.set_figwidth(config['fig_width'] / 4) 

        gs = gridspec.GridSpec(ncols=3, nrows=2,
                         width_ratios=[10, 10, 3], wspace=.5, hspace = .5,
                         height_ratios=[3, 1])

        ax0 = fig.add_subplot(gs[0,:-1])
        ax1 = fig.add_subplot(gs[0,2])
        ax2 = fig.add_subplot(gs[1,0], polar=True)
        ax3 = fig.add_subplot(gs[1,1], polar=True)

        animate(i, frames, ax0, ax1, ax2, ax3, t, data, config, False)
        plt.plot()
        f = 'images/{0:05d}image.png'.format(i)
        fig.savefig(f, transparent=True)
        print (('{} of {}, {}').format(i, frames, f))
        plt.clf()
        plt.close('all')

if __name__ == "__main__":
    main()







