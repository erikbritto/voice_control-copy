import speech_recognition as sr
import os
import socket
from itertools import groupby


def validate_command(command):
	c = command.split()

	if c[0] == 'turn' and c[1] in ('on', 'off'):
		return command
	elif c[0] == 'color':
		colors = ('red', 'blue', 'white', 'yellow', 'green', 'pink')
		if c[1] in colors:
			return command
	elif c[0] == 'brightness':
		try:
			return c[0] + ' ' + str(int(c[1]))
		except ValueError:
			return False
	elif c[0] == 'lamp':
		try:
			return c[0] + ' ' + str(int(c[1]))
		except ValueError:
			return False
	return False
   

def convert_commands(input_string):
		
	directives = ('turn', 'color', 'brightness', 'lamp')

	commands = input_string.split()

	commands_formatted = [i + ' ' + j for i,j in zip(commands[:-1],commands[1:]) if i in directives]

	commands_formatted = [x[0] for x in groupby(commands_formatted)]

	valid = [validate_command(i) for i in commands_formatted]

	return [i + ' ' for i in valid if i]


def main():
	HOST = '192.168.0.37'  # Socket server's IP (actuator)
	PORT = 57000

	r = sr.Recognizer()
	#p = os.system("pgrep python") # Check if python is running

	#Open socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	print 'OPENING SOCKET'
	audio = 0
	duration = 0
	offset = 0
	pos = 0
	#i = 0


	#try:
	while True:#(p == 0):
		#if(p == 0):
		text = ''
		with sr.AudioFile("audio.wav") as source:
			source.audio_reader.setpos(pos)
			audio = r.record(source,duration=duration,offset=offset)
			
			#print i 
			#i += 1

			#print pos

			#p = os.system("pgrep python")
			#print p

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
				s.send(c)

			duration = duration + 10
			offset = offset + 1
			pos = source.audio_reader.tell()


	# except Exception as e:
	# 	#print "Exception: " + str(e) 
	# finally:
	# 	#Close socket
	# 	s.close()
	# 	quit()
			
main()