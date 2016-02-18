import json
import os
import subprocess

import requests

from transcription import Transcriber

TRANSCRIPTION_PATH = "transcription_data"

seen_users = set()
trans = Transcriber()


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

    with open(dstpath, 'w') as outfile:
        outfile.write(json.dumps(info) + "\n")
    with open(path2, 'w') as outfile:
        outfile.write("{}".format(text))
    return dstpath


def request_chunk(offset, country_code="US"):
    # print "[ processing chunk with offset {} ]".format(offset)

    url = 'http://data.sleeptalkrecorder.com/data/topList?filter=countryCode=="{}"&offset={}&order=thumbs&time=all' \
        .format(country_code, offset)

    r = requests.get(url)
    data = r.json()
    num_transcribed = 0
    for entry in data:
        # print "name=", entry['clipName'], entry['username'], entry['clipPath']
        username = entry['username']

        if username in seen_users:
            continue

        clip_name = file_escape(entry['clipName'])
        filename = file_escape("{}_{}".format(username, clip_name))
        mp3_name = os.path.join(".", TRANSCRIPTION_PATH, "data", "{}.mp3".format(filename))
        download_file(entry['clipPath'], mp3_name)
        wav_name = trans.create_wav(mp3_name)
        if wav_name:
            text = trans.transcribe(wav_name)
            if text:
                seen_users.add(username)
                save_transcription(text, filename, entry)
                num_transcribed += 1
    # print "successfully transcribed {} recordings".format(num_transcribed)
    return num_transcribed, len(data)


def download_audio_files(start_offset=0):
    global seen_users
    seen_users = set()
    offset = start_offset
    total_transcribed = 0

    paths = ["./{}/data".format(TRANSCRIPTION_PATH), "./{}/text".format(TRANSCRIPTION_PATH),
             "./{}/transcriptions".format(TRANSCRIPTION_PATH)]
    for dir in paths:
        if not os.path.exists(dir):
            os.makedirs(dir)
    while True:
        (amt, total) = request_chunk(offset)
        if total == 0:
            break
        offset += total
        total_transcribed += amt
        print "TOTAL TRANSCRIPTIONS =", total_transcribed


def clean():
    subprocess.call("cd /Users/jameslennon/PycharmProjects/sleeptalking-transcription && rm -rf transcription_data/*",
                    shell=True)
