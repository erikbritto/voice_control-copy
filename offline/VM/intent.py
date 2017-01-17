import string
import re
from words_to_numbers import WordsToNumbers
from itertools import groupby


class Intent():
	"""Class to perform intent recognition
	
	[description]
	
	Variables:
		number_words {tuple} -- [description]
		options {tuple} -- [description]
	"""


	number_words = ( "zero", "one", "two", "three", "four", "five", "six",
			"seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
			"fourteen","fifteen","sixteen", "seventeen", "eighteen", "nineteen",
			"twenty","thirty", "forty", "fifty", "sixty", "seventy", "eighty",
			"ninety","hundred", "thousand", "million", "billion", "trillion")
	

	options = ('light_number', 'on_off','color', 'brightness_number')


	def __init__(self, text = ''):
		"""Constructor for the class
		
		Keyword Arguments:
			text {str} -- Text to retrieve intents (default: {''})
		"""

		self.text = text.lower()

		self.intent_keywords = { 
			'intent' : ['light','lights', 'lamp','lamps'],
			'on_off' : ['on','off'],
			'color' : ['red','blue','yellow','green','pink','white']
		}

		self.intents = []

		self.wtn = WordsToNumbers()


	def set_text(self, text):
		"""Sets the text to be used converting all letters to lowercase.
		
		Arguments:
			text {str} -- The text to be used
		"""
		self.text = text.lower()


	def get_text(self):
		"""Gets the text being used
		
		Returns:
			str -- The text being used
		"""
		return self.text


	def __convert_numbers(self,s):
		"""Converts all written number in the string to int numbers
		
		Converts all individual text numbers to int and then adds the 
		adjacent ones if the one on the left is bigger.
		'one hundred' would be converted to '1 100' and 'eighty three' to '83'
		
		Arguments:
			s {str} -- The string with the numbers.
		"""

		aux_l = []

		#Creates a list with each individual number converted from text to int
		for w in s.split():
			try:
				n = self.wtn.parse(w)
				aux_l.append(str(n))
			except KeyError:
				aux_l.append(w)


		i = len(aux_l) - 1
		new_aux_l = []
		last_len=0
		last_n = 0
		number = False
		while i >= 0:
			try:
				cur = aux_l[i] #Gets current element in the list
				cur_len = len(cur) #Gets lenght of the element0
				cur_n = int(cur) #Converts element to int

				#Checks if current elment is bigger than the previous
				if cur_len > last_len:
					#Adds both numbers and sets previous number with the result
					last_len = cur_len
					last_n += cur_n
					number = True
				else: #Current element is of same size or smaller

					#Appends previous element to new list and sets current as
					#the the previous number
					new_aux_l.append(str(last_n))
					last_len = cur_len
					last_n = cur_n

			except ValueError as e:
				#The current element is not a number

				#If last elment was a number appends it to the list
				if number:
					new_aux_l.append(str(last_n))

				#Appends current element
				new_aux_l.append(cur)

				#Reset
				last_len = 0
				last_n = 0
				number = False

			i -= 1

		return ' '.join(new_aux_l[::-1])


	def parse_intents(self):
		"""[summary]
		
		[description]
		"""

		#Converts synonyms of light to light
		s = re.sub('|'.join(self.intent_keywords['intent'][1:]), 'light',
			self.text)

		#Remove extra words
		s = re.sub('( and )|,|&', ' ', s)
		s = re.sub(' +',' ', s)

		#Removes repeated adjacent words
		s = ' '.join([x[0] for x in groupby(s.split())])


		#Separates in multiple commands, one for each appearance of 'light'
		list_of_lights = []
		i = 0
		while i >= 0:
			i = string.rfind(s,'light')
			list_of_lights.append(s[i:])
			s = s[:i]

		#Fixes the order of the list
		list_of_lights = list_of_lights[:-1][::-1]

		#If there are no words 'light', reverts the list to the original text
		if list_of_lights == []:
			list_of_lights = [self.text]
		
		for l in list_of_lights:

			#Converts all the numbers in the string
			l = self.__convert_numbers(l)

			dict_intents = {}
			list_of_words = l.split()

			#Fill the dictionary with the intents defined in intent_keywords
			for w in list_of_words:
				for intent_key,intent_value in self.intent_keywords.iteritems():
					if w in intent_value:
						dict_intents[intent_key] = [{'value': w}]
						
		
			#Sets 'on_off' to 'on' if does not exists and the intents does
			if 'intent' in dict_intents.keys():
				dict_intents['intent'] = [{'value':'change_lamp_state'}]
				if 'on_off' not in dict_intents.keys():
					dict_intents['on_off'] = [{'value':'on'}]
			
			#Finds all numbers referring to lights in the string
			l_numbers = re.search('(light)( [0-9]+)+', l)
			if l_numbers:
				dict_intents['light_number'] = [{'value': i} 
					for i in l_numbers.group(0)[6:].split()]

			#Finds the brightness defined in the string if it exists
			bri_number = re.search(
				'(brightness) (([0-9]+)|(up|down|high|low|medium))', l)
			if bri_number:
				dict_intents['brightness_number'] = \
					[{'value':bri_number.group(2)}]

			self.intents.append(dict_intents)


		return {'_text':self.text, 'entities' : self.intents[0]}


	def get_intents(self):
		"""Gets a list with the intents
		
		Returns:
			[list] -- list with the intents
		"""
		return self.intents
