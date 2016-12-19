import os
import socket



HOST = '192.168.0.84' #VM's IP Address
PORT = 57000

arecord = os.system("arecord -D plughw:1,0 audio.wav")

p = os.system("pgrep arecord")

try:
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((HOST,PORT))

	try:
		arq = open('/opt/iot-audio/audio.wav', 'r')

		while (p == 0):
			p = os.system("pgrep arecord")
			print "arecord PID: " + str(p)
			print "Recording"
			for line in arq.readlines():
				s.send(line)
		else:
			print "Finished"
			arq.close()
			s.close()
	except Exception as e:
		raise e
		
except Exception as e:
	print "ERROR: " + str(e)