#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
#sudo iptables -X
sudo iptables -F
echo -e "\n----Table Cleared ----\n"

#An issue with my system involves iptables breaking if all INPUT is dropped
#without loopback being accepted beforehand
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A FORWARD -i lo -j ACCEPT

#Drop all Input and Forward connections
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP

#Allow Forwaded connections, all connections from server, 
#and ssh connection from all of client-net
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A FORWARD -p tcp  -s 192.168.100.0/24 --dport 22 -j ACCEPT
sudo iptables -A FORWARD -p tcp  -s 192.168.101.2 -j ACCEPT
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -L

#sudo iptables -X
#sudo iptables -P INPUT ACCEPT
#sudo iptables -F
#echo -e "\n----Table Cleared ----\n"
#sudo iptables -L
