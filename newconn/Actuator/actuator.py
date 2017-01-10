# Raspberry PI Actuator
# IP - 192.168.0.37
#Networking
import connection
# argparse to parse the argunments for the logging
import argparse
#Logging
import logging
import vc_logging
#Time
import timeit
#Lights
from lights import Light

class Actuator():
	"""	Actuator node class."""


	def __init__(self, args, HOST = '', PORT = 57000, LIGHT_IP ='192.168.0.87'):
		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")
		self.HOST = HOST
		self.PORT = PORT
		self.args = args
		self.color = {
						'red'       : 0,
						'yellow'    : 14000,
						'green'     : 25500,
						'white'		: 35000,
						'blue'      : 47000,
						'pink'      : 56100
					}

		self.lights = [Light(i,LIGHT_IP) for i in range(1,4)]


	def execute_command(self, command):
		"""[summary]
		
		[description]
		
		Arguments:
			command {[type]} -- [description]
		"""

		c = command.split('|')

		#Obtains list of lights that with issued commands
		if c[1] == 'all':
			lamp = list(range(0,3))
		else:
			lamp = [int(i)-1 for i in c[1].split(',')]

		#Issue commands for each light
		for i in lamp:
			#State
			if c[2]:
				self.lights[i].set_status(True if c[2] == 'on' else False)

			#Color
			if c[3]:
				self.lights[i].set_color(self.color[c[3]])

			#Brightness
			if c[4]:
				bri = int((int(c[4])/100.0)*254) + \
					(self.lights[i].get_bri() if c[4][0] in ('+','-') else 0)
				if bri > 254:
					bri = 254
				elif bri < 0:
					bri = 0
				self.lights[i].set_bri(bri)

			self.log.info(str(self.lights[i]))
			self.lights[i].update_light()


	def main(self):
		
		HOST = "192.168.0.98" #IP of Bristol VM
		SENSOR_HOST = '192.168.0.38'
		PORT = 5008

		conn = connection.Client(HOST, PORT)
		time_conn = connection.Client(SENSOR_HOST,PORT)


		try:
			self.log.info('Opening connection')

			conn.connect()
			self.log.info('connected!')
			time_conn.connect()
			self.log.info('connected to sensor!')

			count = 0
			while True:

				command = conn.receive_message()

				if command != None: 

					self.log.info('Received: ' + str(command))

					data = command.split('/')

					for d in data:
						if d:
							if d != 'invalid':
								start_command = timeit.default_timer()
								self.execute_command(d)
								end_command = timeit.default_timer()

							time_conn.send_message('Received-'+ str(count))
							self.log.info('Time from sensor to controller: '
								+ str(end_command-start_command))
							count += 1
				else:
					break

		except KeyboardInterrupt:
			self.log.debug('\nINTERRUPTED BY USER')	
		except Exception as e:
			self.log.debug("ERROR: " + str(e))
		finally:
			conn.destroy()
			time_conn.destroy()
			self.log.debug('Finishing program')



if(__name__ == '__main__'):
	try:
		parser = argparse.ArgumentParser(description='Actuator Node Logging')

		parser.add_argument('--log-level', action="store", type=str,
			choices=["critical", "error", "warning", "info", "debug", "notset"],
			default="info", help='Select the log level of the program.')

		parser.add_argument('--verbose', default=False, action = 'store_true',
			help='Select whether to output logs to the console.')

		args = parser.parse_args()

	except Exception as e:
		print 'ERROR PARSING ARGUMENTS'
	act = Actuator(args)
	act.main()
