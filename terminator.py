#!/usr/bin/env python3
# Build for Raspberry 4 

import struct
import pyaudio
import pvporcupine
import speech_recognition as sr
import threading
import subprocess
import json
import requests
import datetime
import os
from subprocess import Popen, PIPE
import vlc
import beepy as beep    #1 : 'coin', 2 : 'robot_error', 3 : 'error', 4 : 'ping', 5 : 'ready', 6 : 'success', 7 : 'wilhelm'
from gtts import gTTS
import wikipedia  # pip3 install wikipedia
from bs4 import BeautifulSoup

# needed for Email send feature
import smtplib   
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Needed for getting the Corona RKI values from the net
import urllib.request, json 
import objectpath
import math


# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# We set here the parameters

porcupine = None
pa = None
audio_stream = None



# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# we catch here the latest news with "Beautiful Soup" and "requests" from WDR

r = requests.get('https://www1.wdr.de/mediathek/audio/wdr-aktuell-news/wdr-aktuell-152.podcast')
soup = BeautifulSoup(r.text, 'lxml')
    
for link in soup.find_all('enclosure'):
    p_news = vlc.MediaPlayer(link.get('url'))
    print(link.get('url'))
    break

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Here are the URL definitions for our VLC player  (NOTE: we need to define them here otherwise threading does not work)

p_seaside = vlc.MediaPlayer("res/seaside.wav")
p_miao = vlc.MediaPlayer("res/katze.mp3")
p_music = vlc.MediaPlayer("http://wdr-1live-live.icecast.wdr.de/wdr/1live/live/mp3/128/stream.mp3")


# ''''''''''''''''''''''''''''''''''''''''''''''''''some definitions''''''''''''''''''''''''''''''''''''''''''''''''''''
# Functions for the VLC as thread  (NOTE: we need to define them here otherwise threading does not work)
def speak(text):
    engine.say(text)
    engine.runAndWait()

def miao():
    p_miao.play()

def seaside():    
    p_seaside.play()

def news():    
    p_news.play()    

def music():
    p_music.play()

# we request with the search string and wikipedia searches the german site and delöivers the number of sentences (here 3)
#
def wiki(suche):
    wikipedia.set_lang("de")
    try:
        print(wikipedia.summary(suche, sentences=3))
        mspeak(wikipedia.summary(suche, sentences=3))
    except:
        print("fehler")
        mspeak("Kann den Begriff in Wiki nicht finden")   



# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# collects the next date of classic garbage collection  
def garbage():    
    today = datetime.date.today()

    # some lists with Germany Days of the week and Months, plus the dates of Garbage collection
    # https://www.w3schools.com/python/python_datetime.asp

    day =["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    month = ["leer", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
    scheduledatelist = ['12.01.2021', '22.01.2021', '13.02.2021', '26.02.2021', '12.03.2021' ,'25.03.2021', '08.04.2021', '23.04.2021', '08.05.2021', '21.05.2021', '05.06.2021', '17.06.2021', '02.07.2021', '17.07.2021', '28.07.2021', '13.08.2021', '25.08.2021', '08.09.2021', '22.09.2021', '06.10.2021', '22.10.2021', '06.11.2021', '17.11.2021', '04.12.2021', '16.12.2021', '29.12.2021']

    for ddate in scheduledatelist:
        md = datetime.datetime.strptime(ddate, "%d.%m.%Y")
    
        if md.strftime("%Y-%m-%d") > today.strftime("%Y-%m-%d"):
            gstr = "Der nächste Restmüll wird am " + day[md.weekday()] + " dem " + md.strftime("%d") + " " + month[int(md.strftime("%m"))] + " abgeholt"
            print(gstr)
            mspeak(gstr)
            break




# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# bring all mp3 streams to ilence (we use this when the wake word has beed detected)
def silence():
    p_news.stop()
    p_seaside.stop()
    p_miao.stop()
    p_music.stop()    
   
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# uses google female voice to speak 

def mspeak(tellme):
	tts = gTTS(tellme, lang="de")
	tts.save('res/mspeak.mp3')
	os.system('mpg321 res/mspeak.mp3 -quiet')
	os.system('rm res/mspeak.mp3')


# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# take a command and process it
def takeCommand():
    
    r=sr.Recognizer()
    
    # How to calibrate the microphoine in case of noise:
    # good link is: https://www.codesofinterest.com/2017/04/energy-threshold-calibration-in-speech-recognition.html 
    #    r.energy_threshold = 4000 
    #    r.adjust_for_ambient_noise(source)
    
    with sr.Microphone() as source:
        print("Listening...")
        os.system('mpg321 res/beep2.mp3 -quiet')
        audio=r.listen(source)

        try:
            statement=r.recognize_google(audio,language='de-DE')
            print(statement)

        except Exception as e:
            mspeak("nix verstanden")
            return "exit"
        return statement.lower()

# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# with this function we write an email including the text 

def sendemail(text):
	
	# Create the email 
	port = 465
	smtp_server = "smtp.xxx.xx"  #past your smtp server
	login = "mail@XXX.XXX" # paste your login   
	password = "XXXXXXXXXX" # paste your password 
	sender_email = "mail@hxxx.xxx" 
	receiver_email = "mail@xxx.xxx" 
	message = MIMEMultipart("alternative") 
	message["Subject"] = "Best wishes from your Voice Assistant..." 
	message["From"] = sender_email 
	message["To"] = receiver_email 
	
	#Add body to email
	message.attach(MIMEText(text, "plain"))
	
	
	# send your email
	with smtplib.SMTP("smtp.xxx.xxx", 587) as server:
		server.login(login, password)
		server.sendmail(sender_email, receiver_email, message.as_string())

	print("Sent")
	mspeak("Email versendet")


def corona():

  	#######################################################################################
	# API documentation RKI (change Object id number for another town - currently 73 = Wuppertal)
	#
	# https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4
	# https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0/data?geometry=-64.203%2C46.211%2C86.221%2C55.839
	

    with urllib.request.urlopen("https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=+Objectid%3D79&objectIds=73&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&returnGeometry=true&returnCentroid=false&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=4326&datumTransformation=&applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=JSON") as url:
        data = json.loads(url.read())
        tree = objectpath.Tree(data)
    
        city = tuple(tree.execute('$..GEN'))
        print("Die Tagesinzidenz in " + city[0] + " vom " + tuple(tree.execute('$..last_update'))[0][0:6] + " liegt bei " + str(math.floor(tuple(tree.execute('$..cases7_per_100k'))[0])))
        mspeak("Die Tagesinzidenz in " + city[0] + " liegt heute bei " + str(math.floor(tuple(tree.execute('$..cases7_per_100k'))[0])))
#-----------------------------  end of definitions  --------------------------------------------------------------------------


# ''''''''''''''''START OF PROGRAM '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Now we start getting the keywords (blueberry and terminator)
# Details can be found here: https://pypi.org/project/pvporcupine/
# sensitivities are made for each keyword. 0 is low 1 is high sensitivity
try:
    
    porcupine = pvporcupine.create(keywords=["blueberry", "terminator"], sensitivities=[0.9, 0.7])
    
    pa = pyaudio.PyAudio()



    audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)


    li = "I'm listening.."
    licnt = 1
    while True:
        li = li + "."
        licnt += 1
        if licnt > 10:
            licnt = 1
            li =  "I'm listening"
        print(li)
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
           
           os.system("clear")
           print("Ja bitte ?") 
           # stop all running threads like music, mp3 player...
           silence()
           
           mspeak("Ja bitte ?")
           
           
           li = "I'm listening.."
                      
           i = 1
           intent = "empty" 
           
           
           while i == 1:
                
                result = takeCommand()
                 

                # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                # Here we try to catch the intents     
                if "musik" in result:
                    mspeak("Let's rock'n roll")
                    t4 = threading.Thread(target=music)
                    t4.start()
                    break
                
                
                elif "natur" in result or "meer" in result:
                    t3 = threading.Thread(target=seaside)
                    t3.start()
                    break
                
                elif "wissen" in result: 
                    mspeak("Wonach soll ich suchen?")
                    wik=takeCommand()
                    t5 = threading.Thread(target=wiki(wik))
                    t5.start()
                    break    


                elif "nachrichten" in result or "news" in result or "info" in result:
                    # https://www1.wdr.de/mediathek/audio/wdr-aktuell-news/index.html
                    # https://wdrmedien-a.akamaihd.net/medp/podcast/weltweit/fsk0/236/2366492/wdraktuell_2021-02-13_wdraktuellum2300uhr_wdr2.mp3
                    mspeak("hier die Nachrichten")
                    t2 = threading.Thread(target=news)
                    t2.start()
                    
                    break                             
                
                elif "katze" in result or "katzen" in result:
                    t1 = threading.Thread(target=miao)
                    t1.start()
                    break
                
                elif "email" in result or "mail" in result:
                    mspeak("Was soll ich schreiben?")
                    mmail=takeCommand()
                    mspeak("Ich hab notiert: "+mmail+"ist das ok?")    
                    confirm=takeCommand()                
                    
                    if "ok" in confirm or "ja" in confirm or "yes" in confirm:
                    	sendemail(mmail)    
                    else:
                        mspeak("ok, verworfen")
                   
                    break
                
                elif "müll" in result or "müllabholung" in result:
                    garbage()
                    break
                

                elif "günther" in result or "günter" in result:
                    
                    beep.beep(7)    
                    break

                
                elif "wetter" in result or "vorhersage" in result:
                    #openweathermap.org JSON request: 
                    #base_url="https://api.openweathermap.org/data/2.5/weather?"

                    base_url="https://api.openweathermap.org/data/2.5/weather?q=Wuppertal&units=metric&lang=de&appid=8ef61edcf1c576d65d836254e11ea420"
                     
                    
                    response = requests.get(base_url)
                    x=response.json()
                    
                    if x["cod"]!="404":
                        y=x["main"]
                        current_temperature = y["temp"]
                        z = x["weather"]
                        weather_description = z[0]["description"]
                        mspeak(" Die Temperatur in Wuppertal ist jetzt" +
                              str(current_temperature) +
                              " Grad und " +
                              str(weather_description))
                        print(" Current temperature in Wuppertal is " +
                              str(current_temperature) +
                              " degree and " +
                              str(weather_description))

                    else:
                        speak(" City Not Found ")
                    break

                elif "corona" in result or "inzidenz" in result:
                    corona()
                    break


                
                elif "was kannst du" in result or "hilfe" in result:
                    mspeak("Frag mich gerne nach Wetter, Wissen, Nachrichten, Emails, Müll, Corona, Natur, Musik oder Katzen ")
                    break 

                    
                elif "bye" in result or "goodbye" in result or "tschüss" in result or "auf wiedersehen" in result:
                    mspeak("Tschüß")
                    break				
                elif "exit" in result:
                	#mspeak("Tschüß")
                	break

                else:
                    mspeak("sorry, dazu weiss ich nix")
                    print('sorry - no intent catched')
                    break

                result = " "

except:
  print("An exception occurred")
  result = " "
