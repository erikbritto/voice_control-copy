# import speech_recognition as sr
import os
import socket
from itertools import groupby

HOST = '192.168.0.37'  # Socket server's IP (actuator)
PORT = 57000

r = sr.Recognizer()
p = os.system("pgrep python") # Check if python is running

#Open socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

duration = 0
offset = 0
pos = 0
i =0

lamp = 0

while (p == 0):
	if(p == 0):
			with sr.AudioFile("audio.wav") as source:
				source.audio_reader.setpos(pos)
				audio = r.record(source,duration=duration,offset=offset)
		
		print i 
		i+=1

		print pos

		p = os.system("pgrep python")
		print p

	try:
			t = r.recognize_google(audio, language="en-US")
			print("Text: \n\n" + t )

			s.send(t)

			duration = duration + 10
			offset = offset + 1
			pos = source.audio_reader.tell()

	except Exception as e:
		print "Exception: " + str(e) 
	finally:
		#Close socket
		s.close()
		quit()
		
