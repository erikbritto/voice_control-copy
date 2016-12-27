#Networking utils
import connection
#Logging utils
import logging
import vc_logging
#Argument parsing utils
import argparse

import os
import pyaudio
import wave
import timeit
from threading import Lock
from threading import Thread
import speech_recognition as sr
from Queue import Queue
from command import Command
from wit import Wit


def encode_command(command):
	return '|'.join(command)+'/'



class AudioProcessing():


	def __init__(self, args, CHUNK = 1024, FORMAT = pyaudio.paInt16, CHANNELS = 1, RATE = 16000):
		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")

		self.CHUNK = CHUNK
		self.FORMAT = FORMAT
		self.CHANNELS = CHANNELS
		self.RATE = RATE

		self.WIDTH = pyaudio.get_sample_size(FORMAT)
		self. MAX_CONNECTIONS = 1

		self.AUDIO_QUEUE = Queue()

		self.LOCK = Lock()

		self. SAVED_FILES = 0
		self.RECOGNIZERS = (self.wit,self.google,self.bing)

		self.services = ('Wit.ai', 'Google', 'Bing')
		self.keys = {
			'Wit.ai' : "YY76MAH6SUSS2QHLHOHWMVXIACVBRWSJ",
			'Google' : None,
			'Bing'   : "584daf06114c4695b82c234182bac530"
		}

#######################################################################
#Debug Functions
#######################################################################

	#Save audio to file
	def save_speech(self, frames, filename = 'audio'):
		""" Saves mic data to temporary WAV file. Returns filename of saved 
			file """

		self.LOCK.acquire()
		filename = filename + '_' + str(self.SAVED_FILES)
		self.SAVED_FILES += 1
		self.LOCK.release()

		# writes data to WAV file
		wf = wave.open(filename + '.wav', 'wb')
		wf.setnchannels(self.CHANNELS)
		wf.setsampwidth(self.WIDTH)
		wf.setframerate(self.RATE)
		wf.writeframes(b''.join(frames))
		wf.close()
		return filename + '.wav'


	#Play audio
	def play(self, audio):
		p = pyaudio.PyAudio()

		stream = p.open(format = self.FORMAT,
						channels = self.CHANNELS,
						rate = self.RATE,
						output=True,)
		
		for d in audio:
			stream.write(d)

		stream.stop_stream()
		stream.close()

		p.terminate()

#######################################################################

# ============================== RECOGNIZERS =========================================

	def google(self, audio,d):

		r = sr.Recognizer()
		# recognize speech using Google Speech Recognition
		try:
			# for testing purposes, we're just using the default API key
			# to use another API key, use 
			# 'r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")'
			# instead of 'r.recognize_google(audio)'
			start = timeit.default_timer()
			speech = r.recognize_google(audio)
			stop = timeit.default_timer()
			print 'google: '+speech

			client = Wit(access_token=self.keys['Wit.ai'])
			message = client.message(msg = speech, verbose = True)

			d['Google'] = message

		except sr.UnknownValueError:
			d['Google'] = ''
			self.log.debug("Google Speech Recognition could not understand audio")
		except sr.RequestError as e:
			d['Google'] = ''
			self.log.debug("Could not request results from \
				Google Speech Recognition service; {0}".format(e))


	def wit(self, audio,d):
		r = sr.Recognizer()
		# recognize speech using Wit.ai
		
		# Wit.ai keys are 32-character uppercase alphanumeric strings
		WIT_AI_KEY = "YY76MAH6SUSS2QHLHOHWMVXIACVBRWSJ"
		try:
			start = timeit.default_timer()
			speech = r.recognize_wit(audio, key=WIT_AI_KEY, show_all = True)
			stop = timeit.default_timer()
			print 'wit: '+ speech['_text']
			d['Wit.ai'] = speech
		except sr.UnknownValueError:
			d['Wit.ai'] = ''
			self.log.debug("Wit.ai could not understand audio")
		except sr.RequestError as e:
			d['Wit.ai'] = ''
			self.log.debug("Could not request results from Wit.ai service; {0}".format(e))


	def bing(self, audio,d):
		r = sr.Recognizer()
		# recognize speech using Microsoft Bing Voice Recognition
		
		# Microsoft Bing Voice Recognition API keys 32-character
		# lowercase hexadecimal strings
		BING_KEY = "584daf06114c4695b82c234182bac530"
		try:
			start = timeit.default_timer()
			speech = r.recognize_bing(audio, key=BING_KEY)
			stop = timeit.default_timer()
			print 'bing: '+ speech

			client = Wit(access_token=self.keys['Wit.ai'])
			message = client.message(msg = speech, verbose = True)

			d['Bing'] = message

		except sr.UnknownValueError:
			d['Bing'] = ''
			self.log.debug("Microsoft Bing Voice Recognition could not understand audio")
		except sr.RequestError as e:
			d['Bing'] = ''
			self.log.debug("Could not request results from Microsoft Bing Voice Recognition \
				service; {0}".format(e))


# ===================================== RECOGNIZERS =================================


	def receive_audio(self, recv_socket, save = False, play = False):
		print('CONNECTION FROM: ' + str(recv_socket.addr[0]) + ":" 
								  + str(recv_socket.addr[1]))

		recv_audio = []
		#Receive audio from socket until the connection closes on the other end
		data = recv_socket.receive_message()
		while data:
			recv_audio.append(data)
			data = recv_socket.receive_message()

		self.AUDIO_QUEUE.put(recv_audio)

		if save:
			self.save_speech(recv_audio)
		if play:
			self.play(recv_audio)



	def analyze_commands(self, formatted_commands):
		features = zip(*formatted_commands)
		result = ['','','','','']
		for i, f in enumerate(features):
			for j in f:
				if j != '':
					result[i] = j
					break
		for f in features[2]:
			if f != 'all' and f != '':
				result[2] = f
				break
		return result


	def encode_command(self, command):
		if command[0] != '':
			return '|'.join(command)+'/'
		else:
			return ''


	def speechToText(self , send_socket):
		print('Starting Recognizer thread')

		r = sr.Recognizer()
		rec_functions = (r.recognize_wit, r.recognize_google, r.recognize_bing)

		while True:
			frames = self.AUDIO_QUEUE.get()
			
			if frames == None:
				break
			
			audioData = sr.AudioData(b''.join(frames),self.RATE, self.WIDTH)
			self.AUDIO_QUEUE.task_done()

			speech_threads = []
			result_dict = {}


			for recognizer in self.RECOGNIZERS:
				t = Thread(target=recognizer, args=(audioData,result_dict))
				speech_threads.append(t)

			for t in speech_threads:
				t.start()
			
			for t in speech_threads:
				t.join()

			# for key, value in result_dict.iteritems():
			# 	self.log.info(key+' ('+str(value[0])+' seconds)'+value[1])


			formatted_commands = []
			for i in self.services:
				if result_dict[i] != '':
					c = Command(result_dict[i])
					formatted_commands.append(c.format_command())
				else:
					formatted_commands.append(['','','','',''])				


			command_list = self.analyze_commands(formatted_commands)
			text = self.encode_command(command_list)

			if text:
				self.log.info("Command: \n\n" + text)
				
				send_socket.send_message(text)

	def main(self, save = False, play = False):
		#Try with 127.0.0.1
		HOST_RECV = ''

		HOST_SEND = '192.168.0.37'  # Socket server's IP (actuator)

		PORT = 57000

		#Open receiving end
		recv_socket = connection.Server(HOST_RECV, PORT)
		recv_socket.connect()

		#Open sending end
		send_socket = connection.Client(HOST_SEND, PORT)
		send_socket.connect()
		#Opening threads
		stt_thread = Thread(target=self.speechToText, args = (send_socket,))
		stt_thread.start()


		try:
			while True:
				self.log.info("\nListening for incoming connections...")

				recv_socket.accept()
				#Open a new thread for each incoming connection
				arguments = (recv_socket, save, play)
				newConnThread = Thread(target=self.receive_audio, args=arguments)
				newConnThread.start()

		except KeyboardInterrupt as e:
			raise e
		except Exception as e:
			raise e
		finally:
			self.log.debug('\nCLOSING SOCKETS')
			recv_socket.destroy()
			send_socket.destroy()
			self.AUDIO_QUEUE.put(None)



if __name__ == '__main__':
	try:
		parser = argparse.ArgumentParser(description='Voice Recording Logging')
		parser.add_argument('--log-level', action="store", type=str,
						choices=["critical", "error", "warning", "info", "debug", "notset"],
						default="info", help='Select the log level of the program.')
		parser.add_argument('--verbose', default=False, action = 'store_true',
						help='Select whether to output logs to the console.')

		args = parser.parse_args()
	except Exception as e:
		print 'ERROR PARSING ARGUMENTS'
	try:
		ap = AudioProcessing(args)

		ap.main(save = True)
	except KeyboardInterrupt:
		print('Finishing')
	except Exception as e:
		print('ERROR: ' + str(e))