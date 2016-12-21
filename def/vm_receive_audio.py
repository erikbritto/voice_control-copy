import socket
import os
import speech_recognition as sr

r = sr.Recognizer()
#Try with 127.0.0.1
HOST = ''
PORT = 57000
# p = os.getpid()
# print p
while True:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)

		print 'Opening connection'
		conn, addr = s.accept()

		break
	except Exception as e:
		print "ERROR OPENING SOCKET: " + str(e)

try:
	arq = open('audio.wav', 'w')
	while True:
		dados = conn.recv(1024)
		if not dados:
			print "ERROR: Connection was closed on the other side"
			break

		arq.write(dados)

	arq.close()
except Exception as e:
	print 'ERROR: ' + str(e)
finally:
	conn.close()
	print 'CLOSING SOCKET'
	s.close()

	
