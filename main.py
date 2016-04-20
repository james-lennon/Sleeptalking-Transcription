import sleep_database
import time

if __name__ == '__main__':
    sleep_database.clean()
    start_time = time.time()
    sleep_database.download_audio_files(save_audio=True, single_file=True, max_count=None, start_offset=1219)
    print "TIME ELAPSED: " + str(time.time() - start_time)

