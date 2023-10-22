--------------------------------------------------

Convert .mov to mp4
% ffmpeg -i FLASH_MESC_PART1.mov -vcodec h264 -c:a aac output1.mp4

What size is the raw video recording? 

 % ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 output1.mp4         
1398x814

Shit, I forgot a section and need to wedge in:

I created the video to insert in quicktime. 

Convert quicktime .mov to mp4
% ffmpeg -i insert_section.mov -vcodec h264 -c:a aac insert_section.mp4

How big is it? 
% ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 insert_section.mp4
938x590

how long is it?
$ ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 insert_section.mp4
19.889000

change the size
% ffmpeg -i insert_section.mp4 -vf "scale=1398x814" output2.mp4

gonna change the codec etc of the movie:
ffmpeg -i output2.mp4 -ss "00:00:00.000" -to "00:00:19.800" -codec:v libx264 -crf 23 -pix_fmt yuv420p -codec:a aac -f mp4 -movflags faststart tmp2.mp4


how long is the original video?
% ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 output1.mp4
574.35800, 9:34 in minutes

trim the first one
% ffmpeg -i output1.mp4 -ss "00:00:00.000" -to "00:06:56.000" -codec:v libx264 -crf 23 -pix_fmt yuv420p -codec:a aac -f mp4 -movflags faststart tmp1.mp4

trim the first one to the end
% ffmpeg -i output1.mp4 -ss "00:06:56.000" -to "00:09:34.000" -codec:v libx264 -crf 23 -pix_fmt yuv420p -codec:a aac -f mp4 -movflags faststart tmp3.mp4

Use this to put them all together:
$ ./combine.py final.mp4 tmp1.mp4 tmp2.mp4 tmp3.mp4

Load this into quicktime to remove audio, then add in NARRATION_AUDIO.m4a
That is called final2.mov, convert back to mp4

$ ffmpeg -i final2.mov -vcodec h264 -c:a aac output1.mp4

These are some comments I want to overlay:

ffmpeg -i output1.mp4 -vf 
"
drawtext=fontfile=/path/to/font.ttf:text='See links in youtube description':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,57,60)',
drawtext=fontfile=/path/to/font.ttf:text='Look at \"Determine your motor parameters\" in the youtube description':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,302,306)', 
drawtext=fontfile=/path/to/font.ttf:text='Those files are used for other controllers':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,458,462)'
"  
-codec:a copy output2.mp4

Then bunch those together and run this command

7:38

$ ffmpeg -i output1.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='See links in youtube description':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,57,60)', drawtext=fontfile=/path/to/font.ttf:text='Look at \"Determine your motor parameters\" in the youtube description':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,302,306)', drawtext=fontfile=/path/to/font.ttf:text='Those files are used for other controllers':fontcolor=yellow:fontsize=36:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=((h-text_h)/2) + 30:enable='between(t,458,462)'" -codec:a copy output2.mp4

Now I want to overlay some images:

04:35 (275) LIST OF FILES TO EDIT IN STMCUT
06:07 (367) LIST OF VARIABLES TO TOUCH IN MP2_V0_1
06:45 (405) PROVIDE PIC OF VOLTAGE DIVIDERS
08:06 (486) ST-LINK - USB - COMPUTER
08:28 (508) ST-LINK PILL
08:30 (510) ST-LINK PILL CAPTION

create an image

convert -background black -fill yellow -pointsize 28 -gravity west label:"MESC_Common/Inc/MESC_MOTOR_DEFAULTS.h\nMESC_F405RG/Core/Inc/MP2_V0_1.h\nMESC_F405RG/Core/Inc/MESC_F405.h" -gravity center thing.png

what's the size:

 % ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0  thing.png 
652x97
So centering is 

(1398 / 2) - (652 / 2) = 699 - 326 = 272

% ffmpeg -i output2.mp4 -i thing.png -filter_complex "[0:v][1:v] overlay=373:100 : enable='between(t,275,282)'" -c:a copy output3.mp4

Let's make another image:
convert -background black -fill yellow -pointsize 28 -gravity west label:"#define ABS_MAX_PHASE_CURRENT\n#define ABS_MAX_BUS_VOLTAGE\n#define ABS_MIN_BUS_VOLTAGE\n#define MAX_IQ_REQUEST\n#define R_VBUS_BOTTOM\n#define R_VBUS_TOP" -gravity center thing2.png

Size?
% ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0  thing2.png 
590x193

to center:
(1398 / 2) - (590 / 2) = 404, but I'm also going to shift left a bit

Overlay this list:
% ffmpeg -i output3.mp4 -i thing2.png -filter_complex "[0:v][1:v] overlay=360:100 : enable='between(t,367,375)'" -c:a copy output4.mp4

Overlay circuit diagram:
% ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0  PICS/circuit_diagram.png 
1130x396

(1398 / 2) - (1130 / 2) = 134

% ffmpeg -i output4.mp4 -i PICS/circuit_diagram.png -filter_complex "[0:v][1:v] overlay=134:100 : enable='between(t,405,412)'" -c:a copy output5.mp4

Overlay more pictures

ST-LINK - USB - COMPUTER
955x595 = CENTER: 222

% ffmpeg -i output5.mp4 -i PICS/STLINK_USB.png -filter_complex "[0:v][1:v] overlay=222:100 : enable='between(t,486,508)'" -c:a copy output6.mp4

ST-LINK PILL
993x544 = CENTER: 203

% ffmpeg -i output6.mp4 -i PICS/STLINK_PILL.png -filter_complex "[0:v][1:v] overlay=203:100 : enable='between(t,507,511)'" -c:a copy output7.mp4

ST-LINK PILL CAPTION
993x544 = CENTER: 203

% ffmpeg -i output7.mp4 -i PICS/STLINK_PILL_CAPTION.png -filter_complex "[0:v][1:v] overlay=203:100 : enable='between(t,510,512)'" -c:a copy output8.mp4

430 has a long pause. 

============================================================
                     BASEMENT MATERIALS
============================================================

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
