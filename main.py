import sleep_database

if __name__ == '__main__':
    sleep_database.clean()
    sleep_database.download_audio_files(save_audio=True)
