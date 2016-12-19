# Raspberry PI Atuador
# IP - 192.168.0.37
#
#


import socket
import os
from beautifulhue.api import Bridge


def turnon():
	global lamp
	bridge = Bridge(device={'ip': '192.168.0.87'}, user={'name': 'go3D6jUyb3yLQFP0tcPmJ3xzNPIC507T1SL2pnir'})
	resource = {
		'which': 3,
		'data': {
			'state': {'on' : True, 'ct' : 222}
		}
	}
	bridge.light.update(resource)
	pass

def turnoff():
	bridge = Bridge(device={'ip': '192.168.0.87'}, user={'name': 'go3D6jUyb3yLQFP0tcPmJ3xzNPIC507T1SL2pnir'})
	resource = {
		'which': 3,
		'data': {
			'state': {'on' : False, 'ct' : 222}
		}
	}
	bridge.light.update(resource)
	pass




# Servidor Socket
# Recebe conexão da VMa
#Could it also be:
#HOST = '127.0.0.1'
#???
HOST = ''
PORT = 57000
#What is this for?
p = os.getpid() #Gets the python pid
print p

while True: 
	try:
		#Create the socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT)) #Bind it to port
		s.listen(1) #Start listening

		try:
			conn, addr = s.accept() #Accept connection


			while True:
				dados = conn.recv(1024) #Receives data from socket, on socket disconnect return 0
				if not dados: #If length of data received is 0 (connection was closed orderly on the other side)
					#Elegantly exit
					print "ERROR: Connection was closed on the other side"
					conn.close()
					s.close()
					quit()

				if dados == 'turn on':
					turnon()
				elif dados == 'turn off':
					turnoff()

				print dados

			conn.close()

		except Exception as e:
			print "ERROR: " + str(e)

		finally:
			s.close()
	except Exception as e:
		print "ERROR: " + str(e)