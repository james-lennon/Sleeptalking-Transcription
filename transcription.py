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
        self.cuss_words = {}
        self._load_uncensor()

    def create_wav(self, srcpath):
        if not os.path.isfile(srcpath):
            return False
        basename = os.path.basename(srcpath)
        name = basename[0:basename.find(".")]
        dstpath = os.path.join(".", "gen", name + ".wav")
        sound = AudioSegment.from_mp3(srcpath)
        sound.export(dstpath, format="wav")
        return dstpath

    def transcribe(self, srcpath, uncensor=True):
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
            text = matches['alternative'][0]['transcript']

            if uncensor:
                text = self._uncensor(text)

            return text
        except sr.UnknownValueError:
            # unable to transcribe
            pass
        except sr.RequestError:
            # request error
            pass
        except TimeoutException:
            # request timed out
            # print "timed out on {}".format(srcpath)
            pass
        return False

    def _load_uncensor(self):
        with open("config/uncensor-data.txt") as openfile:
            words = openfile.read().split("\n")
            for w in words:
                if len(w) == 0: continue
                c = w[0].lower()
                if c not in self.cuss_words:
                    self.cuss_words[c] = {}
                self.cuss_words[c][len(w)] = w

    def _uncensor(self, content):
        words = content.split(" ")
        for i in range(len(words)):
            w = words[i].lower()
            if w.find("*") > -1:
                if len(w) == 0: continue
                n = len(w)
                c = w[0]
                if c in self.cuss_words and n in self.cuss_words[c]:
                    words[i] = self.cuss_words[c][n]
                    print("replaced {} with {}".format(w, words[i]))
                else:
                    print("couldn't uncensor {}".format(w))
        return " ".join(words)
