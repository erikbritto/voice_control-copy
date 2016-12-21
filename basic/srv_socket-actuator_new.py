# Raspberry PI Atuador
# IP - 192.168.0.37
#
#


import socket
import os
from beautifulhue.api import Bridge



def color_to_hue(color):
	color_dict = {
					'red'       : 0,
					'yellow'    : 12750,
					'green'     : 25500,
					'blue'      : 46920,
					'pink'      : 56100
				}

	if color == 'white':
		return {'ct' : 222}
	else:
		return {'hue' : color_dict[color]}

def update_lamp(lamp,d):
	#IP: Philips Hue Bridge (the small curcular device that connects to the lamps) IP
	bridge = Bridge(device={'ip': '192.168.0.87'}, user={'name': 'go3D6jUyb3yLQFP0tcPmJ3xzNPIC507T1SL2pnir'})
	resource = {
		'which': lamp,
		'data': {
			'state': d
		}
	}
	bridge.light.update(resource)
	pass

def convert_command(lamp, command):
	MAX_LAMPS = 3		#Maximum number of lamps connected to bridge

	command_dict = {}
	c = command.split()
	
	if c[0] == 'turn':
		command_dict['on'] = True if c[1] == 'on' else False
	elif c[0] == 'color':
		command_dict = color_to_hue(c[1])
	elif c[0] == 'brightness':
		value = int(c[1])
		if 0 <= value <= 100:		#Check if brightness value is in range
			command_dict['bri'] = int((value/100.0)*254)
	elif c[0] == 'lamp':
		value = int(c[1])
		if 1 <= value <= MAX_LAMPS:	#Check if lamp number is in range
			lamp = value
	
	return (lamp,command_dict)


def main():
	lamp = 3	#Define default lamp
	
	# Socekt Server
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
			print 'OPENING SOCKET'
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind((HOST, PORT)) #Bind it to port
			s.listen(1) #Start listening
			print 'LISTENING ON PORT: ' + str(PORT)
			try:
				print 'Opening connection'
				conn, addr = s.accept() #Accept connection

				#Maybe move this to else statement
				while True:
					dados = conn.recv(1024) #Receives data from socket, on socket disconnect return 0
					if not dados: #If length of data received is 0 (connection was closed orderly on the other side)
						#Elegantly exit
						print "ERROR: Connection was closed on the other side"
						print 'Closing connection'
						conn.close()
						print 'Closing socket'
						s.close()
						print 'Exiting'
						quit()

					print 'Received: ' + dados

					data = dados.split()

					data = [i + ' ' + j for i,j in zip(data[:-1],data[1:])]

					for d in data:
						lamp,command_dict = convert_command(lamp, d)
						if command_dict:		#False if command_dict is empty
							update_lamp(lamp, command_dict)
					
						print d

				# print 'Closing connection'
				# conn.close()

			except Exception as e:
				print "ERROR: " + str(e)
				print 'CLOSING SOCKET'
				s.close()

			# finally:
			# 	print 'CLOSING SOCKET'
			# 	s.close()
		except Exception as e:
			print "ERROR: " + str(e)


main()