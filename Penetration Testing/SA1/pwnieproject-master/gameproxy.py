#!/usr/bin/env python
 
import socket
import threading
import logger
import parser
import time

## All the fancy connection bits happen here
class GameProxy:

	################################################################################
	## Both client and server connections behave in exactly the same way - THIS WAY.
	################################################################################
	def feed_parser(self, name, inConnection, outConnection, parser):
		
		socket_error = False	
		while (not socket_error):

			# get some data (on our non-blocking socket)	
			data = None
				
			while (data == None and not socket_error):
				try:
					# get data
					data = inConnection.recv(1024)

					# if there wasn't data, recv would have thrown an exception. If we get here, it didn't, so there MAY be data to add to the parser.
					# However, if the server isn't CONNECTED AT ALL any more, then recv will repeatedly return data of length 0 - don't parse that, obviously.
					if(len(data) == 0): 
						raise EOFError(name + ": Socket appears to have been disconnected.")

					# we should have data to parse.
					parser.addRawData(data)

				except BlockingIOError as e:
					pass
					# There was no data
					# perhaps a tiny nap?
					# time.sleep(0.05)

				except Exception as e:
						# Something else went wrong with our recv of the socket - this is not good.
						self.log.addAndPrint(name + ": Critical socket error when receiving data: " + str(e))
						socket_error = True
						break
				
				# Regardless, quickly check if the parser has finished making any packets, and pass them on if it has
				packet = parser.getPacket()
				while (packet != None):

					try:
						outConnection.send(packet)
					except Exception as e:
						self.log.addAndPrint(name + ": Critical client socket error when sending data: " + str(e))
						socket_error = True
					packet = parser.getPacket()
				
				# make sure we're still allowed to live
				if(self.die):
					socket_error = False
					break

		# Disconnected
		self.log.addAndPrint(name + ": Disconnected.")
		self.die = True
		return

	################################################################################################################################################
	## Server thread - basically identical to the client thread running in __init__, but with a different parser and reversed sockets.
	################################################################################################################################################
	def server_thread_func(self):


		self.serverParser = parser.Parser(self.name + "[Server Parser]", self.log, False, self, True)
		self.feed_parser(self.name + "[Server>>Client]", self.server_socket, self.client_socket, self.serverParser)	
		
		# disconnected - thread dies, so kill the whole proxy and return to the switchboard
		self.die = True
		return
	
	################################################################################################################################################
	## Constructor
	## We use the Switchboard thread for this port to run the client side of the connection, and start a server thread for that side.#
	## The sockets have already been prepared for us by the Switchboard - we'll tag directly onto them.
	################################################################################################################################################
	def __init__(self, log, client_socket, server_socket, name):

		# Set up our stuff
		self.log = log
		self.client_socket = client_socket
		self.server_socket = server_socket
		self.name = name
		self.die = False

		# set up another thread for the server>>client
		self.server_thread = threading.Thread(target=self.server_thread_func)
		self.server_thread.start()

		# set up a parser thread to deal with the packets
		self.clientParser = parser.Parser(self.name + "[Client Parser]", self.log, True, self, False)
	
		self.feed_parser(self.name + "[Client>>Server]", self.client_socket, self.server_socket, self.clientParser)	

		# Disconnected
		# this will return control of this thread back to the Switchboard, which will re-establish the port for our later use if we return to this game server.
		return

	def kill(self):
		self.die = True
