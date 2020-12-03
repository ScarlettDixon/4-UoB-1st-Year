#!/usr/bin/env python

import gameproxy
import threading
import socket

class Switchboard:

	SERVERADDRESS = ""

	def listenThread(self, index):

		port = index + 3000
		while(not self.die):

			self.log.addAndPrint("[Switchboard] New listener starting for " + str(port) + "; Waiting for socket.")
			
			# Get the client (i.e. game-side) socket ready to go...
			connect_ok = False
			while(not connect_ok):
				#print("Trying to re-establish...")
				try:
					self.switchboard_listeners[index] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					self.switchboard_listeners[index].bind(("0.0.0.0", port))
					connect_ok = True
				except Exception as e:
					#print("Error: " + str(e))
					pass

			self.log.addAndPrint("[Switchboard] Successful bind to socket. Listening: " + str(port))
			self.switchboard_listeners[index].listen(0)
	
			# ...and the socket we'll use to connect to the server
			self.switchboard_servers[index] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			
			# accept() blocks until the client connects
			try:
				self.switchboard_clients[index], client_addr = self.switchboard_listeners[index].accept()
			except:
				# Socket was closed while we were waiting to accept() - probably the program quit.
				self.log.addAndPrint("[Switchboard] accept() failed while waiting for client connection")
				self.switchboard_listeners[index].close()
				break

			self.log.addAndPrint("[Switchboard] Game has connected from " + str(client_addr) + " to port " + str(port))

			# now that a client has connected, open a corresponding connection to the server.
			self.switchboard_servers[index].connect((Switchboard.SERVERADDRESS, port))
			self.log.addAndPrint("[Switchboard] Successfully connected to server: " + str(Switchboard.SERVERADDRESS) + ":" + str(port))
	
			# non-blocking socket works better in conjunction with the parser thread(s)
			self.switchboard_servers[index].settimeout(0.0)
			self.switchboard_clients[index].settimeout(0.0)

			# this will block until the game session has ended
			proxy = gameproxy.GameProxy(self.log, self.switchboard_clients[index], self.switchboard_servers[index], "[gameProxy:" + str(port) + "]")

			self.log.addAndPrint("[Switchboard] Proxy for " + str(port) + " stopped blocking; reclaiming socket.")

			# that proxy disconnected; clear up and restart
			self.switchboard_servers[index].close()
			self.switchboard_listeners[index].close()
			self.switchboard_clients[index].close()


	def __init__(self, log):
		self.log = log
		self.die = False

		log.addAndPrint("[Switchboard] Server target is " + Switchboard.SERVERADDRESS)

		## We need 10 threads... ew
		self.switchboard_threads = []
		self.switchboard_listeners = []
		self.switchboard_servers = []
		self.switchboard_clients = []

		for i in range(0,10):
			self.switchboard_listeners.append(0)
			self.switchboard_servers.append(0)
			self.switchboard_clients.append(0)

			self.switchboard_threads.append(threading.Thread(target=self.listenThread, args=(i,)))
			self.switchboard_threads[i].start()
		
	def kill(self):
		self.die = True
		
		
		for i in range(0,10):
			try:
				self.switchboard_listeners[i].shutdown(socket.SHUT_RD)
				self.switchboard_listeners[i].close()
				self.switchboard_servers[i].shutdown(socket.SHUT_RD)
				self.switchboard_servers[i].close()
				self.switchboard_clients[i].shutdown(socket.SHUT_RD)
				self.switchboard_clients[i].close()
			except Exception as e:
				self.log.addAndPrint("[Switchboard] Couldn't close connections of index [" + str(i) + "]")

		self.log.addAndPrint("[Switchboard] Dying...")
