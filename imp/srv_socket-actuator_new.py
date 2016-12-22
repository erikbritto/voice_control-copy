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
	
	command_dict = {}
	c = command.split()
	
	if c[0] == 'turn':
		command_dict['on'] = True if c[1] == 'on' else False
	elif c[0] == 'color':
		command_dict = color_to_hue(c[1])
	elif c[0] == 'brightness':
		command_dict['bri'] = int((int(c[1])/100.0)*254)
	elif c[0] == 'lamp':
		lamp = int(c[1])
	
	return (lamp,command_dict)


def main():
	lamp = 3	#Define default lamp
	
	# Socekt Server
	#Could it also be:
	#HOST = '127.0.0.1'
	#???
	HOST = ''
	PORT = 57000


	conn = connection.Server(HOST, PORT)

	try:
		print 'Opening connection'

		conn.connect()

		while True:

			dados = conn.receive_message()

			print 'Received: ' + dados

			data = dados.split(',')

			for d in data:
				if d:
					lamp,command_dict = convert_command(lamp, d)
					if command_dict:		#False if command_dict is empty
						update_lamp(lamp, command_dict)
				
					print d
				#CRIA STRING VAZIA NO SPLIT COM VIRGULA SE A VIRGULA ESTA NO FINAL DA STRING ATUAL
		
	except KeyboardInterrupt:
		print '\nINTERRUPTED BY USER'		
	except Exception as e:
		print "ERROR: " + str(e)
	finally:
		conn.disconnect()
		conn.destroy()
		print 'Finishing program'



if(__name__ == '__main__'):
	main()