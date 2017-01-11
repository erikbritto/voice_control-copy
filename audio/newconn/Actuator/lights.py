#Lights Api
from beautifulhue.api import Bridge

class Light():
	""" This class contains the lights information and a funtion to update them
	
	This class contains a list of dictionaries containing the state of each lamp
	connected. It provides functions to obtain and update information on status,
	color and brighness, and a funtion to update the lights with the current
	information
	"""

	def __init__(self, light, light_ip = '192.168.0.87' ):
		
		self.bridge = Bridge(device={'ip': light_ip}, 
			user={'name': 'go3D6jUyb3yLQFP0tcPmJ3xzNPIC507T1SL2pnir'})

		self.light = light

		self.set_state()

		self.set_sat(254)


	def __str__(self):
		return 'Light ' + str(self.light) + \
			': on = ' + str(self.get_status()) +\
			', color (hue) = ' + str(self.get_color()) + \
			', brightness = ' + str(self.get_bri())

	def get_state(self):
		return self.state


	def set_state(self):
		resource = {'which': self.light, 'verbose': True}

		self.state = self.bridge.light.get(resource)['resource']['state']


	def set_status(self, statusLamp):
		self.state['on'] = statusLamp

	def get_status(self):
		return self.state['on']

	def set_color(self, color):
		self.state['hue'] = color

	def get_color(self):
		return self.state['hue']

	def set_bri(self, bri):
		self.state['bri'] = bri

	def get_bri(self):
		return self.state['bri']

	def set_sat(self, sat):
		self.state['sat'] = sat

	def get_sat(self):
		return self.state['sat']

	def update_light(self):
		resource = {
			'which': self.light,
			'data': {
				'state':{
							'on': self.get_status(),
							'hue': self.get_color(),
							'bri': self.get_bri(),
							'sat' : self.get_sat()
						}
			}
		}
		self.bridge.light.update(resource)