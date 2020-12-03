#!/usr/bin/env python
 
import socket
import threading
import logger
import datetime
import time
import packet as pkt
import switchboard

def main():
	
	## centralised logger thread so we can keep everything centralised between multiple executing threads. Logging is great.
	t = time.strftime("%a %d/%m/%Y %H:%M:%S", time.localtime(time.time()))
	log = logger.FileLogger("proxy.log")
	log.addAndPrint(" -- Proxy started " + t + " --")

	## We used to work with two proxy connections - but really, all we did with the auth proxy was tunnel it. That's sort of pointless
	## Let's let the game connect to the auth server without our intervention, and rely on our preload to redirect game traffic to us.
	## We also no longer need our config file - we'll just be extra and listen on all ports. We can just do that.

	log.addAndPrint("Starting switchboard.\nIf the program recently crashed or was CTRL-C'd recently, you may have to wait.")
	
	## the game connection proxy (on 3000-3009)
	## let's set up a switchboard for this. All the magic happens there - we can just do console things.
	switchboard.Switchboard.SERVERADDRESS = "bhm-ercc-dl380.rjthomas.eu"
	try:
		sb = switchboard.Switchboard(log)
	except OSError as e:
		log.addAndPrint("Critical error: Could not initialise switchboard: " + str(e))
		log.kill()
		exit()

	print("Console ready; exit to close.")	

	while True:
		command = input().lower()
		
		# all my pennies for switch/case
		if ( command == "exit" ):
			log.add("[Local Console] Command: exit")
			print("Exiting...")
			sb.kill()
			log.kill()
			exit()

		elif ( (command[:5] == "show ") or (command[:5] == "hide ") ):
			packet = command[5:7]
			packet = packet.encode('ascii')

			client_failed = False
			server_failed = False

			show = True
			if(command[:4] == "hide"):
				show = False

			try:
				entry = pkt.Packet.client_packet_types[packet]
				pkt.Packet.client_packet_types[packet] = (entry[0], entry[1], show)
			except KeyError as e:
				client_failed = True

			try:
				entry = pkt.Packet.server_packet_types[packet]
				pkt.Packet.server_packet_types[packet] = (entry[0], entry[1], show)
			except KeyError as e:
				server_failed = True

			if(client_failed and server_failed):
				print("Packet type " + str(packet) + " isn't registered.")

		elif (command[:7] == "status"):
			print("Packet types (Client): ")
			for x in pkt.Packet.client_packet_types:
				print(x.decode('ascii') + " " + str(pkt.Packet.client_packet_types[x]))

			print("Packet types (Server): ")
			for x in pkt.Packet.server_packet_types:
				print(x.decode('ascii') + " " + str(pkt.Packet.server_packet_types[x]))

		else:
			log.add("[Local Console] Unknown command: " + command)
			print("Unknown command: " + command)
			
			
main()