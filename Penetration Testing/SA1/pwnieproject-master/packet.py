#!/usr/bin/env python

from abc import ABC, abstractmethod
import struct

###########################################################################################################################################################################
## Thrown if a variable length packet is incomplete.
## The packetiser can catch these errors and know that it needs to read more before trying to packetise us again.
## Unless something goes very wrong, our fixed length packets should always be complete as we can check their fixed length is present within the datastream
###########################################################################################################################################################################
class IncompletePacketException(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

###########################################################################################################################################################################
## Use this to unpack and pack all those pesky XYZs
###########################################################################################################################################################################
class Vector:
	def __init__(self, raw):

		x = raw[:4]
		y = raw[4:8]
		z = raw[8:12]
		self.x = float(struct.unpack('f', x)[0])
		self.y = float(struct.unpack('f', y)[0])
		self.z = float(struct.unpack('f', z)[0])

	def pack(self):
		return struct.pack('f', self.x) + struct.pack('f', self.y) + struct.pack('f', self.z)

	def toString(self):
		return "X: {:.2f} Y: {:.2f} Z: {:.2f}".format(self.x, self.y, self.z)

	def toCSVable(self):
		return "{:.2f},{:.2f},{:.2f}".format(self.x, self.y, self.z)

###########################################################################################################################################################################
## Stores a single packet.
## This is an abstract class - extend it for each packet type.
###########################################################################################################################################################################
class Packet:

	PACKETTYPE_POSITION = b'\x6d\x76'				# mv
	PACKETTYPE_FIREWEAPON = b'\x2a\x69'	 			# *i
	PACKETTYPE_WEAPONSWITCH = b'\x73\x3d'	 		# s=		
	PACKETTYPE_INITHASH = b'\x50\x58'				# We shouldn't ever be in a situation where these are packetised - we catch the special cases, and they're not in are dictionaries below.	
	PACKETTYPE_CHAT = b'\x23\x2a'						# #*
	PACKETTYPE_JUMP = b'\x6a\x70'						# jp
	PACKETTYPE_EMPTY = b'\x00\x00'					#
	PACKETTYPE_ACTORINTERACT = b'\x65\x65'			# ee 
	PACKETTYPE_KEY = b'\x6b\x79'						# ky
	PACKETTYPE_TEST = b'tt'								# tt
	
	PACKETTYPE_UNKNOWN = b'??'		

	client_packet_types = {
		# this dictionary is "static-ish"; we don't change fields 0 and 1, but can change field 2 to toggle display/logging
		# initial bytes as key, tuple containing packet's human-readable name, the packet's length as data (including the header), and default for whether to log to screen or not. 
		# a length of zero denotes a packet that can have a variable length; that length will be encoded in the packet, and will be extracted.
		PACKETTYPE_POSITION: ("Position Update", 22, False),
		PACKETTYPE_FIREWEAPON: ("Fire Weapon", 0, True),	
		PACKETTYPE_WEAPONSWITCH: ("Weapon Switch", 3, True),
		PACKETTYPE_CHAT: ("Chat packet", 0, True),
		PACKETTYPE_JUMP: ("Jump packet", 3, True),
		PACKETTYPE_EMPTY: ("Empty client packet", 0, False),
		PACKETTYPE_ACTORINTERACT: ("Actor interact", 6, True),
		PACKETTYPE_KEY: ("Submit Key", 0, True),
		PACKETTYPE_TEST: ("STUB: Test Packet", 0, True),
		PACKETTYPE_UNKNOWN: ("Unknown Packet", 1024, True)
	}

	PACKETTYPE_SERVER_MANIFEST = b'\x6d\x6b' 					# mk
	PACKETTYPE_SERVER_EMPTY = b'\x00\x00'						#
	PACKETTYPE_SERVER_MONSTERUPDATE = b'\x70\x73' 			# ps
	PACKETTYPE_SERVER_OTHERPLAYERSUPDATE = b'\x70\x70'    # pp
	PACKETTYPE_SERVER_OTHERPLAYERSGONE = b'\x5e\x63'      # ^c
	PACKETTYPE_SERVER_POSITION = b'\x6d\x76'					# mv
	PACKETTYPE_SERVER_CHAT = b'\x23\x2a'						# #*
	PACKETTYPE_SERVER_DESPAWN = b'\x78\x78'		 			# xx
	PACKETTYPE_SERVER_MOBILESTATUS = b'\x73\x74'				# st
	PACKETTYPE_SERVER_MANAUPDATE = b'\x6d\x61'				# ma
	PACKETTYPE_SERVER_MOBILEHITPOINTSUPDATE = b'\x2b\x2b' # ++
	PACKETTYPE_SERVER_MOBILETRANSFORMSTATE = b'\x74\x72'  # tr
	PACKETTYPE_SERVER_RECEIVEITEM = b'\x63\x70'				# cp
	PACKETTYPE_SERVER_AREATRANSITION = b'\x63\x68'			# rt
	PACKETTYPE_SERVER_PLAYERMANIFEST = b'\x6e\x63'			# nc

	server_packet_types = {
		PACKETTYPE_SERVER_MANIFEST: ("Manifest mobiles", 0, True),
		PACKETTYPE_SERVER_EMPTY: ("Empty server packet", 0, False),
		PACKETTYPE_SERVER_MONSTERUPDATE: ("Monster update", 30, False),
		PACKETTYPE_SERVER_OTHERPLAYERSUPDATE: ("Other Players Update", 32, False), 
		PACKETTYPE_SERVER_OTHERPLAYERSGONE: ("Other player gone", 6, True),
		PACKETTYPE_SERVER_POSITION: ("Position update", 24, False),
		PACKETTYPE_SERVER_CHAT: ("Chat Packet", 0, True),
		PACKETTYPE_SERVER_DESPAWN: ("Object Despawn", 6, True),
		PACKETTYPE_SERVER_MOBILESTATUS: ("Mobile object status", 0, True),
		PACKETTYPE_SERVER_MANAUPDATE: ("Mana Update", 6, False),
		PACKETTYPE_SERVER_MOBILEHITPOINTSUPDATE: ("Mobile object hitpoints change", 10, True),
		PACKETTYPE_SERVER_MOBILETRANSFORMSTATE: ("Mobile object changed state", 0, True),
		PACKETTYPE_SERVER_RECEIVEITEM: ("Received item", 0, True),
		PACKETTYPE_SERVER_AREATRANSITION: ("Area transition", 0, True),
		PACKETTYPE_SERVER_PLAYERMANIFEST: ("Player manifest", 0, True),
		PACKETTYPE_UNKNOWN: ("Unknown Packet", 1024, True)
	}
	###########################################################################################################################################################################
	## raw is the binary data of the packet.
	###########################################################################################################################################################################
	def __init__(self, raw):

		self.packettype = raw[:2] # first two bytes are the header
		
		# Implmentations of this abstract class can do fancy things with the raw data - we shouldn't.
		self.raw = raw

		## Let's find out what our type is
		try:
			self.packetinfo = Packet.client_packet_types[self.packettype]
		except KeyError as e:
			try:
				self.packetinfo = Packet.server_packet_types[self.packettype]
			except KeyError as e:
				# This packet doesn't have a header we know about
				self.packetinfo = Packet.client_packet_types[Packet.PACKETTYPE_UNKNOWN]

	# Call this to reassemble the packet's fields back into a new self.raw binary stream
	@abstractmethod
	def reconstruct(self):
		pass

	# for ease of logging, we can make a packet identify itself
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + self.raw.hex() + "]" )

	# raw hex representation of the packet for analysis/logging
	def toHex(self):
		return self.raw.hex()

###########################################################################################################################################################################
## Stores a single packet and parses the header to determine type. ALMOST ALL PACKETS ARE THIS except UnknownPacket and VariableLengthPacket (and its children)
## There is a niche case where a server packet and client packet can have the same header, but one is implemented and the other not, and they are structured differently.
## An example is the mv packet, which is different depending on origin.
## Extracting a header will use the implemented definition, which may not be the correct one - which means we end up passing broken/truncated packets etc.
## This is an abstract class - extend it for each packet type.
###########################################################################################################################################################################
class HeaderPacket(Packet):
	
	def __init__(self, raw, packettypes):

		super().__init__(raw)

		## note that raw contains possibly more than one packet.
		## The packetiser can find out how much we've used, and how much is left, by checking the static packet_types[packettype][1] and doing some string magic with that value
		## we'll do the same to ensure that our raw data is only the data for this packet.
		try:
			length = packettypes[self.packettype][1]
		except KeyError as e:
			length = len(raw)
			 
		self.raw = raw[:length]		 # first length bytes of the raw is all we need.

class ServerHeaderPacket(HeaderPacket):
	def __init__(self, raw):

		super().__init__(raw, Packet.server_packet_types)

class ClientHeaderPacket(HeaderPacket):
	def __init__(self, raw):

		super().__init__(raw, Packet.client_packet_types)

###########################################################################################################################################################################
## Simple variable length packets are treated a little differently and should extend this abstract class. 
## Note that we don't implement reconstruct(), so we can't be constructed.
###########################################################################################################################################################################
class VariableLengthPacket(Packet):

	def __init__(self, raw):
		self.variablefield = ''
		self.remainder = ''
		super().__init__(raw)

	def getRemainder(self):
		return self.remainder

###########################################################################################################################################################################
## Simple variable length packets are treated a little differently and should extend this abstract class. 
## Note that we don't implement reconstruct(), so we can't be constructed.
###########################################################################################################################################################################
class SimpleVariableLengthPacket(VariableLengthPacket):

	def __init__(self, raw, offset):
		
		super().__init__(raw)

		if(len(self.raw) < 5):				# these packets must have ID (2 bytes) size (2 bytes) and at least 1 byte of stuff
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex())		

		try:
			self.__parse_vlength(offset)
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))
	
	def getRemainder(self):
		return self.remainder

	def __parse_vlength(self, offset):

		# the two bytes after the header are the length of the variable portion. They are in little endian?
		length = (ord(self.raw[3+offset:4+offset])*256) + ord(self.raw[2+offset:3+offset])

		# next comes the variable portion, for -length- characters
		if(len(self.raw) < length+4+offset):
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + "Length was " + str(len(self.raw)) + ", expected " +str(length+4+offset) + "; offset is " + str(offset))	
		self.variablefield = self.raw[4+offset:length+4+offset]

		# so the actual raw data belonging to this packet are the two header bytes + two field size bytes (4) plus the length of the name -length-
		# set self.raw to this, and self.remainder to everything else.
		tmp = self.raw[:length+4+offset] 
		self.remainder = self.raw[length+4+offset:]
		self.raw = tmp	
	
###########################################################################################################################################################################
## Mobile actor status effect update
## This can't be a SimpleVariableLengthPacket sadly because the status byte comes after the name
###########################################################################################################################################################################
class ServerMobileStatusPacket(VariableLengthPacket):

	def __init__(self, raw):

		self.status = ""
		self.statustoggle = 0
		self.id = 0

		super().__init__(raw)
		
		try:
			self.__parseid()
			self.__parsestatus()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))

	def __parseid(self):
		# the (four?) bytes after the header are the ID(?). Little endian(?)
		self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 32-bit integer

	def __parsestatus(self):
		# The name of the status is variable length
		length = (ord(self.raw[7:8])*256) + ord(self.raw[6:7])

		# cut it out
		if(len(self.raw) < length+9):    # 9 not 8 as we expect a byte after the name of the status
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + "Length was " + str(len(self.raw)) + ", expected " +str(length+9))	
		self.variablefield = (self.raw[8:length+8])
		self.status = self.variablefield.decode('ascii')

		# the final byte after the name
		self.statustoggle = ord(self.raw[length+8:length+9])

		# so the actual raw data belonging to this packet are the two header bytes + two field size bytes (4) plus the length of the name -length-
		# set self.raw to this, and self.remainder to everything else.
		tmp = self.raw[:length+9] 
		self.remainder = self.raw[length+9:]
		self.raw = tmp	

	# Override
	def toLoggable(self):
		if(self.statustoggle == 1):
			return ( str(self.packetinfo[0]) + " [" + str(self.id) + "] gains status [" + self.status + "]" )
		else:
			return ( str(self.packetinfo[0]) + " [" + str(self.id) + "] loses status [" + self.status + "]" )

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + struct.pack('<H', len(self.status)) + self.status.encode('ascii') + self.statustoggle.to_bytes(1, byteorder='big', signed=False)

###########################################################################################################################################################################
## Mobile actor transform state (DEAD!)
###########################################################################################################################################################################
class ServerMobileTransformStatePacket(VariableLengthPacket):

	def __init__(self, raw):

		self.state = ""
		self.id = 0

		self.target = 0

		super().__init__(raw)

		try:
			self.__parseid()
			self.__parsenewstate()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))

	def __parseid(self):
		# the (four?) bytes after the header are the ID(?). Little endian(?)
		self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 32-bit integer

	def __parsenewstate(self):
		# The name of the status is variable length
		length = (ord(self.raw[7:8])*256) + ord(self.raw[6:7])

		# cut it out
		if(len(self.raw) < length+12):    # 12 not 8 as we expect 4 bytes after the name of the transformed state
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + "Length was " + str(len(self.raw)) + ", expected " +str(length+12))	
		self.variablefield = (self.raw[8:length+8])
		self.state = self.variablefield.decode('ascii')

		# there should be four bytes left
		self.target = self.raw[length+8:length+12]

		# so the actual raw data belonging to this packet are the two header bytes + two field size bytes (4) plus the length of the name -length-
		# set self.raw to this, and self.remainder to everything else.
		tmp = self.raw[:length+12] 
		self.remainder = self.raw[length+12:]
		self.raw = tmp	

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + str(self.id) + "] transformed to new state [" + self.state + "] relating to object = [" + self.target.hex() + "]" )

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + struct.pack('<H', len(self.state)) + self.state.encode('ascii') + self.target

###########################################################################################################################################################################
## Receive Item
###########################################################################################################################################################################
class ServerReceiveItemPacket(VariableLengthPacket):

	def __init__(self, raw):

		self.itemname = ""
		self.quantity = 0

		super().__init__(raw)

		try:
			self.__parse()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))

	def __parse(self):
		# The name of the status is variable length
		length = (ord(self.raw[3:4])*256) + ord(self.raw[2:3])

		# cut it out
		if(len(self.raw) < length+8):    # 8 not 4 as we expect 4 bytes after the name
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + "Length was " + str(len(self.raw)) + ", expected " +str(length+8))	
		self.variablefield = (self.raw[4:length+4])
		self.itemname = self.variablefield.decode('ascii')

		# there should be four bytes left
		self.quantity = struct.unpack('<I', self.raw[length+4:length+8])[0]

		tmp = self.raw[:length+8] 
		self.remainder = self.raw[length+8:]
		self.raw = tmp	

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + self.itemname + "] (Qty: " + str(self.quantity) + ")")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<H', len(self.itemname)) + self.itemname.encode('ascii') + struct.pack('<I', self.quantity)

###########################################################################################################################################################################
## Shiny items announced to us at the start of the game connection
###########################################################################################################################################################################
class ServerManifestPacket(VariableLengthPacket):

	def __init__(self, raw):
		self.remainder = ''
		
		self.name= ''
		self.namelength = 0;
		self.id = ''
		
		# not sure what's in this bit yet
		self.otherstuff = ''

		self.position = ''

		super().__init__(raw)
	
		## These packets must be at LEAST 36 bytes in size (for a 1-byte name field)
		if(len(self.raw) < 36):
			raise IncompletePacketException(str(self.packettype) + " " + str(self.raw))	

		try:
			self.__parseid()
			self.__parsename()
			self.__parseposition()
			self.__parseotherstuff()
			self.__parseremainder()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))

	def __parseid(self):
		# the 4 (nine?) bytes after the header are the ID(?). Little endian(?)
		self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 64-bit integer
		
	def __parsename(self):	
		# bytes 12:14 are the length of the field
		self.namelength = (ord(self.raw[12:13])*256) + ord(self.raw[11:12])

		# now that we know the length of the name, we can confirm that this packet is complete.
		if(len(self.raw) < self.namelength + 35):
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex())	

		# next comes the variable portion, for -length- characters
		self.name = self.raw[13:self.namelength+13]
	
	def __parseposition(self):
		self.position = Vector(self.raw[self.namelength + 13:self.namelength + 25])
		pass
	
	def __parseotherstuff(self):
		self.otherstuff = self.raw[self.namelength + 25:self.namelength + 35]

	def __parseremainder(self):
		tmp = self.raw[:self.namelength + 35]
		self.remainder = self.raw[self.namelength + 35:]
		self.raw = tmp

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": " + self.name.decode('ascii') + "[" + str(self.id) + "] at " + self.position.toString() + "; stuff is [" + self.otherstuff.hex() + "]") # ; raw = [" + self.raw.hex() + "]")

	def getRemainder(self):
		return self.remainder

	def reconstruct(self):
		length = hex(self.namelength)
		self.raw = self.packettype + struct.pack('<Q', self.id) + b'\x00' + struct.pack('<H', len(self.name)) + self.name + self.position.pack() + self.otherstuff

###########################################################################################################################################################################
## Monster updates
###########################################################################################################################################################################
class ServerMonsterUpdatePacket(ServerHeaderPacket):

	def __init__(self, raw):
		
		self.id = ''
		
		# not sure what's in this bit yet
		self.otherstuff = ''

		self.position = ''

		super().__init__(raw)
	
		self.__parseid()
		self.__parseposition()
		self.__parseotherstuff()

	def __parseid(self):
		# the (four?) bytes after the header are the ID(?). Little endian(?)
		self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 32-bit integer
	
	def __parseposition(self):
		self.position = Vector(self.raw[6:18])
		pass
	
	def __parseotherstuff(self):
		self.otherstuff = self.raw[18:30]

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": [" + str(self.id) + "] at " + self.position.toString() + "; stuff is [" + self.otherstuff.hex() + "]")

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + self.position.pack() + self.otherstuff

###########################################################################################################################################################################
## TEST PACKET
###########################################################################################################################################################################
class ServerTestPacket(SimpleVariableLengthPacket):

	def __init__(self, raw):
		
		#self.id = ''
		self.locationname = ""
		#self.position = ''

		super().__init__(raw, 0)
	
		#self.__parseid()
		#self.__parseposition()
		self.locationname = self.variablefield.decode('ascii')
		#self.__parsename()

	#def __parseid(self):
		# the (four?) bytes after the header are the ID(?). Little endian(?)
		#self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 32-bit integer
	
#	def __parseposition(self):
		#self.position = Vector(self.raw[6:18])
		#pass

	def toLoggable(self):
		#return ( str(self.packetinfo[0]) + ": [" + str(self.id) + "] at " + self.position.toString() + "]")
		return ( str(self.packetinfo[0]) + ": location name is [" + self.locationname + "]")

	def reconstruct(self):
		#self.raw = self.packettype + struct.pack('<I', self.id) + self.position.pack()
		self.raw = self.packettype + struct.pack('<H', len(self.locationname)) + self.variablelengthfield

###########################################################################################################################################################################
## Area Transition Packet
## This is handled very carefully in the parser - it indicates that the server connection is about to be closed, and that we should close the client connection in return.
## The timing has to be right - this needs to be received by the client before we sever the link.
###########################################################################################################################################################################

class ServerAreaTransitionPacket(SimpleVariableLengthPacket):

	def __init__(self, raw):
		
		self.locationname = ""
		super().__init__(raw, 0)

		self.locationname = self.variablefield.decode('ascii')

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": location name is [" + self.locationname + "]")

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<H', len(self.locationname)) + self.variablelengthfield

###########################################################################################################################################################################
## Player Object updates
###########################################################################################################################################################################
class ServerOtherPlayersUpdatePacket(ServerHeaderPacket):

	def __init__(self, raw):
			
		# [pp] [id    ] [pos?                  ] vert rota      spdx spdy spdz fb
		# 7070 950a0000 3aa552c7b72f5fc7f8aa9544 0000 0000 0000 0000 0000 beff 0000

		self.id = ''
		self.position = ''

		# not that worried about this stuff
		self.otherstuff = ''

		super().__init__(raw)
	
		self.__parseid()
		self.__parseposition()
		self.__parseotherstuff()

	def __parseid(self):
		# the (four?) bytes after the header are the ID(?). Little endian(?)
		self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 32-bit integer
	
	def __parseposition(self):
		self.position = Vector(self.raw[6:18])
		pass
	
	def __parseotherstuff(self):
		self.otherstuff = self.raw[18:32]

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": [" + str(self.id) + "] at " + self.position.toString() + "; stuff is [" + self.otherstuff.hex() + "]; RAW: [" + self.raw.hex() + "]")

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + self.position.pack() + self.otherstuff

###########################################################################################################################################################################
## Mobile HP update - including us!
###########################################################################################################################################################################
class ServerMobileHitpointsUpdatePacket(ServerHeaderPacket):

	def __init__(self, raw):
		
		self.id = ''
		self.hp = 0

		super().__init__(raw)
	
		self.__parseid()
		self.__parsehp()

	def __parseid(self):
		# the (four?) bytes after the header are the ID(?). Little endian(?)
		self.id = struct.unpack('<I', self.raw[2:6])[0] 		  # Unsigned 32-bit integer
	
	def __parsehp(self):
		self.hp = struct.unpack('<i', self.raw[6:10])[0]

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": [" + str(self.id) + "] HP is now [" + str(self.hp) + "]" )#{:.0f}]".format(self.hp) )

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + struct.pack('<i', self.hp)

###########################################################################################################################################################################
## Empty server packet
## Often just 0000, but sometimes the server just hurls 00s at us. Let's clean them all up in one go.
###########################################################################################################################################################################
class ServerEmptyPacket(VariableLengthPacket):
	
	def __init__(self, raw):

		super().__init__(raw)
		self.packetinfo = Packet.server_packet_types[self.packettype]
		self.__parsebytes()

	def __parsebytes(self):	
		
		count = 2
		while True:
			if(self.raw[count:count+1] != b'\x00'):
				break
			count +=1

		tmp = self.raw[:count]
		self.remainder = self.raw[count:]
		self.raw = tmp
	
	# Overrides
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": Empty (length: " + str(len(self.raw)) + ") [" + self.raw.hex() + "]" )

	# Implements
	def reconstruct(self):
		print("Did you just try to reconstruct an EmptyPacket?")
		pass

###########################################################################################################################################################################
## Empty client packet
## Often just 0000, but sometimes more
## this is literally identical to the server's one
###########################################################################################################################################################################
class EmptyPacket(ServerEmptyPacket):
	
	def __init__(self, raw):

		super().__init__(raw)

###########################################################################################################################################################################
## Something despawned?
###########################################################################################################################################################################
class ServerDespawnPacket(ServerHeaderPacket):
	
	def __init__(self, raw):

		self.id = 0

		super().__init__(raw)
		self.__parseid()
	
	def __parseid(self):
		self.id = struct.unpack('<I', self.raw[2:6])[0] 

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id)

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": [" + str(self.id) + "]")

###########################################################################################################################################################################
## Player moves out of range (or logs out?)
###########################################################################################################################################################################
class ServerOtherPlayersGonePacket(ServerHeaderPacket):
	
	def __init__(self, raw):

		self.id = 0

		super().__init__(raw)
		self.__parseid()
	
	def __parseid(self):
		self.id = struct.unpack('<I', self.raw[2:6])[0] 

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id)

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": [" + str(self.id) + "]")

###########################################################################################################################################################################
## Mana update - our new mana value stored directly in the packet.
###########################################################################################################################################################################
class ServerManaUpdatePacket(ServerHeaderPacket):
	
	def __init__(self, raw):

		self.mana = 0

		super().__init__(raw)
		self.__parsemana()
	
	def __parsemana(self):
		self.mana = struct.unpack('<I', self.raw[2:6])[0]  #struct.unpack('<H', self.raw[2:4])[0] # ord(self.raw[2:3]) # struct.unpack('<I', self.raw[2:6])[0] 

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.mana) #self.packettype + struct.pack('<H', self.mana) #self.mana.to_bytes(1, byteorder='big', signed=False)  #struct.pack('<I', self.mana)

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + ": [" + str(self.mana) + "]")

###########################################################################################################################################################################
## Position update packet
###########################################################################################################################################################################
class PosPacket(ClientHeaderPacket):
	
	def __init__(self, raw):

		self.position = 0

		self.face_a = 0
		self.face_b = 0

		self.otherstuff = ''

		super().__init__(raw)
		self.__parseposition()
		self.__parsefacing()
		self.__parseotherstuff()

	def __parseposition(self):
		self.position = Vector(self.raw[2:14])

	def __parsefacing(self):
		self.face_a = struct.unpack('H', self.raw[14:16])[0]
		self.face_b = struct.unpack('H', self.raw[16:18])[0]
		pass

	def __parseotherstuff(self):
		self.otherstuff = self.raw[18:]

	# for ease of logging, we can make a packet identify itself
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " " + self.position.toString() + " facing [" + str(self.face_a) + " " + str(self.face_b) + "]; otherstuff is [" + self.otherstuff.hex() + "]")

	def reconstruct(self):
		self.raw = self.packettype + self.position.pack() + struct.pack('H', self.face_a) + struct.pack('H', self.face_b) + self.otherstuff

###########################################################################################################################################################################
## Server Position update packet
###########################################################################################################################################################################
class ServerPosPacket(ServerHeaderPacket):
	
	def __init__(self, raw):

		self.position = 0

		self.id = 0

		# vertical
		self.face_a = 0

		# rotation
		self.face_b = 0

		self.otherstuff = ''

		super().__init__(raw)
		self.__parseid()
		self.__parseposition()
		self.__parsefacing()
		self.__parseotherstuff()

	def __parseid(self):
		self.id = struct.unpack('<I', self.raw[2:6])[0] 

	def __parseposition(self):
		self.position = Vector(self.raw[6:18])

	def __parsefacing(self):
		self.face_a = struct.unpack('H', self.raw[18:20])[0]
		self.face_b = struct.unpack('H', self.raw[20:22])[0]

	def __parseotherstuff(self):
		self.otherstuff = self.raw[22:]

	# for ease of logging, we can make a packet identify itself
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + str(self.id) + "] " + self.position.toString() + " facing [" + str(self.face_a) + " " + str(self.face_b) + "]; otherstuff is [" + self.otherstuff.hex() + "]")

	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + self.position.pack() + struct.pack('H', self.face_a) + struct.pack('H', self.face_b) + self.otherstuff

###########################################################################################################################################################################
## Jump packet
###########################################################################################################################################################################
class JumpPacket(ClientHeaderPacket):
	
	def __init__(self, raw):

		self.state = 0 			# 0 or 1; 1 seems to be the start of a jump, 0 ends

		super().__init__(raw)
		self.__parsejump()

	def __parsejump(self):
		self.state = ord(self.raw[2:3])
	
	# Overrides
	def toLoggable(self):
		if(self.state == 1):
			return ( str(self.packetinfo[0]) + ": Jump starts")
		return ( str(self.packetinfo[0]) + ": Jump ends")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + self.state.to_bytes(1, byteorder='big', signed=False) 

###########################################################################################################################################################################
## When we walk over those treasure blobs
###########################################################################################################################################################################
class ActorInteractPacket(ClientHeaderPacket):
	
	def __init__(self, raw):

		self.id = 0 			# ID of the blob we walk over

		super().__init__(raw)
		self.__parseid()

	def __parseid(self):
		self.id = struct.unpack('<I', self.raw[2:6])[0] 
	
	# Overrides
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " with object [" + str(self.id) + "]")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id)

###########################################################################################################################################################################
## Game connection initialisation packet - contains some strange single-byte variable value as well as our hash
## We should never receive these - merely pass them on as a special case before the parser starts processing "real" packets.
## Don't do anything with them - just pass them on.
###########################################################################################################################################################################
class InitPacket(Packet):
	
	def __init__(self, raw):

		super().__init__(raw)
	
	# Overrides
	def toLoggable(self):
		return ( "InitPacket; raw = [" + self.raw.hex() + "]")

	# Implements
	def reconstruct(self):
		print("Why are you building an InitPacket?")	 

###########################################################################################################################################################################
## Game connection initialisation packet sent by a client that's been appropriately LD_PRELOADed
## This contains the port we're to connect to and the idk
###########################################################################################################################################################################
class DoctoredInitPacket(ClientHeaderPacket):
	
	# header PX     idk port   middle                                 
	# 0x50 0x58,   0xXX 0xXX 0x20 0x00 (ish), 32-byte hash? string
	
	def __init__(self, raw):

		self.hash = ''
		self.port = 0
		self.idk = ''
		self.middle = ''


		super().__init__(raw)

		#print(self.raw.hex())

		self.__parsedoctoredinfo()
		self.__parsemiddle()
		self.__parsehash()		

		#print(self.toLoggable())

	def __parsemiddle(self):
		self.middle=self.raw[4:6]

	def __parsedoctoredinfo(self):
		self.idk = self.raw[2:3]
		self.port = ord(self.raw[3:4]) + 3000
		

	def __parsehash(self):
		self.hash = self.raw[-32:]
	
	# Overrides
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " is doctored; port [" + str(self.port) + "], idk [" + self.idk.hex() + "], middle [" + self.middle.hex() + "], hash [" + self.hash.hex() + "]" )

	# Implements
	def reconstruct(self):
		print("Did you just try to reconstruct an DoctoredInitPacket?")

###########################################################################################################################################################################
## Weapon switch packet
###########################################################################################################################################################################
class WpnSwitchPacket(ClientHeaderPacket):

	def __init__(self, raw):

		self.index = 0 

		super().__init__(raw)
		self.__parseweaponindex()

	# Implements
	def reconstruct(self):
		pass

	def __parseweaponindex(self):	
		self.index = ord(self.raw[2:3])

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " Swapped to position " + str(self.index) )

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + self.index.to_bytes(1, byteorder='big', signed=False) 

###########################################################################################################################################################################
## Weapon fire packet
## Note that the packets for this are variable length because they contain the name of the weapon
###########################################################################################################################################################################
class PewPacket(VariableLengthPacket):

	def __init__(self, raw):

		self.weapon_name = ""
		self.weapon_name_length = 0
		self.remainder = ''

		self.position = 0

		super().__init__(raw)

		try:
			self.__parseweaponname()
			self.__parseposition()
			self.__parseremainder()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))	

		if(len(self.raw) < self.weapon_name_length+16):
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex())	

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + self.weapon_name + "]")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<H', len(self.weapon_name)) + self.weapon_name.encode('ascii') + self.position.pack()

	def __parseweaponname(self):
		# the two bytes after the header are the length of the name. They are in little endian?
		self.weapon_name_length = (ord(self.raw[3:4])*256) + ord(self.raw[2:3])

		# next comes the variable portion, for -length- characters
		# check length +16; header (2) + length bytes (2) + the position floats at the end (12) +(?) the associate position packet (?)

		self.weapon_name = self.raw[4:self.weapon_name_length+4].decode('ascii')

	def __parseposition(self):
		self.position = Vector(self.raw[self.weapon_name_length + 4:self.weapon_name_length + 16])

	def __parseremainder(self):
		# two header bytes + two field size bytes (4) plus the length of the name plus a position (12) = 16
		tmp = self.raw[:self.weapon_name_length+16] 
		self.remainder = self.raw[self.weapon_name_length+16:]
		self.raw = tmp	

	def getRemainder(self):
		return self.remainder
	
###########################################################################################################################################################################
## TESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTESTTEST
## Note that the packets for this are variable length because they contain the name of the weapon
###########################################################################################################################################################################
class TestPewPacket(VariableLengthPacket):

	def __init__(self, raw):

		self.weapon_name = ""
		self.weapon_name_length = 0
		self.remainder = ''

		self.position = 0

		super().__init__(raw)

		try:
			self.__parseweaponname()
			self.__parseposition()
			self.__parseremainder()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))	

		if(len(self.raw) < self.weapon_name_length+16):
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex())	

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + self.weapon_name + "]")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<H', len(self.weapon_name)) + self.weapon_name.encode('ascii') + self.position.pack()

	def __parseweaponname(self):
		# the two bytes after the header are the length of the name. They are in little endian?
		self.weapon_name_length = (ord(self.raw[3:4])*256) + ord(self.raw[2:3])

		# next comes the variable portion, for -length- characters
		# check length +16; header (2) + length bytes (2) + the position floats at the end (12) +(?) the associate position packet (?)

		self.weapon_name = self.raw[4:self.weapon_name_length+4].decode('ascii')

	def __parseposition(self):
		self.position = Vector(self.raw[self.weapon_name_length + 4:self.weapon_name_length + 16])

	def __parseremainder(self):
		# two header bytes + two field size bytes (4) plus the length of the name plus a position (12) = 16
		tmp = self.raw[:self.weapon_name_length+16] 
		self.remainder = self.raw[self.weapon_name_length+16:]
		self.raw = tmp	

	def getRemainder(self):
		return self.remainder	
	
###########################################################################################################################################################################
## Chat packet
## variable length because of chatty nonsense
###########################################################################################################################################################################
class ChatPacket(SimpleVariableLengthPacket):

	def __init__(self, raw):

		self.chat = "" 

		super().__init__(raw,0)
		self.__parsechat()

	def __parsechat(self):
		# just an ASCII decoding of the variable length field
		self.chat = self.variablefield.decode('ascii')

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " Local player said [" + self.chat + "]")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<H', len(self.chat)) + self.chat.encode('ascii')

###########################################################################################################################################################################
## Key packet
## eg. the pirate key 6R87D-Y0AVZ-NA3X5-ME2DK-NUA0W
###########################################################################################################################################################################
class KeyPacket(SimpleVariableLengthPacket):

	PIRATEKEY = "6R87D-Y0AVZ-NA3X5-ME2DK-NUA0W"

	def __init__(self, raw):

		self.key = "" 

		super().__init__(raw, 0)
		self.__parsekey()

	def __parsekey(self):
		# just an ASCII decoding of the variable length field
		self.key = self.variablefield.decode('ascii')

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " Submitting key [" + self.key + "]")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<H', len(self.key)) + self.key.encode('ascii')

###########################################################################################################################################################################
## Server Chat packet
###########################################################################################################################################################################
class ServerChatPacket(SimpleVariableLengthPacket):

	def __init__(self, raw):

		self.chat = ""
		self.id = 0

		super().__init__(raw, 4)
		self.__parseid()
		self.__parsechat()

	def __parseid(self):
		self.id = struct.unpack('<I', self.raw[2:6])[0] 

	def __parsechat(self):
		# just an ASCII decoding of the variable length field
		self.chat = self.variablefield.decode('ascii')

	# Override
	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " [" + str(self.id) + "] said [" + self.chat + "]")

	# Implements
	def reconstruct(self):
		self.raw = self.packettype + struct.pack('<I', self.id) + struct.pack('<H', len(self.chat)) + self.chat.encode('ascii')

###########################################################################################################################################################################
## When players come within range, this packet is recvd.
###########################################################################################################################################################################
class ServerPlayerManifestPacket(Packet):

	# hdr  [id    ] [ln] [name                  ] [ln] [groupname     ] [?                                                                             ] [ln] [equipped weapon name          ] [      ] number of status
	# 6e63 a31f0000 0600 72756e72756e             0400 67727032         03 95d4db 00 515151 00 10191f 00 000000 00 a07f17c70bae9ac6f05d1d45 000086ba0000 1000 477265617442616c6c734f6646697265 64000000 0000

	def __init__(self, raw):

		self.id = 0
		
		self.name = ""
		self.name_length = 0
		
		self.groupname = ""
		self.groupname_length = 0
		
		# 17 bytes of Stuff
		self.otherstuff = ''
		
		# Vector object
		self.position = 0

		self.facingstuff = 0		
		
		self.weaponname = ""
		self.weaponname_length = ""
		
		self.sixtyfour = ''		
		
		self.numberofstatuses = 0
		self.statuses = []
		
		self.totallength = 0
		
		self.remainder = ''

		super().__init__(raw)
		
		try:	
			self.__parseid()
			self.__parsename()
			self.__parsegroupname()
			self.__parsestuff()
			self.__parseposition()
			self.__parseweapon()
			self.__parse64()
			self.__parsestatuseffects()
			self.__parseremainder()
		except Exception as e:
			raise IncompletePacketException(self.packettype.hex() + " " + self.raw.hex() + str(e))

	def __parseid(self):
		self.id = struct.unpack('<I', self.raw[2:6])[0]
		
	def __parsename(self):
		self.name_length = (ord(self.raw[7:8])*256) + ord(self.raw[6:7])
		self.name = self.raw[8:self.name_length+8].decode('ascii')
		
	def __parsegroupname(self):
		startpos = 8 + self.name_length # header (2) + id (4) + length (2) + name_length
		self.groupname_length = (ord(self.raw[startpos+1:startpos+2])*256) + ord(self.raw[startpos:startpos+1])
		self.groupname = self.raw[startpos+2:startpos+2+self.groupname_length].decode('ascii')

	def __parsestuff(self):
		startpos = 10 + self.name_length + self.groupname_length # header (2) + id (4) + length (2) + name + length (2) + group name
		# the stuff is 17 bytes long
		self.otherstuff = self.raw[startpos:startpos+17]
		
	def __parseposition(self):
		startpos = 10 + self.name_length + self.groupname_length + 17
		self.position = Vector(self.raw[startpos:startpos+29])
		
		self.facingstuff = self.raw[startpos+29:startpos+35]
	
	def __parseweapon(self):
		startpos = 10 + self.name_length + self.groupname_length + 17 + 18 # stuff + position
		self.weaponname_length = (ord(self.raw[startpos+1:startpos+2])*256) + ord(self.raw[startpos:startpos+1])
		self.weaponname = self.raw[startpos+2:startpos+self.weaponname_length+2].decode('ascii')		

	def __parse64(self):
		startpos = 10 + self.name_length + self.groupname_length + 17 + 18 + self.weaponname_length
		self.sixtyfour = self.raw[startpos:startpos+4]

	def __parsestatuseffects(self):
		
		startpos = 12 + self.name_length + self.groupname_length + 17 + 18 + self.weaponname_length + 4 # header (2) + id (4) + length (2) + name_length + length (2) + group name + other stuff (17) + length (2) + weapon_length + sixtyfour (4)
		self.numberofstatuses = (ord(self.raw[startpos+1:startpos+2])*256) + ord(self.raw[startpos:startpos+1])
		startpos = startpos + 2
		
		# each status consists of a 2-byte length, the string of the status, and a byte denoting "on" or "off"(?)		
		for i in range(0,self.numberofstatuses):
			status_length = (ord(self.raw[startpos+1:startpos+2])*256) + ord(self.raw[startpos:startpos+1])
			self.statuses.append(self.raw[startpos+2:startpos+2+status_length].decode('ascii'))
			
			# let's just ignore that extra byte, but add it to the length
			startpos = startpos + status_length + 2 + 1 # 2 byte length + the length of the string + 1 (for the extra byte)
	
		# there's an extra 00 at the end
			
		self.totallength = startpos
		#print("[" + self.raw.hex() + "] (" + str(self.totallength) + ")")

	def toLoggable(self):
		return ( str(self.packetinfo[0]) + " " + self.name + " [" + str(self.id) + "] group [" + self.groupname + "] using " + self.weaponname + " with status " + str(self.statuses))

	def __parseremainder(self):

		tmp = self.raw[:self.totallength] 
		self.remainder = self.raw[self.totallength:]
		self.raw = tmp	
		
		#print("remainder: [" + self.remainder.hex() + "]")

	def getRemainder(self):
		return self.remainder

	# Implements
	def reconstruct(self):
		# DO THIS D:
		pass


###########################################################################################################################################################################
## Generic "Unknown" packet
## THIS MUST EXTEND PACKET, NOT HEADERPACKET
###########################################################################################################################################################################
class UnknownPacket(Packet):

	def __init__(self, raw):
	
		super().__init__(raw)

	# Implements
	def reconstruct(self):
		pass

