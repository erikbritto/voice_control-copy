import speech_recognition as sr
import os
import connection
from itertools import groupby


def valid_command(command):
	MAX_LAMPS = 3		#Maximum number of lamps connected to bridge

	c = command.split()

	try:
		if c[0] == 'turn' and c[1] in ('on', 'off'):
			return True
		elif c[0] == 'color':
			colors = ('red', 'blue', 'white', 'yellow', 'green', 'pink')
			if c[1] in colors:
				return True
		elif c[0] == 'brightness':
			if 0 <= int(c[1]) <= 100:		#Check if brightness value is in range
				return True
		elif c[0] == 'lamp':
			if 0 <= int(c[1]) <= MAX_LAMPS:		#Check if brightness value is in range
				return True
	except Exception:
		return False
	
	return False
   

def convert_commands(input_string):
		
	directives = ('turn', 'color', 'brightness', 'lamp')

	commands = input_string.split()

	numbers = { 'one' : '1', 'two' : '2', 'to' : '2', 'too' : '2', 'three' : '3', 'tree' : '3'}

	for i,c in enumerate(commands):
		if c in numbers.keys():
			commands[i] = numbers[c]

	#Make tuples from pairs of recognized words
	commands_formatted = [i + ' ' + j for i,j in zip(commands[:-1],commands[1:]) if i in directives]

	#Remove duplicate commands
	commands_formatted = [x[0] for x in groupby(commands_formatted)]


	#Create list of valid commands separated by comma
	return [cmd + ',' for cmd in commands_formatted if valid_command(cmd)]



def main():
	HOST = '192.168.0.37'  # Socket server's IP (actuator)
	PORT = 57000

	audio = 0
	duration = 0
	offset = 0
	pos = 0
	
	r = sr.Recognizer()
	
	#Create and open the connection
	
	s = connection.Client(HOST, PORT)
	s.connect()

	try:
		while True:

			try:
				with sr.AudioFile("audio.wav") as source:
					source.audio_reader.setpos(pos)
					# audio = r.record(source,duration=duration,offset=offset)
					audio = r.record(source)
				os.remove('audio.wav')
				print 'Ready to receive new file'
			except IOError:
				#print 'Cannot open file audio.wav'
				pass
			else:
				text = ''
				try:
					text = r.recognize_google(audio, language="en-US")
				except sr.UnknownValueError:
					print("Google Speech Recognition could not understand audio")
				except sr.RequestError as e:
					print("Could not request results from Google Speech Recognition service; {0}".format(e))

				if text:
					print("Text: \n\n" + text)
					
					valid_commands = convert_commands(text)

					for c in valid_commands:
						print 'Sending: '+ c
						# #Send command
						s.send_message(c)

					# duration = duration + 10
					# offset = offset + 1
					# pos = source.audio_reader.tell()


	except KeyboardInterrupt:
		# Close connection
		s.destroy()
		print 'Finishing program'


if(__name__ == '__main__'):
	main()