import os
import signal
from contextlib import contextmanager

import speech_recognition as sr
from pydub import AudioSegment


class TimeoutException(Exception): pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class Transcriber:
    def __init__(self):
        pass

    def create_wav(self, srcpath):
        if not os.path.isfile(srcpath):
            return False
        basename = os.path.basename(srcpath)
        name = basename[0:basename.find(".")]
        dstpath = os.path.join(".", "gen", name + ".wav")
        sound = AudioSegment.from_mp3(srcpath)
        sound.export(dstpath, format="wav")
        return dstpath

    def transcribe(self, srcpath):
        if not os.path.isfile(srcpath):
            return False

        r = sr.Recognizer()

        with sr.WavFile(srcpath) as source:
            # r.adjust_for_ambient_noise(source)
            audio = r.record(source)

        # calibrate energy threshold (sensitivity)
        r.energy_threshold = 100
        r.pause_threshold = 10
        r.pause_threshold = 1

        try:
            # transcribe with 10 second time limit using Google's speech-to-text API
            with time_limit(10):
                matches = r.recognize_google(audio, show_all=True)

            # check if failed
            if len(matches) == 0:
                return False

            # return first result
            return matches['alternative'][0]['transcript']
        except sr.UnknownValueError:
            # unable to transcribe
            pass
        except sr.RequestError:
            # request error
            pass
        except TimeoutException:
            # request timed out
            print "timeout"
            pass
        return False

    def uncensor(self, content):
        words = content.split(" ")
        for w in words:
            pass
        return content
