#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
#sudo iptables -X
sudo iptables -F
echo -e "\n----Table Cleared ----\n"

#Allow loopback as system seems to crash if not
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A FORWARD -i lo -j ACCEPT

sudo iptables -P FORWARD DROP

#Block all connections to client apart from server
sudo iptables -i enp0s8 -A FORWARD -p tcp  -s 192.168.101.2 -j ACCEPT 

#Now set what is allowed to come from client
#Allow only connections in the /24 range that are to port 22 or 80
#(Pre-defined allowed ports) this should also block IP spoofing
sudo iptables -i enp0s3 -A FORWARD -p tcp  -s 192.168.100.0/24 -d 192.168.101.2 -m multiport --dport 22,80 -j ACCEPT

#Block broadcasts from client-net
sudo iptables -i enp0s3 -A FORWARD -p tcp  -s 192.168.100.255 -j DROP

sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

sudo iptables -L

#sudo iptables -X
#sudo iptables -P INPUT ACCEPT
#sudo iptables -F
#echo -e "\n----Table Cleared ----\n"
#sudo iptables -L
