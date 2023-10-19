import urllib.request
import json
import re

def get_web_page(req):
    try: urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason) 
    with urllib.request.urlopen(req) as response:
        the_page = response.read().decode('utf-8')
        response.close()
        return(the_page)
        
def get_json_file(fname):
    with open(fname, 'r') as fcc_file:
        page = json.load(fcc_file, strict=False)
        return(page)

def make_frame(lines): 
    names = []
    sets = {}

    for key in lines[0].keys():
        names.append(key)
        sets[key] = []

    for line in lines:
        for name in names:
            sets[name].append(line[name])

    my_dict = {}
    for name in names:
        my_dict.update({name: sets[name]})
        
    return(my_dict)

def pad_data_set(array, collection_speed, start_s, vid_len):
    key = list(array.keys())[0]
    row = array[key]
    data_sec = len(row) / collection_speed
    end_sec = vid_len - start_s - data_sec
    front_pad = int(start_s * collection_speed)
    end_pad = int(end_sec * collection_speed)

    d = {}
    d['data'] = array
    d['front_pad']= front_pad
    d['data_len'] = len(row)
    d['end_pad']= end_pad

    for item in array:
        row = array[item]
        l1 = [row[0]] * front_pad
        l2 = [row[-1]] * end_pad
        array[item] = l1 + row + l2

    print('data length {0}(secs) {1}(frames)'.format(data_sec, len(row)))
    print('video length: {0}(secs) {1}(data_frames)'.format(vid_len, int(vid_len*collection_speed)))
    print('adding {0}(secs) {1}(frames) to beginning'.format(start_s, front_pad))
    print('adding {0}(secs) {1}(frames) to end'.format(end_sec, end_pad))
    # print('{0}(secs) {1}(frames) final dataset'.format(len(array[item]) / collection_speed, len(array[item])))


    return(d)

def strip_vt100_commands (str):
    cmds = {
        '[32m': '',
        '[35m': '',
        '[36m': '',
        '[37m': '',
        '[46m': '',
        '[15': '',
        '[35': '',
        '[46': '',
        '[57': '',
        '[3': '', # put this last
        '`': ''}
    for key, value in cmds.items():
        str = re.sub('^[0-9: \.]*', '', str)
        str = str.replace(key, value)
        str = re.sub('\| ', '\t', str)

    return(str)

# meaning: parse all the results that come from Jens' get call to the terminal
def load_get_response(lines):
    d = {}
    for line in lines.split('\n'):

        mapping =  dict.fromkeys(range(32))
        line = line.translate(mapping)
        line = strip_vt100_commands(line)

        if (line.count('\t')) == 4: 
            l = line.split('\t');
            d[l[0]] = {}
            d[l[0]]['value'] = l[1]
            d[l[0]]['min']   = l[2]
            d[l[0]]['max']   = l[3]
            d[l[0]]['desc']  = l[4]
    return(d)

