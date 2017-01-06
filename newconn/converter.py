#Networking utils
import connection
#Logging utils
import logging
import vc_logging
#Argument parsing utils
import argparse

import os
# import pyaudio
import wave
import timeit
from threading import Lock
from threading import Thread
import speech_recognition as sr
from Queue import Queue
from command import Command
from wit import Wit


#Google Cloud dependencies
import base64
import json
from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials


DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
				 'version={apiVersion}')


def get_speech_service():
	credentials = GoogleCredentials.get_application_default().create_scoped(
		['https://www.googleapis.com/auth/cloud-platform'])
	http = httplib2.Http()
	credentials.authorize(http)

	return discovery.build(
		'speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)


def encode_command(command):
		if command[0] != '':
			return '|'.join(command)+'/'
		else:
			return ''


def multi_replace(d, string):
	list_of_string = string.split()

	for i,s in enumerate(list_of_string):
		if s in d.keys():
			list_of_string[i] = d[s]

	return ' '.join(list_of_string)


class AudioProcessing():


	def __init__(self, args):#, FORMAT = pyaudio.paInt16, CHANNELS = 1, RATE = 16000):
		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")
		
		self.HOST = ''
		self.PORT_RECV = int(args.port_recv)
		self.PORT_SEND = int(args.port_send)
		
		# self.FORMAT = FORMAT
		# self.CHANNELS = CHANNELS
		# self.RATE = RATE

		# self.WIDTH = pyaudio.get_sample_size(FORMAT)
		self. MAX_CONNECTIONS = 1

		self.AUDIO_QUEUE = Queue()

		self.LOCK = Lock()

		self. SAVED_FILES = 0
		#self.RECOGNIZERS = (self.wit,self.google,self.bing)
		self.RECOGNIZERS = (self.wit,self.bing)

		#self.services = ('Wit.ai', 'Google', 'Bing', 'Google Cloud')
		self.services = ('Wit.ai', 'Bing', 'Cloud')
		self.keys = {
			'Wit.ai' : "YY76MAH6SUSS2QHLHOHWMVXIACVBRWSJ", # Wit.ai keys are 32-character uppercase alphanumeric strings
			'Bing'   : "584daf06114c4695b82c234182bac530"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
		}

		self.similar = {
						'to'		: 'two',
						'too'		: 'two',
						'tree'		: 'three',
						'tri'		: 'three',
						'breakfast' : 'brightness',
						'retina'	: 'brightness',
						'like'		: 'light',
						'lite'		: 'light'
						}

#######################################################################
#Debug Functions
#######################################################################

	# #Save audio to file
	# def save_speech(self, frames, filename = 'audio'):
	# 	""" Saves mic data to temporary WAV file. Returns filename of saved 
	# 		file """

	# 	self.LOCK.acquire()
	# 	filename = filename + '_' + str(self.SAVED_FILES)
	# 	self.SAVED_FILES += 1
	# 	self.LOCK.release()

	# 	# writes data to WAV file
	# 	wf = wave.open(filename + '.wav', 'wb')
	# 	wf.setnchannels(self.CHANNELS)
	# 	wf.setsampwidth(self.WIDTH)
	# 	wf.setframerate(self.RATE)
	# 	wf.writeframes(b''.join(frames))
	# 	wf.close()
	# 	return filename + '.wav'


	# #Play audio
	# def play(self, audio):
	# 	p = pyaudio.PyAudio()

	# 	stream = p.open(format = self.FORMAT,
	# 					channels = self.CHANNELS,
	# 					rate = self.RATE,
	# 					output=True,)
		
	# 	for d in audio:
	# 		stream.write(d)

	# 	stream.stop_stream()
	# 	stream.close()

	# 	p.terminate()

#######################################################################

# ============================== RECOGNIZERS =========================================


	def google_cloud(self,audio,d):

		try:
			speech_content = base64.b64encode(audio)

			service = get_speech_service()
			service_request = service.speech().syncrecognize(
				body={
					'config': {
						'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
						'sampleRate': 16000,  # 16 khz
						'languageCode': 'en-US',  # a BCP-47 language tag
						"speech_context": {
							"phrases":["on", "off", 'lamp', "lamps", 'light', "lights",
							 "brightness", "color", 'two', 'three',
							'red', 'blue', 'white', 'yellow', 'green', 'pink']
						}

					},
					'audio': {
						'content': speech_content.decode('UTF-8')
						}
					})

			start = timeit.default_timer()
			response = service_request.execute()
			stop = timeit.default_timer()

			json_response = response['results'][0]['alternatives'][0]

			confidence = json_response['confidence']
			original_speech = json_response['transcript']
			
			running_time = stop-start

			speech = multi_replace(self.similar,original_speech)

			wit_start = timeit.default_timer()
			client = Wit(access_token=self.keys['Wit.ai'])
			message = client.message(msg = speech, verbose = True)
			wit_end = timeit.default_timer()
			
			d['Cloud'] = message
			end = timeit.default_timer()

			# self.log.warning('Google Cloud:' + original_speech
			# 	+ '\nRunning time: ' + str(running_time)
			# 	+ '\nWit intent processing running time: ' + str(wit_end - wit_start)
			# 	+ '\nTotal running time: ' + str(end-start))

			log_message = 'Google Cloud (running time ' + str(running_time) \
				+ ', confidence ' + str(confidence) + '):\n' + original_speech \
				+ '\nWit intent processing running time: ' + str(wit_end - wit_start) \
				+ '\nTotal running time: ' + str(end-start)

			self.log.info(log_message)

		except Exception as e:
			d['Cloud'] = {}
			self.log.debug("Google Cloud ERROR: " + str(e))


	def google(self, audio,d):

		r = sr.Recognizer()
		# recognize speech using Google Speech Recognition
		try:

			start = timeit.default_timer()
			response = r.recognize_google(audio)['alternatives'][0]
			stop = timeit.default_timer()

			confidence = response['confidence']
			original_speech = response['transcript']

			running_time = stop-start

			speech = multi_replace(self.similar,original_speech)

			self.log.info('Google (running time ' + str(stop-start) 
					+ ', confidence ' + str(confidence) + '): ' + speech)
			
			wit_start = timeit.default_timer()
			client = Wit(access_token=self.keys['Wit.ai'])
			message = client.message(msg = speech, verbose = True)
			wit_end = timeit.default_timer()


			d['Google'] = message
			end = timeit.default_timer()

			log_message = 'Google (running time ' + str(running_time) \
				+ ', confidence ' + str(confidence) + '):\n' + original_speech \
				+ '\nWit intent processing running time: ' + str(wit_end - wit_start) \
				+ '\nTotal running time: ' + str(end-start)

			self.log.info(log_message)

		except sr.UnknownValueError:
			d['Google'] = {}
			self.log.debug("Google Speech Recognition could not understand audio")
		except sr.RequestError as e:
			d['Google'] = {}
			self.log.debug("Could not request results from \
				Google Speech Recognition service; {0}".format(e))
		except Exception as e:
			d['Google'] = {}
			self.log.debug("Google - ERROR: " + str(e))


	def wit(self, audio,d):
		r = sr.Recognizer()
		# recognize speech using Wit.ai
		
		try:
			start = timeit.default_timer()
			speech = r.recognize_wit(audio, key=self.keys['Wit.ai'], show_all = True)
			stop = timeit.default_timer()
			d['Wit.ai'] = speech

			running_time = stop-start

			self.log.info('Wit.ai (running time ' + str(running_time) + '):\n'+ speech['_text'])

			# self.log.warning('Wit:' + speech['_text']
			# 	+ '\nTotal running time: ' + str(running_time))

		except sr.UnknownValueError:
			d['Wit.ai'] = {}
			self.log.debug("Wit.ai could not understand audio")
		except sr.RequestError as e:
			d['Wit.ai'] = {}
			self.log.debug("Could not request results from Wit.ai service; {0}".format(e))
		except Exception as e:
			d['Wit.ai'] = {}
			self.log.debug("Wit - ERROR: " + str(e))


	def bing(self, audio,d):
		r = sr.Recognizer()
		# recognize speech using Microsoft Bing Voice Recognition

		try:
			start = timeit.default_timer()
			response = (r.recognize_bing(audio, key=self.keys['Bing'], show_all = True))['results'][0]
			stop = timeit.default_timer()

			confidence = response['confidence']
			original_speech = response['lexical']
			
			running_time = stop-start

			speech = multi_replace(self.similar,original_speech)

			wit_start = timeit.default_timer()
			client = Wit(access_token=self.keys['Wit.ai'])
			message = client.message(msg = speech, verbose = True)
			wit_end = timeit.default_timer()

			d['Bing'] = message
			end = timeit.default_timer()

			# self.log.warning('Bing:' + original_speech
			# 	+ '\nRunning time: ' + str(running_time)
			# 	+ '\nWit intent processing running time: ' + str(wit_end - wit_start)
			# 	+ '\nTotal running time: ' + str(end-start))

			log_message = 'Bing (running time ' + str(running_time)\
				+ ', confidence ' + str(confidence) + '):\n' + original_speech\
				+ '\nWit intent processing running time: ' + str(wit_end - wit_start)\
				+ '\nTotal running time: ' + str(end-start)

			self.log.info(log_message)


		except sr.UnknownValueError:
			d['Bing'] = {}
			self.log.debug("Microsoft Bing Voice Recognition could not understand audio")
		except sr.RequestError as e:
			d['Bing'] = {}
			self.log.debug("Could not request results from Microsoft Bing Voice Recognition \
				service; {0}".format(e))
		except Exception as e:
			d['Bing'] = {}
			self.log.debug("Bing - ERROR: " + str(e))


# ===================================== RECOGNIZERS =================================


	def receive_audio(self, recv_socket, save = False, play = False):
		print('CONNECTION FROM: ' + str(recv_socket.addr[0]) + ":" 
								  + str(recv_socket.addr[1]))

		#recv_audio = []
		recv_audio = ''
		#Receive audio from socket until the connection closes on the other end
		data = recv_socket.receive_message()
		while data:
			#recv_audio.append(data)
			recv_audio += data
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

		for f in features[1]:
			if f != 'all' and f != '':
				if result[1] == 'all' or len(result[1]) < len(f):
					result[1] = f

		for f in features[2]:
			if f == 'on':
				result[2] = f
				break

		#As long as it only supports one color and one brightness value at a time
		result[3] = result[3].split(',')[0]
		result[4] = result[4].split(',')[0]
		return result


	def speechToText(self, send_socket):
		print('Starting Recognizer thread')

		while True:
			frames = self.AUDIO_QUEUE.get()
			
			if frames == None:
				break
			
			speech_threads = []
			result_dict = {}


			t = Thread(target=self.google_cloud, args=(frames,result_dict))
			speech_threads.append(t)


			#audioData = sr.AudioData(b''.join(frames),self.RATE, self.WIDTH)
			audioData = sr.AudioData(frames,16000, 2L)
			self.AUDIO_QUEUE.task_done()


			for recognizer in self.RECOGNIZERS:
				t = Thread(target=recognizer, args=(audioData,result_dict))
				speech_threads.append(t)

			for t in speech_threads:
				t.start()
			
			for t in speech_threads:
				t.join()

			self.log.debug("[LISTEN FOR SPEECH] FINISHED RECOGNIZER THREADS")

			formatted_commands = []
			for i in self.services:
				if result_dict[i]:
					c = Command(result_dict[i])
					formatted_commands.append(c.format_command())
					self.log.info(i + ': ' + str(formatted_commands[-1]))
				else:
					formatted_commands.append(['','','','',''])


			command_list = self.analyze_commands(formatted_commands)
			text = encode_command(command_list)

			if text:
				self.log.info("Command: \n\n" + text)
				send_socket.send_message(text)


	def main(self, save = False, play = False):

		#Open receiving end
		recv_socket = connection.Server(self.HOST, self.PORT_RECV)
		recv_socket.connect()

		#Open sending end
		send_socket = connection.Server(self.HOST, self.PORT_SEND)
		send_socket.connect()
		send_socket.accept()
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
		parser.add_argument('--port-recv', action="store", default=5007, help='Select the port through which the program will receive data.')
		parser.add_argument('--port-send', action="store", default=5008, help='Select the port through which the program will send data.')
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

		ap.main()
	except KeyboardInterrupt:
		print('Finishing')
	except Exception as e:
		print('ERROR: ' + str(e))
