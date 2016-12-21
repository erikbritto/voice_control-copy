import os
import socket



HOST = '192.168.0.84' #VM's IP Address
PORT = 57000

#arecord = os.system("arecord -D plughw:1,0 audio.wav")

p = os.system("pgrep arecord")

while True:
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect((HOST,PORT))
		break
	except Exception as e:
		print "ERROR OPENING SOCKET: " + str(e)

try:
	arq = open('/home/pi/def/audio.wav', 'r')

	while (p == 0):
		p = os.system("pgrep arecord")
		print "arecord PID: " + str(p)
		print "Recording"
		for line in arq.readlines():
			s.send(line)

except IOError as e:
	print 'ERROR: ' + str(e)
except KeyboardInterrupt:
	print "Finished"
	arq.close()
finally:
	print 'CLOSING SOCKET'
	s.close()
