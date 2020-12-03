#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -F
echo -e "\n----Table Cleared ----\n"

sudo iptables -A INPUT -p tcp --dport 80 -j REJECT
sudo iptables -A INPUT -p udp --dport 80 -j REJECT
sudo iptables -L
