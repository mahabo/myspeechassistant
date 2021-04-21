
My Speech Assistant

This is the sample code of my private speech assitant with local "wake-word" on a raspberry 4

The solution uses uses open components to recognize locally the wake word "terminator" and translates then with google components voice to text and text to speech. 
Currently the solution supports following fancy use cases in German language:

Weather (Wetter):
provides the weather of a pre-configured location of choice
Knowlege (Wissen wiki):
The first phrases of the wikipedia article 

News (Nachrichten)
The latest WDR radio station mp3 podcast news

Emails 
writes STT to a preconfigured email adress

Garbage
tells the next garbage collection date. Data is collected from local open data project 


Corona
Tells the current corona incident number from RKI of a pre-configured town in Germany 

Nature, Cat 
plays sound files 

Music 
Plays Live 1 online radio stream




The solution needs some pre-installations:
sudo apt-get install vlc mpc mpd python3-bs4 mpg321
pip3 install python-vlc beepy gTTS wikipedia objectpath speechrecognition pvporcupine bs4 bout pyaudio



Have fun..
