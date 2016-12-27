class Command():

	options = ('on_off', 'light_number', 'color', 'brightness_number')

	def __init__(self, command, MAX_LAMPS = 3):
		self.command = command
		self.valid = False
		self.cmd_var = { 
						'on_off' : '',
						'light_number' : 'all,',
						'color'  : '',
						'brightness_number'  : ''
					}
		self.MAX_LAMPS = MAX_LAMPS

		self.__store_intents()
		self.__validate_command()


	def set_command(self, command, MAX_LAMPS = 3):
		self.command = command
		self.valid = False
		self.cmd_var = { 
						'on_off' : '',
						'light_number' : 'all,',
						'color'  : '',
						'brightness_number'  : ''
					}
		self.MAX_LAMPS = MAX_LAMPS		

		self.__store_intents()
		self.__validate_command()



	def __store_intents(self):

		#TODO log confidence
		
		entities = {}
		
		#TODO
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
		if not (self.cmd_var['color'][:-1] in ('red', 'blue', 'white', 'yellow', 'green', 'pink')):
			self.cmd_var['color'] = ''

		#Check if brightness value is in range
		if self.cmd_var['brightness_number'] != '':
			if not (0 <= int(self.cmd_var['brightness_number'][:-1]) <= 100):
				self.cmd_var['brightness_number'] = ''

		lights = (self.cmd_var['light_number'][:-1]).split(',')
		n_lights = []
		for l in lights:
			if l == 'all':
				n_lights = [l]
				break
			elif ( 0 <= int(l) <= self.MAX_LAMPS):
				n_lights.append(l)
		self.cmd_var['light_number'] = ','.join(n_lights) + ','



	def format_command(self):

		if self.valid:
			command = ['light']
		else:
			command = ['']

		for opt in self.options:
			command.append(self.cmd_var[opt][:-1])
		return command


	def isValid(self):
		return self.valid


	def get_text(self):
		return self.text