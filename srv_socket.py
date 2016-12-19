import socket
import os
import speech_recognition as sr

r = sr.Recognizer()
#Try with 127.0.0.1
HOST = ''
PORT = 57000
# p = os.getpid()
# print p
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1)

	conn, addr = s.accept()

	try:
		arq = open('/home/cbtm/socketpython/audio.wav', 'w')
		while True:
			dados = conn.recv(1024)
			if not dados:
				print "ERROR: Connection was closed on the other side"
				break

		arq.write(dados)

		arq.close()
	except Exception as e:
		raise e
	finally:
		conn.close()
		s.close()
except Exception as e:
	print "ERROR: " + str(e)
	
