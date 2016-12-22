
import os
import speech_recognition as sr
import connection

r = sr.Recognizer()
#Try with 127.0.0.1
HOST = ''
PORT = 57000

conn = connection.Server(HOST, PORT)

try:
	while True:
		print 'Opening connection'
		conn.connect()

		conn.receive_file(1024, 'temp.wav')
		os.rename('temp.wav','audio.wav')

		conn.disconnect()
except Exception as e:
	print 'ERROR: ' + str(e)
finally:
	print 'CLOSING SOCKET'
	s.close()

	
