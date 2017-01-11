#Networking utils
import connection
#Logging utils
import logging
import vc_logging
#Argument parsing utils
import argparse

#Timing
import timeit

#Threads
from threading import Thread
from Queue import Queue

#Speech Recognition
from sphinx import Sphinx

#Intent and Command
from command import Command
from intent import Intent


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


	def __init__(self, args):
		vc_logging.init_logger(level = args.log_level, verbose = args.verbose)
		self.log = logging.getLogger("vc_logger")
		
		self.HOST = ''
		self.PORT_RECV = int(args.port_recv)
		self.PORT_SEND = int(args.port_send)

		self. MAX_CONNECTIONS = 1

		self.AUDIO_QUEUE = Queue()

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


# ============================= RECOGNIZERS ====================================

	def sphinx_recognize(self,audio,sphinx):
		try:
			sphinx_start = timeit.default_timer()
			original_speech = sphinx.recognize(audio)
			sphinx_stop = timeit.default_timer()

			running_time = sphinx_stop-sphinx_start

			speech = multi_replace(self.similar,original_speech)
			
			intent_start = timeit.default_timer()
			i = Intent(speech)
			message = i.parse_intents()
			intent_end = timeit.default_timer()


			sphinx_end = timeit.default_timer()

			log_message = 'Sphinx (running time ' + str(running_time) + '):\n'\
				+ original_speech \
				+ '\nIntent processing running time: ' \
				+ str(intent_end - intent_start) \
				+ '\nTotal running time: ' + str(sphinx_end-sphinx_start)

			self.log.info(log_message)
			return message
		except Exception as e:
			self.log.debug('Error: ' + str(e))
			return {}

# ================================ /RECOGNIZERS ================================


	def receive_audio(self, recv_socket):
		self.log.info('CONNECTION FROM: ' + str(recv_socket.addr[0]) + ":" 
								  + str(recv_socket.addr[1]))

		recv_audio = ''
		#Receive audio from socket until the connection closes on the other end
		data = recv_socket.receive_message()
		while data:
			recv_audio += data
			data = recv_socket.receive_message()

		self.AUDIO_QUEUE.put(recv_audio)


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

		#If it only supports one color and one brightness value at a time
		result[3] = result[3].split(',')[0]
		result[4] = result[4].split(',')[0]
		return result


	def speechToText(self, send_socket):
		print('Starting Recognizer thread')
		sphinx = Sphinx()

		while True:
			frames = self.AUDIO_QUEUE.get()

			if frames == None:
				break

			result = self.sphinx_recognize(frames,sphinx)

			self.log.debug("[LISTEN FOR SPEECH] FINISHED RECOGNIZER THREADS")

			formatted_commands = []

			if result:
				c = Command(result)
				formatted_commands.append(c.format_command())
				self.log.info(str(formatted_commands[-1]))
			else:
				formatted_commands.append(['','','','',''])


			command_list = self.analyze_commands(formatted_commands)
			text = encode_command(command_list)

			if text:
				self.log.info("Command: \n\n" + text)
				send_socket.send_message(text)
			else:
				send_socket.send_message('invalid/')


	def main(self):

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
				newConnThread = Thread(target=self.receive_audio, 
										args=(recv_socket,))
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

		parser.add_argument('--port-recv', action="store", default=5007, 
			help='Select the port through which the program will receive data.')

		parser.add_argument('--port-send', action="store", default=5008, 
			help='Select the port through which the program will send data.')

		parser.add_argument('--log-level', action="store", type=str,
			choices=["error", "warning", "info", "debug", "notset"],
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
