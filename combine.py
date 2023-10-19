#! /usr/bin/env python3

import sys

from moviepy.editor import *

video_codec = 'libx264'
audio_codec = 'aac'

l = []
l = sys.argv[1:]

clips = []
for f in l[1:]:
    v = VideoFileClip(f)
    clips.append(v)
    print (v.duration)

allclips = concatenate_videoclips(clips)
print (allclips.duration)

allclips.write_videofile(l[0], codec=video_codec, audio_codec=audio_codec)
