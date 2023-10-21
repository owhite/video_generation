-------------------------------
Dependencies:
ffmpeg

Python modules:
mapplotlib
matplotlib
moviepy
pandas

-------------------------------

This fixed pytube to work on my mac

python -m pip install git+https://github.com/Zeecka/pytube@fix_1060
pip install --upgrade pytube

------------------------------
Making the video involves creating a series of videos that get stitched together. 
Be sure to check the output of every step, it is quite unlikely that everything will work the first time. The main thing to watch out for is if the codecs for audio and video work with ffmpeg, particularly when youre joining or overlaying videos together

## Go fetch the raw video footage from youtube
$ ./download_movie.py -c config.json -o raw.mp4

Get the resolution of the video, run:
$ ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 raw.mp4
1280x720

Get the duration of the video:
$ ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 raw.mp4
75.813152

These are configuration settings that go into config.json
    "movie_title": "MP2 hill climb",
    "amp_title": "FW=90, MAX=300A",
    "fig_height": 7,
    "fig_width": 10,
    "movie_URL": "https://youtu.be/UQB3h4kRCKc", 
    "movie_size": "1280x720", 
    "start_sec": 10.0, 
    "data_collection_period": 10.0, 
    "movie_duration": 75.81,
    "max_vals": 

fig_height/width refers to the size of the overlay on the raw video, the units are matplotlib units (inches?) and do not need to match the raw input video
movie_size is in pixels and does need to match the raw video
start_sec: your data probably does not go the whole length of the raw video, set this time point to when data was collected
max and min_vals refer to details of your controller

## Data overlay. Create a series of slides for overlay
#   note: this does not have to match the resolution of the raw video
#   note: this takes a while to run
$ ./bar_chart_overlay.py -d scrap.json -c config.json 

## use those slides to make transparent webm output
#  these types of steps could be done in the python programs but it's better to review
#  the intermediate results
$ ffmpeg -framerate 10 -pattern_type glob -i "images/*.png" -r 30  -pix_fmt yuva420p overlay.webm

## perform overlay of file output.webm on to thing.mp4
$ ffmpeg -i raw.mp4 -c:v libvpx-vp9 -i overlay.webm -filter_complex overlay movie.mp4

inspect movie.mp4 to make sure you have audio and an data overlay on top of the video. 

## create two pics then fade them in and out to create a movie
#   these are like opening credits and they need to be correct screen resolution
$ ./make_stats_slide.py -d scrap.json -c config.json -o premovie

## creates amp / ehz etc...
$ ./plot_amps.py -c config.json -d json_files/may21_1.json -o aftermovie

# This is how to create a still slide:
$ cat credits.txt | magick -gravity Center -background black -fill yellow -size 1280x720 -pointsize 24 label:@- credits.png

# This is how to convert a still slide into a fade in / fade out video:
$ ffmpeg -loop 1 -t 5 -i credits.png -filter_complex "[0:v]fade=t=in:st=0:d=1,fade=t=out:st=4:d=1[v0];  [v0]concat=n=1:v=1:a=0,format=yuv420p[v]" -map "[v]" credits.mp4

# This is how to make a still slide of the WRONG size
$ cat credits.txt | magick -gravity Center -background black -fill yellow -size 1200x720 -pointsize 24 label:@- static.png

# make a video, this is the wrong size and will look like static in the last step.
$ ffmpeg -loop 1 -t 5 -i static.png -filter_complex "[0:v]fade=t=in:st=0:d=1,fade=t=out:st=4:d=1[v0];  [v0]concat=n=1:v=1:a=0,format=yuv420p[v]" -map "[v]" static.mp4

$ ./combine.py output1.mp4 premovie.mp4 movie.mp4 aftermovie.mp4 credits.mp4 static.mp4


------------------------------
rpm(motor) = (ehz * 60) / pp
rpm(wheel) = (ehz * 60) / (pp * gear_ratio)
drpm(wheel) = rpm * circumference = (ehz * 60 * circumference) / (pp * 9.82)
drpm * minutes = distance traveled per minute = (dtpm)
dtpm = (ehz * 60 * circumference) / (pp * 9.82 * 60)
dtpms = (ehz * 60 * circumference) / (pp * 9.82 * 60 * 10)
circumference = 219.5
pp = 7
dtpms = (ehz * 60 * 219.5) / (7 * 9.82 * 60 * 10)
dtpms = ehz * (13170 / 41244)

distance traveled on a 219.5mm circuference tire for 1/10sec at given
dtpms = ehz * .31931 (cm)
dtpms = ehz * 3.1931 (mm)

--------------------------------------------------

## Go fetch the raw video footage from youtube
#  "movie_URL": "https://www.youtube.com/watch?v=QXmi6-ig2mM&feature=youtu.be", 
$ ./download_movie.py -c config.json -o raw.mp4

## it's too long to play with

$ ffmpeg -ss 00:00:00 -to 00:01:00 -i raw.mp4 -c copy output1.mp4

What is the size?
$ ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 raw.mp4
1280x716

Overlay text
ffmpeg -i scrap1.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='Stack Overflow':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,4)', drawtext=fontfile=/path/to/font.ttf:text='THING THING':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,0,4)'" -codec:a copy scrap2.mp4

ffmpeg -i scrap1.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='THING THING':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,1,4)'" -codec:a copy scrap2.mp4

Or, create an image

convert -background black -fill yellow -pointsize 28 -gravity west label:"This is line 1 of text\nThis is line 2 of text" -gravity center -extent 1200x800 thing.png

Fix transparent background 

convert thing.png -fuzz 10% -transparent black thing2.png

And then overlay on video
ffmpeg -i scrap1.mp4 -i thing2.png -filter_complex "[0:v][1:v] overlay=0:0 : enable='between(t,0,4)'" -c:a copy scrap2.mp4

convert -background black -fill yellow -pointsize 28 -gravity west label:"This is line 1 of text\nThis is line 2 of text" -gravity center -extent 400x400 thing.png

Suppose you want to change the position of the overlaid image:

ffmpeg -i scrap1.mp4 -i thing.png -filter_complex "[0:v][1:v] overlay=100:100 : enable='between(t,0,4)'" -c:a copy scrap2.mp4

--------------------------------------------------

Convert .mov to mp4
% ffmpeg -i FLASH_MESC_PART1.mov -vcodec h264 -c:a aac output1.mp4

What size is the raw video recording? 

 % ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 output1.mp4         
1398x814

These are some comments I want to overlay:
min:sec sec
00:57   57  See links in the description
03:43   223 Actually I meant hit "Open"
03:53   233 Did I say "Open"? hit "Finish"
05:05   305 See "Determine your motor parameters" in comments
08:31   511 Technically this a compile not a flash
09:14   554 Okay now it is flashing

To do that make this list:

ffmpeg -i output1.mp4 -vf 
"
drawtext=fontfile=/path/to/font.ttf:text='See links in the description':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,56,60)',
drawtext=fontfile=/path/to/font.ttf:text='Ok actually I meant \"hit Open\"':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,223,227)', 
drawtext=fontfile=/path/to/font.ttf:text='Did I say \"Open\"? hit \"Finish\"':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,233,236)', 
drawtext=fontfile=/path/to/font.ttf:text='See \"Determine your motor parameters\" in comments':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,305,309)', 
drawtext=fontfile=/path/to/font.ttf:text='Technically this a compile not a flash':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,511,515)', 
drawtext=fontfile=/path/to/font.ttf:text='Okay now it is flashing':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,554,557)'
"  
-codec:a copy output2.mp4

Bunch those together and run this command

% ffmpeg -i output1.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='See links in the description':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,56,60)',drawtext=fontfile=/path/to/font.ttf:text='Ok actually I meant \"hit Open\"':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,223,227)', drawtext=fontfile=/path/to/font.ttf:text='Did I say \"Open\"? hit \"Finish\"':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,233,236)', drawtext=fontfile=/path/to/font.ttf:text='See \"Determine your motor parameters\" in comments':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,305,309)', drawtext=fontfile=/path/to/font.ttf:text='Technically this a compile not a flash':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,511,515)', drawtext=fontfile=/path/to/font.ttf:text='Okay now it is flashing':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,554,557)'"  -codec:a copy output2.mp4

Now I want to overlay some images:

04:32 PROVIDE LIST OF FILES TO EDIT
06:00 PROVIDE LIST FOR MP2_V0_1.h
06:40 PROVIDE PIC OF VOLTAGE DIVIDERS
07:50 Pic of ST-LINK
07:58 ST-LINK - USB - COMPUTER
08:06 ST-LINK PILL
08:11 ST-LINK PILL CAPTION

create an image

convert -background black -fill yellow -pointsize 28 -gravity west label:"MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h\nMESC_F405RG/Core/Inc/MP2_V0_1.h\nMESC_F405RG/Core/Inc/MESC_F405.h" -gravity center thing.png

what's the size:

 % ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0  thing.png 
652x97
So centering is 

(1398 / 2) - (652 / 2) = 699 - 326 = 272

% ffmpeg -i output2.mp4 -i thing.png -filter_complex "[0:v][1:v] overlay=373:100 : enable='between(t,272,279)'" -c:a copy output3.mp4

Let's make another image:
convert -background black -fill yellow -pointsize 28 -gravity west label:"#define ABS_MAX_PHASE_CURRENT\n#define ABS_MAX_BUS_VOLTAGE\n#define ABS_MIN_BUS_VOLTAGE\n#define MAX_IQ_REQUEST\n#define R_VBUS_BOTTOM\n#define R_VBUS_TOP" -gravity center thing2.png

Size?
% ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0  thing2.png 
590x193

to center:
(1398 / 2) - (590 / 2) = 404, but I'm also going to shift left a bit

Overlay this list:
% ffmpeg -i output3.mp4 -i thing2.png -filter_complex "[0:v][1:v] overlay=360:100 : enable='between(t,360,368)'" -c:a copy output4.mp4

Overlay circuit diagram:
% ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0  PICS/circuit_diagram.png 
1130x396

(1398 / 2) - (1130 / 2) = 134

% ffmpeg -i output4.mp4 -i PICS/circuit_diagram.png -filter_complex "[0:v][1:v] overlay=134:100 : enable='between(t,400,410)'" -c:a copy output5.mp4

Overlay more pictures

07:58 ST-LINK - USB - COMPUTER
955x595 = CENTER: 222

% ffmpeg -i output5.mp4 -i PICS/STLINK_USB.png -filter_complex "[0:v][1:v] overlay=222:100 : enable='between(t,478,486)'" -c:a copy output6.mp4

08:06 ST-LINK PILL
993x544 = CENTER: 203

% ffmpeg -i output6.mp4 -i PICS/STLINK_PILL.png -filter_complex "[0:v][1:v] overlay=203:100 : enable='between(t,486,491)'" -c:a copy output7.mp4

08:11 ST-LINK PILL CAPTION
993x544 = CENTER: 203

% ffmpeg -i output7.mp4 -i PICS/STLINK_PILL_CAPTION.png -filter_complex "[0:v][1:v] overlay=203:100 : enable='between(t,491,494)'" -c:a copy output8.mp4






