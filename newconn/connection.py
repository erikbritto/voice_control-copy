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
		""" Constructor method for class Connect.

		Opens a network socket on the Host and Port specified by the user

		Args:
			HOST (str): Host machine to the socket, defaults to empty (localhost).
			PORT (int): Port in which the socket will be running. Defaults to 57000.
		""" 

		print '[CONNECTION] OPENING SOCKET'
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.HOST = HOST
			self.PORT = PORT
			self.connected = False
			self.log = logging.getLogger("vc_logger")
		except socket.error as e:
			self.log.debug('[CONNECTION] SOCKET ERROR: ' + str(e))
			quit()
		except socket.herror as e:
			self.log.debug('[CONNECTION] SOCKET HERROR: ' + str(e))
			quit()
		except socket.gaierror as e:
			self.log.debug('[CONNECTION] SOCKET GAIERROR: ' + str(e))
			quit()
		except socket.timeout as e:
			self.log.debug('[CONNECTION] SOCKET TIMEOUT: ' + str(e))
			quit()
		except Exception as e:
			self.log.debug('[CONNECTION] ERROR OPENING SOCKET: ' + str(e))
			quit()
			
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
			self.log.debug('[SERVER INIT] SOCKET ERROR (SETTING SOCKET OPTIONS): ' + str(e))
			quit()
		except socket.herror as e:
			self.log.debug('[SERVER INIT] SOCKET HERROR (SETTING SOCKET OPTIONS): ' + str(e))
			quit()
		except socket.gaierror as e:
			self.log.debug('[SERVER INIT] SOCKET GAIERROR (SETTING SOCKET OPTIONS): ' + str(e))
			quit()
		except socket.timeout as e:
			self.log.debug('[SERVER INIT] SOCKET TIMEOUT (SETTING SOCKET OPTIONS): ' + str(e))
			quit()
		except Exception as e:
			self.log.debug('[SERVER INIT] ERROR SETTING SOCKET OPTIONS: ' + str(e))
			quit()
		

	def connect(self,  connections=1):
		""" Binds the socket to a port and start listening for connections on it. 
		
		Keyword Arguments:
			connections {number} -- Maximum number of connections the socket should be able to accept simultaneously. (default: {1})
		"""

		try:
			self.log.info(str((self.HOST, self.PORT)))
			self.s.bind((self.HOST, self.PORT))
			self.s.listen(connections)
		except IOError as e:
			self.log.debug('[SERVER CONNECT] IOError: ' + str(e))
		except socket.error as e:
			self.log.debug('[SERVER CONNECT] SOCKET ERROR: ' + str(e))
			quit()
		except socket.herror as e:
			self.log.debug('[SERVER CONNECT] SOCKET HERROR: ' + str(e))
			quit()
		except socket.gaierror as e:
			self.log.debug('[SERVER CONNECT] SOCKET GAIERROR: ' + str(e))
			quit()
		except socket.timeout as e:
			self.log.debug('[SERVER CONNECT] SOCKET TIMEOUT: ' + str(e))
			quit()
		except KeyboardInterrupt:
			raise
			quit()
		except Exception as e:
			self.log.debug('[SERVER CONNECT] ERROR BINDING SOCKET: ' + str(e) )
			quit()

	def disconnect(self):
		""" Closes an open connection on the socket. """

		self.log.info('[SERVER DISCONNECT] CLOSING CONNECTION')
		try:
			if self.connected:
				self.conn.close()
		except Exception as e:
			self.log.debug('[SERVER DISCONNECT] ERROR CLOSING CONNECTION: ' + str(e))

	def accept(self): 
		""" Accept a connection on socket. """

		self.log.info('[SERVER ACCEPT] Opening connection')

		self.conn, self.addr = self.s.accept()
		self.log.info('[SERVER ACCEPT] CONNECTION FROM: ' + str(self.conn) + ":" 
								  + str(self.addr))
		self.connected = True

	#============================================================================ SEND FROM SERVER

	def send_message(self, message=''):
		""" Send a message to a server
		
		Keyword Arguments:
			message {str} -- Message to be sent. (default: {''})
		"""

		try:
			# print 'Sending message'
			###############################

			self.conn.sendall(message)

			###############################
		except IOError as e:
			self.log.debug('[SERVER SEND] ERROR: ' + str(e))
		except socket.error as e:
			self.log.debug('[SERVER SEND] SOCKET ERROR: ' + str(e))
		except socket.herror as e:
			self.log.debug('[SERVER SEND] SOCKET HERROR: ' + str(e))
		except socket.gaierror as e:
			self.log.debug('[SERVER SEND] SOCKET GAIERROR: ' + str(e))
		except socket.timeout as e:
			self.log.debug('[SERVER SEND] SOCKET TIMEOUT: ' + str(e))
		except KeyboardInterrupt:
			self.log.debug('[SERVER SEND] Finished')
		else:
			self.log.debug('[SERVER SEND] Finished sending')

	#============================================================================ RECV FROM SERVER

	def receive_message(self, nbytes = 1024):
		""" Receives a message on a socket.
		
		
		Args:
			nbytes {number} -- number of bytes in message (default: {1024})

		Returns:
			data   {str}  -- message received
		"""

		try:
			# self.log.info('receiving message')
			###############################

			data = self.conn.recv(nbytes)
			if not data: #Socket has closed on the other end
				self.log.debug('[SERVER RECV] ERROR: Connection was closed on the other side')
				self.disconnect()
			return data

			###############################
		except IOError as e:
			self.log.debug('[SERVER RECV] IOError: ' + str(e))
		except socket.error as e:
			self.log.debug('[SERVER RECV] SOCKET ERROR: ' + str(e))
		except socket.herror as e:
			self.log.debug('[SERVER RECV] SOCKET HERROR: ' + str(e))
		except socket.gaierror as e:
			self.log.debug('[SERVER RECV] SOCKET GAIERROR: ' + str(e))
		except socket.timeout as e:
			self.log.debug('[SERVER RECV] SOCKET TIMEOUT: ' + str(e))
		except Exception as e:
			self.log.debug('[SERVER RECV] ERROR: error receiving message')
		else:
			self.log.info('[SERVER RECV] Finished sending')

	def destroy(self):
		""" Destructor method for class.

		Closes the socket opened on constructor.
		"""
		try:
			self.disconnect()
			self.log.info('[SERVER] CLOSING SOCKET')
			self.s.close()
		except Exception as e:
			self.log.debug('[SERVER] ERROR CLOSING SOCKET: ' + str(e))


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
		
		try:
			self.log.debug('[CLIENT CONNECT] CONNECTING TO: ' + self.HOST + ' ON PORT: ' + str(self.PORT))
			self.s.connect((self.HOST, self.PORT))
			self.connected = True
		except IOError as e:
			self.log.debug('[CLIENT CONNECT] IOError: ' + str(e))
		except socket.error as e:
			self.log.debug('[CLIENT CONNECT] SOCKET ERROR: ' + str(e))
		except socket.herror as e:
			self.log.debug('[CLIENT CONNECT] SOCKET HERROR: ' + str(e))
		except socket.gaierror as e:
			self.log.debug('[CLIENT CONNECT] SOCKET GAIERROR: ' + str(e))
		except socket.timeout as e:
			self.log.debug('[CLIENT CONNECT] SOCKET TIMEOUT: ' + str(e))
		except Exception as e:
			self.log.debug('[CLIENT CONNECT] EXCEPTION: ' + str(e))

	#============================================================================ SEND FROM CLIENT


	def send_message(self, message=''):
		""" Send a message to a server
		
		Keyword Arguments:
			message {str} -- Message to be sent. (default: {''})
		"""

		try:
			# print 'Sending message'
			###############################

			self.s.sendall(message)

			###############################
		except IOError as e:
			self.log.debug('[CLIENT SEND] IOError: ' + str(e))
		except socket.error as e:
			self.log.debug('[CLIENT SEND] SOCKET ERROR: ' + str(e))
		except socket.herror as e:
			self.log.debug('[CLIENT SEND] SOCKET HERROR: ' + str(e))
		except socket.gaierror as e:
			self.log.debug('[CLIENT SEND] SOCKET GAIERROR: ' + str(e))
		except socket.timeout as e:
			self.log.debug('[CLIENT SEND] SOCKET TIMEOUT: ' + str(e))
		except KeyboardInterrupt:
			self.log.debug('[CLIENT SEND] KEYBOARD INTERRUPT Finished')
		else:
			self.log.debug('[CLIENT SEND] Finished sending')

	#============================================================================ RECV FROM CLIENT
	
	def receive_message(self, nbytes = 1024):
		""" Receives a message on a socket.
		
		
		Args:
			nbytes {number} -- number of bytes in message (default: {1024})

		Returns:
			data   {str}  -- message received
		"""

		try:
			# self.log.info('receiving message')
			###############################

			data = self.s.recv(nbytes)
			if not data: #Socket has closed on the other end
				self.log.debug('[CLIENT RECV] ERROR: Connection was closed on the other side')
				self.destroy()
			return data

			###############################
		except IOError as e:
			self.log.debug('[CLIENT RECV] IOError: ' + str(e))
			quit()
		except socket.error as e:
			self.log.debug('[CLIENT RECV] SOCKET ERROR: ' + str(e))
		except socket.herror as e:
			self.log.debug('[CLIENT RECV] SOCKET HERROR: ' + str(e))
		except socket.gaierror as e:
			self.log.debug('[CLIENT RECV] SOCKET GAIERROR: ' + str(e))
		except socket.timeout as e:
			self.log.debug('[CLIENT RECV] SOCKET TIMEOUT: ' + str(e))
		except Exception as e:
			self.log.debug('[CLIENT RECV] ERROR: error receiving message')
		else:
			self.log.info('[CLIENT RECV] Finished sending')

	#============================================================================ END OF CLIENT
	def destroy(self):
		""" Destructor method for class.

		Closes the socket opened on constructor.
		"""
		self.log.info('[CLIENT] CLOSING SOCKET')
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
	