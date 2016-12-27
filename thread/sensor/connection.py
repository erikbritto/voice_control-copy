import socket
import os
import logging

class Connection(object):

	""" Manages socket connections side.
	
	Attributes:
		Inherited:
			HOST (str): Host machine in which the socket has been opened.
			PORT (int): Port in which the socket has been opened.
			s (socket): Socket object.
		Self:
			conn (socket): Connection accepted on socket.
			addr (socket): Address of machine which connected on socket.
			connected (boolean): Is there an active connection on the socket?
	"""

	def __init__(self, HOST='', PORT=57000):
		''' Constructor method for class Connect.

		Opens a network socket on the Host and Port specified by the user

		Args:
			HOST (str): Host machine to the socket, defaults to empty (localhost).
			PORT (int): Port in which the socket will be running. Defaults to 57000.

		'''

		while True:

			self.log = logging.getLogger("vc_logger")
			self.log.info('OPENING SOCKET')
			try:
				self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.HOST = HOST
				self.PORT = PORT
				self.connected = False
				
				break
			except socket.error as e:
				self.log.debug('SOCKET ERROR: ' + str(e))
			except socket.herror as e:
				self.log.debug('SOCKET HERROR: ' + str(e))
			except socket.gaierror as e:
				self.log.debug('SOCKET GAIERROR: ' + str(e))
			except socket.timeout as e:
				self.log.debug('SOCKET TIMEOUT: ' + str(e))
			except Exception as e:
				self.log.debug('ERROR OPENING SOCKET: ' + str(e))
		

	def destroy(self):
		""" Destructor method for class Connection.

		Closes the socket opened on constructor.
		"""
		self.s.close()

class Server(Connection):

	""" Manages socket connections on the SERVER side.
	

	The __init__ method is inherited from super class Connection.

	Attributes:
		Inherited:
			HOST (str): Host machine in which the socket has been opened.
			PORT (int): Port in which the socket has been opened.
			s (socket): Socket object.
		Self:
			conn (socket): Connection accepted on socket.
			addr (socket): Address of machine which connected on socket.
			connected (boolean): Is there an active connection on the socket?
	"""

	def __init__(self, HOST='', PORT=57000):
		super(Server, self).__init__(HOST, PORT)
		try:
			self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error as e:
			self.log.debug('SOCKET ERROR (SETTING SOCKET OPTIONS): ' + str(e))
		except socket.herror as e:
			self.log.debug('SOCKET HERROR (SETTING SOCKET OPTIONS): ' + str(e))
		except socket.gaierror as e:
			self.log.debug('SOCKET GAIERROR (SETTING SOCKET OPTIONS): ' + str(e))
		except socket.timeout as e:
			self.log.debug('SOCKET TIMEOUT (SETTING SOCKET OPTIONS): ' + str(e))
		except Exception as e:
			self.log.debug('ERROR SETTING SOCKET OPTIONS: ' + str(e))
		

	def connect(self,  connections=1):
		""" Binds the socket to a port and start listening for connections on it. 
		
		Keyword Arguments:
			connections {number} -- Maximum number of connections the socket should be able to accept simultaneously. (default: {1})
		"""

		attempts = 0
		while True:
			try:
				print str((self.HOST, self.PORT))
				self.s.bind((self.HOST, self.PORT))
				self.s.listen(connections)

				break
			except socket.error as e:
				self.log.debug('SOCKET ERROR: ' + str(e))
			except socket.herror as e:
				self.log.debug('SOCKET HERROR: ' + str(e))
			except socket.gaierror as e:
				self.log.debug('SOCKET GAIERROR: ' + str(e))
			except socket.timeout as e:
				self.log.debug('SOCKET TIMEOUT: ' + str(e))
			except KeyboardInterrupt:
				raise
			except Exception as e:
				self.log.debug('ERROR BINDING SOCKET: ' + str(e) )

			
			print 'Attempts: ' + str(attempts)
			attempts+=1

	def disconnect(self):
		""" Closes an open connection on the socket. """

		self.log.info('CLOSING CONNECTION')
		try:
			if self.connected:
				self.conn.close()
		except Exception as e:
			self.log.debug('ERROR CLOSING CONNECTION: ' + str(e))

	def accept(self): 
		""" Accept a connection on socket. """

		self.log.info('Opening connection')

		self.conn, self.addr = self.s.accept()

		self.connected = True


	def receive_file(self, nbytes = 1024, filename = 'temp.wav', path = ''):
		""" Receives a file from socket connection.
		
		Args:
			nbytes {number} -- Number of bytes read at a time from socket. (default: {1024})
			filename {str} -- Name of the file. (default: {'temp.wav'})
			path {str} -- Path to the file. (default: {''})
		"""
		try:
			file = open(path+filename, 'w')

			#######################
			while True:
				data = self.conn.recv(nbytes)
				if not data:
					self.log.debug('ERROR: Connection was closed on the other side')
					self.disconnect()
					break

				file.write(data)
			#######################

			file.close()
		except IOError:
			self.log.debug('IO ERROR: ' + str(e))
		except Exception as e:
			self.log.debug('ERROR: ' + str(e))

	def receive_message(self, nbytes = 1024):
		""" Receives a message on a socket.
		
		
		Args:
			nbytes {number} -- number of bytes in message (default: {1024})

		Returns:
			data   {str}  -- message received
		"""

		try:
			###############################

			data = self.conn.recv(nbytes)
			if not data: #Socket has closed on the other end
				self.log.debug('ERROR: Connection was closed on the other side')
				self.disconnect()
			return data

			###############################
		except socket.error as e:
			self.log.debug('SOCKET ERROR: ' + str(e))
		except socket.herror as e:
			print 'SOCKET HERROR: ' + str(e)
		except socket.gaierror as e:
			self.log.debug('SOCKET GAIERROR: ' + str(e))
		except socket.timeout as e:
			self.log.debug('SOCKET TIMEOUT: ' + str(e))
		except Exception as e:
			self.log.debug('ERROR: error receiving message')

	def destroy(self):
		""" Destructor method for class.

		Closes the socket opened on constructor.
		"""
		try:
			self.disconnect()
			self.log.info('CLOSING SOCKET')
			self.s.close()
		except Exception as e:
			self.log.debug('ERROR CLOSING SOCKET: ' + str(e))


class Client(Connection):

	""" Manages socket connections on the CLIENT side.
	

	The __init__ method is inherited from super class Connection.

	Attributes:
		Inherited:
			HOST (str): Host machine in which the socket has been opened.
			PORT (int): Port in which the socket has been opened.
			s (socket): Socket object.
		Self:
			connected (boolean): Is there an active connection on the socket?

	"""

	def connect(self):
		""" Connect to a server on the host and port 
		
		"""
		attempts = 0
		while True:
			try:
				print 'CONNECTING TO: ' + self.HOST + ' ON PORT: ' + str(self.PORT)
				self.s.connect((self.HOST, self.PORT))
				self.connected = True
				break
			except socket.error as e:
				self.log.debug('SOCKET ERROR: ' + str(e))
			except socket.herror as e:
				self.log.debug('SOCKET HERROR: ' + str(e))
			except socket.gaierror as e:
				self.log.debug('SOCKET GAIERROR: ' + str(e))
			except socket.timeout as e:
				self.log.debug('SOCKET TIMEOUT: ' + str(e))
			except Exception as e:
				self.log.debug('ERROR CONNECTING SOCKET: ' + str(e))
				self.log.debug('Attempts: ' + str(attempts))
			attempts+=1
	
	def send_file(self, filename, path=''):
		""" Send a file to the server on a socket. 
		
		Args:
			filename {str} -- Name of the file
			path {str} -- Path to file(default: {''})
		"""

		closenow = False
		if not self.connected:
			self.connect()
			closenow = True

		try:
			self.log.debug('Sending file')
			###############################
			file = open(path+filename, 'r')

			for line in file.readlines():
				self.s.send(line)

			file.close()
			###############################
		except IOError:
			self.log.debug('ERROR: ' + str(e))
		except KeyboardInterrupt:
			self.log.debug("Finished")
		else:
			self.log.info('Finished sending')

		if closenow:
			self.destroy()

	def send_message(self, message=''):
		""" Send a message to a server
		
		Keyword Arguments:
			message {str} -- Message to be sent. (default: {''})
		"""

		try:
			###############################

			self.s.send(message)

			###############################
		except IOError:
			self.log.debug('ERROR: ' + str(e))
		except KeyboardInterrupt:
			self.log.debug('Finished')
			

	def destroy(self):
		""" Destructor method for class.

		Closes the socket opened on constructor.
		"""
		self.log.info('CLOSING SOCKET')
		self.s.close()

if __name__ == '__main__':
	try:
		s = Server()
		s.connect()
		c = Client()
		c.connect()
	except Exception as e:
		s.destroy()
		c.destroy()
	