#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptabels -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -F
echo -e "\n----Table Cleared ----\n"

#Logs must come first as setting after won't work
sudo iptables -i enp0s3 -A INPUT -p tcp --dport 80 -j LOG -m limit --limit 1/second
sudo iptables -i enp0s3 -A INPUT -p tcp --dport 80 -j DROP

#Left input all the way through as it doesn't hurt
sudo iptables -i enp0s3 -A INPUT -p tcp --dport 80  -j LOG -m limit --limit 1/second
sudo iptables -i enp0s3 -A INPUT -p udp --dport 80 -j DROP 

#Limited to 1 a second
sudo iptables -i enp0s3 -A FORWARD -p tcp --dport 80 -j LOG --log-prefix "PORT 80 TCP:" -m limit --limit 1/second
sudo iptables -i enp0s3 -A FORWARD -p tcp --dport 80 -j DROP 

sudo iptables -i enp0s3 -A FORWARD -p udp --dport 80 -j LOG --log-prefix "PORT 80 UDP:"-m limit --limit 1/second
sudo iptables -i enp0s3 -A FORWARD -p udp --dport 80 -j DROP 

sudo iptables -L

