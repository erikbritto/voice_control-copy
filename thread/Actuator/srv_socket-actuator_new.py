# Raspberry PI Actuator
# IP - 192.168.0.37
#Networking
import connection
# argparse to parse the argunments for the logging
import argparse
#Logging
import logging
import vc_logging
import os
#Lamp API
from beautifulhue.api import Bridge

class Actuator():
	"""  

	Actuator node class.

	"""
	def __init__(self, args, HOST = '', PORT = 57000, LIGHT_IP = '192.168.0.87'):
		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")
		self.HOST = HOST
		self.PORT = PORT
		self.args = args
		self.light_ip = LIGHT_IP
		self.color = {
						'red'       : 0,
						'yellow'    : 14000,
						'green'     : 25500,
						'white'		: 35000,
						'blue'      : 47000,
						'pink'      : 56100
					}



	def update_lamp(self, lamp, d):
		#IP: Philips Hue Bridge (the small curcular device that connects to the lamps) IP
		bridge = Bridge(device={'ip': self.light_ip}, 
						user={'name': 'go3D6jUyb3yLQFP0tcPmJ3xzNPIC507T1SL2pnir'})
		resource = {
			'which': lamp,
			'data': {
				'state': d
			}
		}
		bridge.light.update(resource)
		pass


	def convert_command(self, command):
		
		command_dict = {}
		c = command.split('|')

		#Light
		if c[1] == 'all':
			lamp = list(range(1,4))
		else:
			lamp = c[2].split(',')
		
		#State
		if c[2]:
			command_dict['on'] = True if c[1] == 'on' else False
		
		#Color
		if c[3]:
			command_dict['hue'] = color[c[3]]
			command_dict['sat'] = 254
		
		#Brightness
		if c[4]:
			command_dict['bri'] = int((int(c[4])/100.0)*254)
		
		return (lamp,command_dict)


	def main(self):
		
		conn = connection.Server()

		try:
			print 'Opening connection'

			conn.connect()
			conn.accept()

			while True:

				command = conn.receive_message()

				if command != None: 

					self.log.info('Received: ' + str(command))

					data = command.split('/')

					for d in data:
						if d:
							lamp,command_dict = self.convert_command(d)
							if command_dict:		#False if command_dict is empty
								for l in lamp:
									self.log.info('lamp: ' + str(lamp)
													+ '\n' + str(command_dict))
									self.update_lamp(l, command_dict)
			
		except KeyboardInterrupt:
			print '\nINTERRUPTED BY USER'		
		except Exception as e:
			self.log.debug("ERROR: " + str(e))
		finally:
			conn.disconnect()
			conn.destroy()
			self.log.debug('Finishing program')



if(__name__ == '__main__'):
	try:
		parser = argparse.ArgumentParser(description='Actuator Node Logging')
		parser.add_argument('--log-level', action="store", type=str, choices=["critical", "error", "warning", "info", "debug", "notset"], default="info", help='Select the log level of the program.')
		parser.add_argument('--verbose', default=False, action = 'store_true', help='Select whether to output logs to the console.')

		args = parser.parse_args()

	except Exception as e:
		print 'ERROR PARSING ARGUMENTS'
	act = Actuator(args)
	act.main()