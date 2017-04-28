# Sleeptalking Transcription Harvester

This project was a part of a research project I presented with Professor Deirdre Barrett of Harvard Medical School at the International Association for the Study of Dreams Conference in the Netherlands.  The goal of this research was to analyze the linguistic content of sleeptalking recordings to see how it compares to regular speech.  

This program accesses a database of sleeptalking recordings from around the world and crawls through all recordings by country.  After finding recordings, the program downloads and converts the audio to WAV files so that they can be transcribed.
It then uses Google’s Speech API to convert audio files to text.  This script generated over 4,600 successful transcriptions from the US.  

To analyze the linguistic contents of these transcriptions, we used the [Linguistic Inquiry and Word Count](https://liwc.wpengine.com) tool.  We analyzed the contents of sleeptalking as compared to regular speech, and saw how these results differred across countries.  

