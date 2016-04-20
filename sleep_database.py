import os
import subprocess
import atexit

import requests

from transcription import Transcriber

TRANSCRIPTION_PATH = "transcription_data"
AUTOSAVE_COUNT = 100

seen_users = set()
trans = Transcriber()
content = ""


def file_escape(string):
    value = ''.join([c for c in string if c.isalnum() or c in (' ', '-', '_')])
    return value.replace(" ", "_").replace("/", ":")


def download_file(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(1024):
            fd.write(chunk)


def save_transcription(text, name, entry):
    dstpath = os.path.join(".", TRANSCRIPTION_PATH, "transcriptions", name + ".txt")
    path2 = os.path.join(".", TRANSCRIPTION_PATH, "text", name + ".txt")
    info = {
        "user": entry['username'],
        "date": entry['date'],
        "name": entry['clipName'],
        "countryCode": entry['countryCode'],
        "transcription": text
    }

    # with open(dstpath, 'w') as outfile:
    #     outfile.write(json.dumps(info) + "\n")
    with open(path2, 'w') as outfile:
        outfile.write("{}".format(text))
    return dstpath


def request_chunk(offset, country_code="US", save_files=False, single_file=True):
    # print "[ processing chunk with offset {} ]".format(offset)

    url = 'http://data.sleeptalkrecorder.com/data/topList?filter=countryCode=="{}"&offset={}&order=thumbs&time=all' \
        .format(country_code, offset)
    content = ""

    r = requests.get(url)
    data = r.json()
    num_transcribed = 0
    for entry in data:
        # print "name=", entry['clipName'], entry['username'], entry['clipPath']
        username = entry['username']

        if username in seen_users:
            continue

        clip_name = file_escape(entry['clipName'])
        filename = file_escape(u"{}_{}".format(username, clip_name.decode(errors="ignore")))
        mp3_name = os.path.join(".", TRANSCRIPTION_PATH, "data", "{}.mp3".format(filename))
        download_file(entry['clipPath'], mp3_name)
        wav_name = trans.create_wav(mp3_name)
        if wav_name:
            text = trans.transcribe(wav_name)
            if text:
                content += text + "\n"
                seen_users.add(username)
                num_transcribed += 1
                if not single_file:
                    save_transcription(text, filename, entry)
        if not (save_files and text):
            remove_audio_file(mp3_name)
        remove_audio_file(wav_name)
    # print "successfully transcribed {} recordings".format(num_transcribed)
    return num_transcribed, len(data), content


def download_audio_files(save_audio=False, start_offset=0, single_file=True, max_count=None):
    global seen_users
    global content
    seen_users = set()
    offset = start_offset
    total_transcribed = 0
    last_save = 0
    # content = ""

    atexit.register(save_files)

    paths = ["./{}/data".format(TRANSCRIPTION_PATH), "./{}/text".format(TRANSCRIPTION_PATH),
             "./{}/transcriptions".format(TRANSCRIPTION_PATH)]
    for dir in paths:
        if not os.path.exists(dir):
            os.makedirs(dir)
    while True:
        (amt, total, text) = request_chunk(offset, save_files=save_audio, single_file=single_file)
        if total == 0:
            break
        content += text.decode(errors="ignore")
        offset += total
        total_transcribed += amt
        print "TOTAL TRANSCRIPTIONS ={}; OFFSET={}".format(total_transcribed, offset)
        if total_transcribed / AUTOSAVE_COUNT > last_save:
            print "AUTOSAVING"
            save_files()
            last_save += 1
        if max_count is not None and total_transcribed >= max_count:
            break

    if single_file:
        with open("transcriptions.txt", "w") as outfile:
            # outfile.write(str(unicode(content, errors='ignore')))
            outfile.write(content.encode('utf-8'))


def save_files():
    global content
    with open("transcriptions.txt", "w") as outfile:
        # outfile.write(str(unicode(content, errors='ignore')))
        outfile.write(content.encode('utf-8'))


def remove_audio_file(filename):
    os.remove(filename)
    # subprocess.call("rm {}".format(filename))


def clean():
    subprocess.call("cd ~/sleeptalking-transcription && rm -rf transcription_data/*",
                    shell=True)
