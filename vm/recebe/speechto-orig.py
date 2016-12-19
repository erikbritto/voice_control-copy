import speech_recognition as sr
import os
import socket


# envia para o atuador
HOST = '150.164.10.107'  # coloca o host do servidor
PORT = 57000

r = sr.Recognizer()
p = os.system("pgrep python")

#socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

duration = 0
offset = 0
pos = 0

while (p == 0 ):
	if(p == 0):
            with sr.AudioFile("audio.wav") as source:

                source.audio_reader.setpos(pos)
                audio = r.record(source, duration=duration, offset=offset)
                print pos
   #             print offset

		p = os.system("pgrep python")
	#	print p



	try:
    		t = r.recognize_google(audio, language="pt-BR")
    		print("Text: \n\n" + t )
                s.send(t)
                duration = duration + 10
                offset = offset + 1
                pos = source.audio_reader.tell()
        except Exception as e:
		    		print("Exception: "+str(e))
