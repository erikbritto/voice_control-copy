class Command():

	options = ('light_number', 'on_off','color', 'brightness_number')
	colors = ('red', 'blue', 'white', 'yellow', 'green', 'pink')

	bri = {
		'up':'+20',
		'down' : '-20',
		'high':'100',
		'low' : '0',
		'medium' : '50'
	}

	def __init__(self, command, MAX_LAMPS = 3):
		"""Constructor for class
		
		Sets the command, stores its intents and validates.
		
		Arguments:
			command {[command]} -- List with each intent
		
		Keyword Arguments:
			MAX_LAMPS {number} -- Maximum number of lamps (default: {3})
		"""
		self.command = command
		self.valid = False
		self.cmd_var = { 
						'light_number' : 'all,',
						'on_off' : '',
						'color'  : '',
						'brightness_number'  : ''
					}
		self.MAX_LAMPS = MAX_LAMPS

		self.__store_intents()
		self.__validate_command()


	def set_command(self, command, MAX_LAMPS = 3):
		"""Sets a new command
		
		Performs the same action as the constructor. To be used if in case of
		reutilizing the same object instance
		
		Arguments:
			command {[command]} -- List with each intent
		
		Keyword Arguments:
			MAX_LAMPS {number} -- Maximum number of lamps (default: {3})
		"""
		self.command = command
		self.valid = False
		self.cmd_var = { 
						'light_number' : 'all,',
						'on_off' : '',
						'color'  : '',
						'brightness_number'  : ''
					}
		self.MAX_LAMPS = MAX_LAMPS		

		self.__store_intents()
		self.__validate_command()



	def __store_intents(self):
		"""Stores intents in the dictinary cmd_var"""

		entities = {}
		
		self.text = self.command['_text']
		entities = self.command['entities']

		if 'intent' in entities.keys():
			if entities['intent'][0]['value'] == 'change_lamp_state':
				self.valid = True

		for opt in self.options:
			if opt in entities.keys():
				self.cmd_var[opt] = ''
				for n in entities[opt]:
					self.cmd_var[opt] += str(n['value'])+','


	def __validate_command(self):

		#Checks if lights are valid
		lights = (self.cmd_var['light_number'][:-1]).split(',')
		n_lights = []
		for l in lights:
			if l == 'all':
				n_lights = [l]
				break
			elif ( 0 <= int(l) <= self.MAX_LAMPS):
				n_lights.append(l)
		self.cmd_var['light_number'] = ','.join(n_lights) + ','

		#Checks if color is valid
		if not (self.cmd_var['color'][:-1] in self.colors):
			self.cmd_var['color'] = ''

		#Checks if brightness is valid
		if self.cmd_var['brightness_number'] != '':
			#Checks if brightness is one of the default values
			if self.cmd_var['brightness_number'][:-1] in self.bri.keys():
				self.cmd_var['brightness_number'] = self.bri[
						self.cmd_var['brightness_number'][:-1]]+','

			#Check if brightness value is in range
			elif not (0 <= int(self.cmd_var['brightness_number'][:-1]) <= 100):
				self.cmd_var['brightness_number'] = ''


	def format_command(self):
		"""Returns a list with the recognized commands
		
		The return list consists of five positions. The first position is the
		word light, that is present if the intent is 'change_lamp_state'.
		The second position is a list with the lights selected or all.
		The third position is the state - 'on' or 'off'
		The fourth position is the color
		The fifth position is the brightness value.
		If any of the commands were not found, its position is set with ''
		
		Returns:
			[str] -- The list with the 
		"""

		if self.valid:
			command = ['light']
		else:
			command = ['']

		for opt in self.options:
			command.append(self.cmd_var[opt][:-1])
		return command


	def is_valid(self):
		return self.valid


	def get_text(self):
		return self.text