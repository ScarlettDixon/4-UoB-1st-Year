#!/usr/bin/env python
 
import queue
import threading
import time
import logger
import packet as pkt
import struct

###########################################################################################################################################################################
## This class will parse our packets into nice data structures
## Packets are stored in a queue, where they're looked at before they're passed on.
###########################################################################################################################################################################
class Parser:

	## This "global" is only set if we are a server who has caught the first packet.
	PLAYERID = ''

	###########################################################################################################################################################################
	## Thread to take the raw data stream and convert it into packets.
	###########################################################################################################################################################################
	def packetise(self, log):
		log.addAndPrint(self.name + ": Packetiser thread started.")
		data = b''

		# (CLIENT) The first packet received from the client is our init packet. That needs to be passed on unchanged.
		# (SERVER) The first packet received from the server contains our ID - handy!
		# The second packet, and those thereafter, are lovely too. Why not count them up?
		packetTotal = 0

		while(not self.die):
			try:
				# get an element from the data stream
				# we might have some data left over after packetising last time - add our new data to the end of that 
				
	
				data = data + self.dataStreamQueue.get(True, 1)
				#print("RAW: [" + data.hex() + "]")

				# Try to process this packet (unless the Special Cases just below instruct otherwise)
				done = False

				# The first couple of packets are special - handle them separately.
				if(packetTotal == 0):								# A very special packet...
					if(self.isClient):								# ...from the client! An InitPacket for us to pass on. Always 38 bytes in length.					
						if(len(data) >= 38):
							packet = pkt.InitPacket(data[:38])
							log.addAndPrint(self.name + "Init packet; Raw: [" + packet.raw.hex() + "]")
							self.packetQueue.put(packet)	# send it on
							packetTotal = 1
							# clear it from our data
							data = b''
						else:
							## we're missing some data - wrap around and get more.
							pass
						
						# Either we got a full packet and passed it on, or we got a bit of a packet and couldn't.
						# Either way, don't go through the packetisation step - either go around and get another set of data after this, or get the second (and subsequent!) packets.
						done = True
					
					else:													# ...from the server! A packet containing our ID - have a goggle at that and pass it on. Always 22 bytes in length.
						if(len(data) >= 22):
							Parser.PLAYERID = data[:4]
							log.addAndPrint(self.name + ": Player ID is " + Parser.PLAYERID.hex())
							packet = pkt.UnknownPacket(data[:38])		
							self.packetQueue.put(packet)	# send it on
							packetTotal = 1
							# clear it from our data
							data = b''
						else:
							## we're missing some data - wrap around and get more.
							pass
		
						# again, no packetisation please
						done = True
				
							
				# The first two characters of this data will ALWAYS (hopefully) be a packet header.
				# If we don't get a whole packet, we leave it in data and wait until it's all in there before we cut it out.
				# Conversely, there may be multiple packets in this one stream - indeed, the game likes to do that a lot. We need to cut them all out separately.
				while(done == False):
					# We're gonna make a packet
					packet = None

					# We've got to instantiate the right packet object for our packet. Search for a header
					packettype = data[:2] # first two bytes are the header
					
					# check to make sure we have the full length of data for that packet - the rest of it might not be here yet.
					# The expected length is stored in the packetlist we got from our gameproxy.
					try:
						length = self.packetlist[packettype][1]
					except KeyError as e:
						# we don't know what this packet is, as it's not in our list... uh oh. We can't packetise it if we don't know how long it should be.	
						# We really must know ALL the packet types before this will work perfectly.
						# We can just packetise the whole thing raw and spit it out; however, if there are multiple packets in this data, we'll miss the ones that come after.
						# That's a shame, but we'll probably survive.
						packet=pkt.UnknownPacket(data)
						
						# check if we wanna log unknown packets being displayed
						if(self.packetlist[b'??'][2] == True):
							log.addAndPrint(self.name + ": Unknown packet [" + packet.toHex() + "]" + "; RAW [" + data.hex() + "]")

						# we used up the entirety of the data - start a new set.
						data = b''
						done = True
						
						# add the packet to the queue
						self.packetQueue.put(packet)
						
					else:
						if(length == 0):
						# some packets have a variable length (denoted 0 in Packet.packet_types[packettype] for that packet type) - let the packet figure this out for itself	

							try:							
								if(self.isClient):
									if (packettype == pkt.Packet.PACKETTYPE_FIREWEAPON):
										packet = pkt.PewPacket(data)
									elif (packettype == pkt.Packet.PACKETTYPE_CHAT):
										packet = pkt.ChatPacket(data)
									elif (packettype == pkt.Packet.PACKETTYPE_EMPTY):
										packet = pkt.EmptyPacket(data)
									elif (packettype == pkt.Packet.PACKETTYPE_KEY):
										packet = pkt.KeyPacket(data)
	
								else:
									## server packets
									if ( packettype == pkt.Packet.PACKETTYPE_SERVER_MANIFEST):
										packet = pkt.ServerManifestPacket(data)
									elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_EMPTY):
										packet = pkt.ServerEmptyPacket(data)
									elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_CHAT):
										packet = pkt.ServerChatPacket(data)
									elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_MOBILESTATUS):
										packet = pkt.ServerMobileStatusPacket(data)
									elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_MOBILETRANSFORMSTATE):
										packet = pkt.ServerMobileTransformStatePacket(data)
									elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_RECEIVEITEM):
										packet = pkt.ServerReceiveItemPacket(data)
									elif( packettype == pkt.Packet.PACKETTYPE_SERVER_PLAYERMANIFEST):
										packet = pkt.ServerPlayerManifestPacket(data)
									elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_AREATRANSITION):
										packet = pkt.ServerAreaTransitionPacket(data)

								if(packet == None):
									# there won't be any more - if the packet isn't a recognised type it'll return a length of False, and be caught above.
									# that is, assuming we put all the packet types in Packet.packet_types[] here
									log.addAndPrint(self.name + ": Stub: Variable length packet type " + packettype.decode('ascii') + " is known, but handling code is not present.")

							except pkt.IncompletePacketException as e:
								# our packet decided that it wasn't complete, so couldn't be parsed; get more data!
								log.addAndPrint(self.name + ": Incomplete packet; cycling for more data." + str(e))
								done = True		## GET MOAR
							else:
								# get the packet to tell us how to log it, and do so
								if(self.packetlist[packettype][2]):
									log.addAndPrint(packet.toLoggable())

								# add the packet to the queue
								if(packet != None):
									self.packetQueue.put(packet)
									packetTotal += 1

								# The packet will give us back anything it didn't use after it calculated its own length.
								data = packet.getRemainder()
								if(len(data) == 0):
									# if there was nothing less, clear our data (as it's all been packetised) and get more data 
									done = True
									data = b''
								else:
									# leave done as False in case there's more.
									pass

						elif(len(data) >= length):	
							# these are the constant length packets, with lengths defined in Packet.packet_types[packettype][1]
							# Check the options. The Packet object contains the key values - check the ones we care about.
							if(self.isClient):
								if (packettype == pkt.Packet.PACKETTYPE_POSITION):
									packet = pkt.PosPacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_WEAPONSWITCH):
									packet = pkt.WpnSwitchPacket(data)

								## We should NEVER get these outside of expected circumstances that are trapped elsewhere
								elif (packettype == pkt.Packet.PACKETTYPE_INITHASH):	
									packet = pkt.InitPacket(data)
									log.addAndPrint(self.name + " Problem? Received an InitPacket unexpectedly.")

								elif (packettype == pkt.Packet.PACKETTYPE_JUMP):
									packet = pkt.JumpPacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_ACTORINTERACT):
									packet = pkt.ActorInteractPacket(data)

							else:
								## server packets
								if (packettype == pkt.Packet.PACKETTYPE_SERVER_MONSTERUPDATE):
									packet = pkt.ServerMonsterUpdatePacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_SERVER_OTHERPLAYERSUPDATE):
									packet = pkt.ServerOtherPlayersUpdatePacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_SERVER_POSITION):
									packet = pkt.ServerPosPacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_SERVER_DESPAWN):
									packet = pkt.ServerDespawnPacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_SERVER_MANAUPDATE):
									packet = pkt.ServerManaUpdatePacket(data)
								elif (packettype == pkt.Packet.PACKETTYPE_SERVER_MOBILEHITPOINTSUPDATE):
									packet = pkt.ServerMobileHitpointsUpdatePacket(data)
								elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_OTHERPLAYERSGONE):
									packet = pkt.ServerOtherPlayersGonePacket(data)
								#elif ( packettype == pkt.Packet.PACKETTYPE_SERVER_TEST):
								#	packet = pkt.ServerTestPacket(data)

							if(packet == None):
								# again, that should be all of them
								log.addAndPrint(self.name + ": Stub: Packet type " + packettype.decode('ascii') + " is known, but handling code is not present.")
							else:
								# add the packet to the queue
								self.packetQueue.put(packet)
								packetTotal += 1
				
							# get the packet to tell us how to log it, and do so
							if(self.packetlist[packettype][2]):
								log.addAndPrint(packet.toLoggable())
	
							# trim our packet out of data. If data was just our packet and nothing else, this should make it '', and we're done.
							# There may be more though, so loop around again and cut out more packets if we can.
							data = data[length:]
							if(len(data) == 0):
								done = True
								data = b''
					
						else:
							# packet is incomplete. Leave what we have in data and more will be concatenated onto it next time around.
							# we know what to expect for the remaining data though
							log.addAndPrint(self.name + ": Incomplete packet received; buffering. Raw: [" + data.hex() + "]")
							done = True
							pass		

			except queue.Empty:						# Nothing to process
				#time.sleep(0.1) 		# this sleep is probably too long
				continue

		# at this point, we've been told to die	
		log.add(self.name + ": packetiser thread dying.")
			 
	###########################################################################################################################################################################
	## Thread to take individual packets and analyse them according to rules we're interested in.
	###########################################################################################################################################################################	
	def analysePackets(self, log):
		log.addAndPrint(self.name + ": Packet analyser thread started.")

		# flags used by haxxxx
		self.whereami = False				# client
		self.nearbynotify = False 			# server only needs this
		self.serverteleportpos = None		# client
		self.rserverteleportpos = None   # client

		while(not self.die):

			try:
				packet = self.packetQueue.get(True, 1)		# Get a WHOLE Packet object (blocks for 1s)
				send = True

				## The Magic Happens Here
				## We can check what kind of packet we got, and do some work based on.
				## If, after doing some work, we want to prevent that packet being sent, then set send to False.
				## (useful when intercepting chat commands - we don't need to show other people we're cheating in chat ;))

				## lovely chat commands
				if(packet.packettype == pkt.Packet.PACKETTYPE_CHAT):
					if(packet.chat == "/whereami"):
						self.whereami = True
						send = False
					elif(packet.chat == "/radar"):
						self.parent.serverParser.nearbynotify = not self.parent.serverParser.nearbynotify
						log.addAndPrint(self.name + "Toggling radar to " + str(self.parent.serverParser.nearbynotify))
						send = False
					elif(packet.chat == "/psychicshopping"):
						self.poke("7")
						send = False
					elif(packet.chat[:7] == "/pewpew"):						
						self.pew(packet.chat)
						send = False
					elif(packet.chat == "/piratekey"):
						log.addAndPrint("Activating the pirate chest.")
						self.chatback("[PROXY] Avast! Pirate shinies!")
						key = pkt.KeyPacket.PIRATEKEY
						packet = pkt.KeyPacket(pkt.Packet.PACKETTYPE_KEY + struct.pack('<H', len(key)) + key.encode('ascii'))
					elif(len(packet.chat) >= 5 and packet.chat[:5] == "/poke"):
						log.addAndPrint("Giving [" + packet.chat[6:] + "] a good poke.")
						self.poke(packet.chat[5:])
						send = False
					elif(len(packet.chat) >= 9 and packet.chat[:9] == "/servertp"):
						if(self.serverteleportpos == None):
							self.serverteleportpos = packet.chat[10:]
							log.addAndPrint(self.name + "Activating ServerTeleport; target is " + self.serverteleportpos)
						else:
							self.serverteleportpos = None
							log.addAndPrint(self.name + "ServerTeleport disengaged; returning to client-reported position.")
						send = False
					elif(len(packet.chat) >= 10 and packet.chat[:10] == "/rservertp"):
						if(self.rserverteleportpos == None):
							self.rserverteleportpos = packet.chat[11:]
							log.addAndPrint(self.name + "Activating RelativeServerTeleport; target is " + self.rserverteleportpos)
						else:
							self.rserverteleportpos = None
							log.addAndPrint(self.name + "RelativeServerTeleport disengaged; returning to client-reported position.")
					
					# Notification packets from the preload override - mirror these back, don't pass them on
					elif(len(packet.chat) >= 7 and packet.chat[0:7] == "[!CHAT]"):
						self.chatback(packet.chat[7:])
						send = False

#				elif((packet.packettype == pkt.Packet.PACKETTYPE_POSITION) and self.whereami):
#					log.add(self.name + ": Informing client of whereamthem. [whereami]")
#					pos = "[PROXY] Your position is " + packet.position.toString()
#					self.chatback(pos)
#					self.whereami = False
				
				elif(packet.packettype == pkt.Packet.PACKETTYPE_POSITION):
					if((packet.packettype == pkt.Packet.PACKETTYPE_POSITION) and (self.serverteleportpos != None)):
						packet = self.serverteleport(packet)
				
					if((packet.packettype == pkt.Packet.PACKETTYPE_POSITION) and (self.rserverteleportpos != None)):
						packet = self.relativeserverteleport(packet)
						
					if((packet.packettype == pkt.Packet.PACKETTYPE_POSITION) and self.whereami):
						log.add(self.name + ": Informing client of whereamthem. [whereami]")
						pos = "[PROXY] Your position is " + packet.position.toString()
						self.chatback(pos)
						self.whereami = False

					if(self.csvUsLog != None):
						#print(packet.position.toCSVable())
						self.csvUsLog.update("Player", packet.position.toCSVable())
						#plogf = open("player.csv", "w")
						#plogf("Player" + "," + packet.position.toCSVable() + "\n")
						#plogf.close()
					
					self.mostRecentPosition = packet
				
				# For monsters, check Map CSV update and nearby notify
				# if a monster is nearby...
				elif(packet.packettype == pkt.Packet.PACKETTYPE_SERVER_MONSTERUPDATE):
					self.csvLog.update(str(packet.id), packet.position.toCSVable())
					if(self.nearbynotify):
						self.nearby()

				# For players, check Map CSV update and nearby notify
				# if a player is nearby...
				elif(packet.packettype == pkt.Packet.PACKETTYPE_SERVER_OTHERPLAYERSUPDATE):
					self.csvPlayerLog.update(str(packet.id), packet.position.toCSVable())
					if(self.nearbynotify):
						self.nearby()


				# convert the packet back into a bytestream and throw it back
				if(send):
					self.completedPackets.put(packet.raw)




			except queue.Empty:						# Nothing to process
				pass
				#time.sleep(0.1) 		# this sleep is probably too long

			
		# at this point, we've been told to die	
		log.add(self.name + ": analyser thread dying.")
		
	###########################################################################################################################################################################
	## Constructor. Takes a name (for logging purposes) and a log to write to. May optionally (= non-zero) take a port to log parse data to.
	###########################################################################################################################################################################	
	def __init__(self, name, log, useClientPacketList, parent, doCSV):
		
		self.dataStreamQueue = queue.Queue()  # Our FIFO queue for raw data. We can split this into discrete packets.
														  # We can't guarantee each chunk of data will be one packet - some assembly may be requried.
		self.packetQueue = queue.Queue()      # Our FIFO queue for packets. Once we've split our data into packets, they go here, and we can extract them as we go.
		self.completedPackets = queue.Queue() # Our FIFO queue for outgoing packets. These have been reassembled by the parser into strings that we can spit out of a socket.

		#####################
		# Variables for haxxx
		#
		self.nearbycheckertime = time.time()
		#
		# mapping CSV logger; this will write out position information we add to it every second.
		if(doCSV):
			self.csvLog = logger.CSVMaker("monsters.csv", True)
			self.csvPlayerLog = logger.CSVMaker("players.csv", True)
			self.csvUsLog = None
		else:
			self.csvLog = None 
			self.csvPlayerLog = None
			self.csvUsLog = logger.CSVMaker("player.csv", False)
		
		# a pkt.PosPacket from our most recent position update
		self.mostRecentPosition = None
		#
		####################		

		# logging stuff
		self.log = log
		self.name = name

		# Our parent object - useful if we want to inject packets to the opposite stream to us.
		self.parent = parent
	
		# client>>Server and server>>client connections use different packet lists.	
		self.isClient = useClientPacketList

		if(useClientPacketList):
			self.packetlist = pkt.Packet.client_packet_types
		else:
			self.packetlist = pkt.Packet.server_packet_types

		# set to True when this thread needs to end (i.e. at program exit)
		self.die = False

		# start the thread that will read from the dataStreamQueue FIFO queue and break it up into packets.
		self.packetise_thread = threading.Thread(target=self.packetise, args=(self.log,))
		self.packetise_thread.start()

		# start the thread that will read from the packetQueue FIFO queue and look at each of the packets. This is where the good stuff will happen.
		self.analyse_thread = threading.Thread(target=self.analysePackets, args=(self.log,))
		self.analyse_thread.start()

	def addRawData(self, data):
		self.dataStreamQueue.put(data)

	def kill(self):
		self.die = True
		if(self.csvLog != None):
			self.csvLog.kill()
			self.csvPlayerLog.kill()

	## Non-blocking; may return None if there are no packets, or a single packet.
	def getPacket(self):
		try:
			packet = self.completedPackets.get(False)
		except queue.Empty:
			return None
		else:
			return packet

####################################################################################################################################################################################
## Any functions for specific hacks can go down here
####################################################################################################################################################################################
	
	## Send a message to yourself
	def chatback(self, message):
		length = len(message).to_bytes(2, byteorder='little', signed=False)
		chatback_packet = pkt.Packet(pkt.Packet.PACKETTYPE_SERVER_CHAT + Parser.PLAYERID + length + message.encode('ascii'))
		self.parent.serverParser.addRawData(chatback_packet.raw)

	## Send a weapon fire packet for the ZeroCool weapon
	## Note that this will not work if you don't have the weapon - a good test case.
	def pew(self, message):
		
		print(str(len(message)) + " " + message[8:9])
		if(len(message) >= 9 and message[8:9] == "f"):
			pewpacket = pkt.PewPacket(pkt.Packet.PACKETTYPE_FIREWEAPON + b'\x10\x00' + "GreatBallsOfFire".encode('ascii') + self.mostRecentPosition.position.pack())
		else:	
			pewpacket = pkt.PewPacket(pkt.Packet.PACKETTYPE_FIREWEAPON + b'\x08\x00' + "ZeroCool".encode('ascii') + self.mostRecentPosition.position.pack())
			
		self.parent.clientParser.addRawData(pewpacket.raw + self.mostRecentPosition.raw)
		self.log.addAndPrint("Weapon pew injected to server: [" + pewpacket.raw.hex() + self.mostRecentPosition.raw.hex() + "]")

	# Periodically update number of mobs nearby
	def nearby(self):
		if((time.time() - self.nearbycheckertime >= 5) and (self.csvLog.timeSinceLastPurge >= 1)):
			mobsnearby = "[PROXY] " + str(len(self.csvLog.csv)) + " monsters, " + str(len(self.csvPlayerLog.csv)) + " players."
			self.chatback(mobsnearby)
			self.nearbycheckertime = time.time()

	# interact with an object
	def poke(self, ident):
		try:
			ident=int(ident.encode('ascii'))
		except ValueError as e:
			self.chatback("[PROXY] Invalid ID (Not an integer?)")
			return
		try:
			ident = struct.pack('<I', ident)
		except struct.error as e:
			self.chatback("[PROXY] Invalid ID.")
			return
		poke_packet = pkt.Packet(pkt.Packet.PACKETTYPE_ACTORINTERACT + ident)
		self.parent.clientParser.addRawData(poke_packet.raw)

	# relative teleport serverside
	def relativeserverteleport(self, packet):
		oldposition = packet.position
		
		try:
			# These will be RELATIVE coordinates
			coordinates = self.rserverteleportpos.split(' ', 2)			# for some reason splits into n+1 parts
			packet.position.x = packet.position.x + float(coordinates[0])
			packet.position.y = packet.position.y + float(coordinates[1])
			packet.position.z = packet.position.z + float(coordinates[2])
		except ValueError as e:
			self.chatback("[PROXY] Invalid coordinates (too few?):" + str(e))
			self.rserverteleportpos = None
			return
		
		packet.reconstruct()
		self.log.addAndPrint(self.name + ": RelativeServerTeleport: " + oldposition.toString() + " to " + packet.position.toString())
		return packet

	# teleport serverside
	def serverteleport(self, packet):
		oldposition = packet.position
	
		try:
			coordinates = self.serverteleportpos.split(' ', 2)			# for some reason splits into n+1 parts
			packet.position.x = float(coordinates[0])
			packet.position.y = float(coordinates[1])
			packet.position.z = float(coordinates[2])
		except ValueError as e:
			self.chatback("[PROXY] Invalid coordinates (too few?)")
			self.serverteleportpos = None
			return

		packet.reconstruct()
		self.log.addAndPrint(self.name + ": ServerTeleport: " + oldposition.toString() + " to " + packet.position.toString())
		return packet	