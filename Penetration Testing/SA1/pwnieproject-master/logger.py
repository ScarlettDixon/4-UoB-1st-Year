#!/usr/bin/env python
 
import queue
import threading
import time
import socket
from abc import ABC, abstractmethod

###########################################################################################################################################################################
## Threaded logger so that we can log information from multiple sources in one place safely
## Log entries are stored in a queue and written every second or so.
## This class is abstract; instantiate either a FileLogger (for log files) or a ListenLogger (for listening for a TCP connection and logging to a connected entity when present)
###########################################################################################################################################################################
class Logger(ABC):
	
	def loggingthread_func(self):

		## call abstract openfd method. This returns a file descriptor.
		## allows us to open all sorts, including files and sockets.
		## Best to do it here rather than in the constructor, as it might block for somethings (sockets!)
		self.log_f = self.openfd()

		while True:

			try:
				message = self.toLog.get(True, 1)
				self.writeTofd(message)
			except queue.Empty as e:
				# there was nothing in the queue
				time.sleep(self.frequency)

			if(self.die == True):
				while(not self.toLog.empty()):
					message = self.toLog.get(True, 1)
					self.writeTofd(message)

				if(self.log_f != None):
					self.log_f.close()
				break		
				
	def __init__(self):
		
		self.toLog = queue.Queue() # Our FIFO queue 

		self.die = False
	
		## How long to sleep() if the logging queue is empty; the frequency of writes
		## Default to 1s, but extending classes may change this
		self.frequency = 1;

		## Once our logging thread opens our log target, this will be a fd. Until then, None.
		## If it's None we can throw away log data instead of putting it into a queue that might never be looked at...
		self.log_f = None

		# start the thread that will read from the FIFO queue and save its contents to the log file.
		self.log_thread = threading.Thread(target=self.loggingthread_func)
		self.log_thread.start()

	# abstract method to open the file/socket
	@abstractmethod
	def openfd(self):
		pass

	# abstract method to write to the file/socket
	@abstractmethod
	def writeTofd(self, message):
		pass

	# add messages to the log
	def addAndPrint(self, message):
		self.add(message)
		print(message)	

	def add(self, message):
		self.toLog.put(message)
	
	def kill(self):
		self.die = True

###########################################################################################################################################################################
## Logger implementation for writing to files
###########################################################################################################################################################################
class FileLogger(Logger):

	def __init__(self, filename):
		
		## set our desired log file name and then call the super constructor. That'll call openfd() for us to open the file.
		self.logFileName = filename
		super().__init__()

	# implement abstract method to open the file
	def openfd(self):
			return open(self.logFileName, "a")

	# implement abstract method to write to the file
	def writeTofd(self, message):
		self.log_f.write(message + "\n")
		self.log_f.flush()

###########################################################################################################################################################################
## Logger implementation for writing to a TCP client connection; useful for exporting data to another program
###########################################################################################################################################################################
class ListenLogger(Logger):

	def __init__(self, name, log, listen_port, hexmode):
		
		## set the port we want to listen to and then call the super constructor. That'll call openfd() for us to establish the connection.
		self.listen_port = listen_port
		self.client_addr = ""
		self.listen_socket = None
		self.hexmode = hexmode

		# logs within logs within logs
		# this should be the file logger used by the rest of the program
		self.log = log
		self.name = name + "[ListenLogger]"
		super().__init__()

	# implement abstract method to open the listening socket
	def openfd(self):
		# Get the client (i.e. game-side) socket ready to go...
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_socket.bind(("127.0.0.1", self.listen_port))
		self.listen_socket.listen(1)
		
		# accept() blocks until the client connects
		try:
			client_socket, self.client_addr = self.listen_socket.accept()
		except:
			self.log.addAndPrint(self.name + ": Accept failed.")
			return

		self.log.add(self.name + ": Accepted log client " + str(self.client_addr) + " on " + str(self.listen_port))

		return client_socket

	# implement abstract method to write to the socket
	def writeTofd(self, message):
		if(self.hexmode):
			self.log_f.send((message.hex() + "\n").encode('ascii'))
		else:
			self.log_f.send(message)

	# Override the add method - we shouldn't put data in our logging queue if there's nowhere to write it to yet.
	# We may not have an inbound connection (nor may ever), so if there's no connection, throw away the data - otherwise our queue may end up massive.
	def add(self, message):
		if(self.log_f != None):
			self.toLog.put(message)
			

	# Override the kill method to close our socket.
	def kill(self):
		if(self.log_f != None):
			self.log_f.close()
		if(self.listen_socket != None):
			self.listen_socket.shutdown(socket.SHUT_RD) 
			self.listen_socket.close()
 
		super().kill()
		self.log.add(self.name + ": " + str(self.client_addr) + " Dying. ")

###########################################################################################################################################################################
## Writing to CSVs for mapping data
## Specialised and simple, so don't extend Logger
##########################################################################################################################################################################
class CSVMaker():

	def loggingthread_func(self):

		while True:

			# write the whole dictionary
			if (self.timeSinceLastPurge >= 1):
				self.log_f = open(self.filename, "w")
				for identifier, position in self.csv.items():
					self.log_f.write(identifier + "," + position + "\n")
		
				self.log_f.flush()
				self.log_f.close()

			if(self.doPurge):
				if(self.timeSinceLastPurge == 5):
					self.csv = {}
					self.timeSinceLastPurge = 0
				
			time.sleep(1)

			if(self.doPurge):
				self.timeSinceLastPurge += 1

			if(self.die == True):
				self.log_f.close()
				break	

	def __init__(self, filename, doPurge):
		
		self.filename = filename
		self.csv = {}
		self.log_f = 0
		self.die = False

		self.doPurge = doPurge

		# we need to purge the list every now and again - this will time us
		if(not doPurge):
			self.timeSinceLastPurge = 1			
		else:
			self.timeSinceLastPurge = 0
		

		self.log_thread = threading.Thread(target=self.loggingthread_func)
		self.log_thread.start()

	def update(self, monsterid, positionstring):
		self.csv[monsterid] = positionstring

	def kill(self):
		self.die = True