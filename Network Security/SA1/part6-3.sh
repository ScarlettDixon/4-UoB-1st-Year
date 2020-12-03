#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -F 
sudo iptables -X LOGGER
echo -e "\n----Table Cleared ----\n"

sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A FORWARD -i lo -j ACCEPT

#sudo iptables -P INPUT DROP

sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A FORWARD -p tcp  -s 192.168.100.0/24 --dport 22 -j ACCEPT
sudo iptables -A FORWARD -p tcp  -s 192.168.101.2 -j ACCEPT
sudo iptables -L

#sudo iptables -X
#sudo iptables -P INPUT ACCEPT
#sudo iptables -F
#echo -e "\n----Table Cleared ----\n"
#sudo iptables -L

#system for creating a new chain specifically for logging other chains
sudo iptables -N LOGGER
sudo iptables -A FORWARD -j LOGGER
sudo iptables -A LOGGER -j LOG  -m limit --limit 1/second
sudo iptables -A LOGGER -j DROP
