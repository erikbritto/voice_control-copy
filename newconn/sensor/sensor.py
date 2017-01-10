################################################################################
# silence_analysys() and audio_int() functions adapted from
# https://github.com/spadgenske/ANDY/blob/master/src/stt.py
################################################################################

#Argument parsing utils
import argparse
#Networking utils
import connection
#Logging utils
import logging
import vc_logging
#Audio libraries
import pyaudio
import wave
import audioop
from collections import deque
import math
import time
import timeit

from threading import Thread
from Queue import Queue

class AudioUtils():

	"""
	
	This class represents the audio recording functions.
		
	"""

	def __init__(self, args, 
		CHUNK = 1024, FORMAT = pyaudio.paInt16, CHANNELS = 1, RATE = 16000, 
		THRESHOLD = 2500, SILENCE_LIMIT = 2, PREV_AUDIO = 1, SAVE = False):
		
		"""
		Initialization method for class AudioUtils.
		
		Defines the constants needed throughout the program.
		
		Keyword Arguments:
			CHUNK {number} -- CHUNKS of bytes to read each time from mic 
								(default: {1024})
			FORMAT {[type]} -- [description] (default: {pyaudio.paInt16})
			CHANNELS {number} -- [description] (default: {1})
			RATE {number} -- [description] (default: {16000})
			THRESHOLD {number} -- The threshold intensity that defines silence 
								and noise signal (an int. lower than THRESHOLD
								is silence) (default: {2500})
			SILENCE_LIMIT {number} -- Silence limit in seconds. The max ammount
								of seconds where only silence is recorded.
								When this time passes the recording finishes
								and the file is delivered. (default: {2})
			PREV_AUDIO {number} -- Previous audio (in seconds) to prepend.
								When noise is detected, how much of previously
								recorded audio is prepended. This helps to
								prevent chopping the beggining of the phrase.
								(default: {1})
		"""

		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")

		#Audio parameters
		self.WIDTH = pyaudio.get_sample_size(FORMAT)
		self.CHUNK = CHUNK
		self.FORMAT = FORMAT
		self.CHANNELS = CHANNELS
		self.RATE = RATE
		###

		#Volume analysys parameters
		self.THRESHOLD = THRESHOLD
		self.SILENCE_LIMIT = SILENCE_LIMIT
		self.PREV_AUDIO = PREV_AUDIO
		###

		#Queue to hold audio to be sent
		self.audioQueue = Queue()
		
		#Queue to hold times at which audio has stopped being sent
		self.timeQueue = Queue()

		#Flags
		self.save = SAVE
		self.finish = False


	def comm_confirmation(self):
		"""Receieves confirmation of action on Actuator and logs total time
		
		Opens a server connection to the Actuator in order to receive
		confirmation on action on its side. Gets the time of receival of the
		message and uses along with the time in which audio stopped being sent
		to get the total roundtrip time
		"""

		self.log.debug('=================== \
			Starting thread comm_confirmation ===================')
		self.act = connection.Server('', 5008)
		self.act.connect()
		self.act.accept()

		count = 0

		while True:

			#Finishes if flag is set
			if self.finish:
				break

			#Receives data from Actuator
			command = self.act.receive_message()

			#Stores the time of message arrival
			arrival = timeit.default_timer()
			
			#Checks if connection was not closed on the other side
			if command != None:
				dispatch_time = self.timeQueue.get()

				#Checks for keyboard interruption on main thread
				if dispatch_time == None:
					break

				self.log.info("command received:  " + command)
				parts = command.split('-')
				if int(parts[1]) != count:
					self.log.debug('Received command number ' + parts[1] +\
					 ' but waiting for command number ' + str(count) +\
					 "'s status")

				#Roundtrip time
				time_dif = arrival - dispatch_time

				self.log.info("Command number " + str(count) +\
					" execution time:  " + str(time_dif))
				count +=1
			else:
				self.log.debug('Actuator connection closed on the other side')
				break


	def silence_analysys(self):
			self.log.info( "* Listening mic. ")
			cur_data = ''  # current chunk  of audio data
			rel = self.RATE / self.CHUNK
			slid_win = deque(maxlen = self.SILENCE_LIMIT * rel)

			#Prepend audio from self.PREV_AUDIO secs before noise was detected
			prev_audio = deque(maxlen = self.PREV_AUDIO * rel) 
			started = False
			audio2send = []


			while True:
				cur_data = self.audioQueue.get()

				#Checks for keyboard interruption on main thread
				if cur_data == None:
					break

				slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

				#Mic is not silent
				if(sum([x > self.THRESHOLD for x in slid_win]) > 0):

					#New recording has started
					if(not started):
						self.log.info("Starting record of phrase")
						#VM's IP and port
						self.s = connection.Client('192.168.0.98', 5007)
						self.s.connect()

						started = True
						self.s.send_message(''.join(prev_audio))

					self.s.send_message(cur_data)

					if self.save:
						audio2send.append(cur_data)

				#Recording was happening and mic became silent
				elif (started is True):
					#Save time of command issuing
					inittime = timeit.default_timer()
					self.timeQueue.put(inittime)

					self.log.info("Finished")
					self.s.destroy()

					if self.save:
						self.save_speech(list(prev_audio) + audio2send)
						audio2send = []

					# Reset all
					started = False
					slid_win = deque(maxlen = self.SILENCE_LIMIT * rel)
					prev_audio = deque(maxlen=0.5 * rel) 

					self.log.info("Listening ...")
				#Mic is silent
				else:
					prev_audio.append(cur_data)


	def callback(self,in_data, frame_count, time_info, status):
		#Puts current chunk in queue
		self.audioQueue.put(in_data)
		return (in_data, pyaudio.paContinue)


	def listen_for_speech(self , num_phrases = -1):
		"""

		Listens to Microphone, extracts phrases from it and sends it to 
		Google's TTS service and returns response. a "phrase" is sound 
		surrounded by silence (according to threshold). num_phrases controls
		how many phrases to process before finishing the listening process 
		(-1 for infinite). 


		Keyword Arguments:
			num_phrases {number} -- Number of phrases the recorder will 
									be ready to record. (default: {1})
		"""

		#Open stream
		self.s = connection.Connection()

		#Creates thread to receive Actuator confirmation
		comm_watch = Thread(target = self.comm_confirmation)
		comm_watch.start()

		#Creates thread to analyze the audio volume
		silence_thread = Thread(target=self.silence_analysys)
		silence_thread.start()

		p = pyaudio.PyAudio()

		stream = p.open(format = self.FORMAT,
						channels = self.CHANNELS,
						rate = self.RATE,
						input = True,
						frames_per_buffer = self.CHUNK,
						stream_callback = self.callback)
		try:

			stream.start_stream()

			while stream.is_active():
				time.sleep(0.1)

		except KeyboardInterrupt:
			self.log.debug("INTERRUPTED BY USER: Finished")
		except Exception as e:
			self.log.debug('ERROR: ' + str(e))
		finally:
			self.finish = True
			self.audioQueue.put(None)
			self.timeQueue.put(None)
			self.s.destroy()
			self.log.info("* Done recording")

			stream.stop_stream()
			stream.close()
			p.terminate()


	def save_speech(self, data):
		"""
		Saves mic data to temporary WAV file. Returns filename of saved file.

		Arguments:
			data {bytes} -- Audio

		Returns:
			filename {str} -- Name of saved file
		"""

		filename = 'audio'
		# writes data to WAV file
		data = ''.join(data)
		wf = wave.open(filename + '.wav', 'wb')
		wf.setnchannels(self.CHANNELS)
		wf.setsampwidth(self.WIDTH)
		wf.setframerate(self.RATE)
		wf.writeframes(data)
		wf.close()
		return filename + '.wav'


	def audio_int(self, num_samples = 25, offset = 1000):
		""" Gets average audio intensity of your mic sound. You can use it to
			get average intensities while you're talking and/or silent. The
			average is the avg of the 20% largest intensities recorded.
		"""

		self.log.info("Getting intensity values from mic.")
		p = pyaudio.PyAudio()
		self.log.info("RATE == " + str(self.RATE))
		stream = p.open(format = self.FORMAT,
						channels = self.CHANNELS,
						rate = self.RATE,
						input = True,
						frames_per_buffer = self.CHUNK)

		values = [math.sqrt(abs(audioop.avg(stream.read(self.CHUNK), 4))) 
				  for x in range(num_samples)] 
		values = sorted(values, reverse=True)
		r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
		self.log.info(" Finished ")
		self.log.info(" Average audio intensity is "+ str(r))
		stream.close()
		p.terminate()

		self.THRESHOLD = r + offset
		return r


if(__name__ == '__main__'):
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

	au = AudioUtils(args)
	au.audio_int(offset = 500)
	au.listen_for_speech()  # listen to mic.