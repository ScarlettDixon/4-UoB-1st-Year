#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -F
echo -e "\n----Table Cleared ----\n"

#Added forward to ensure the connection across is blocked for port 80
#kept INPUT REJECTs because they don't reduce security and keep the
#router safer
sudo iptables -i enp0s3 -A INPUT -p tcp --dport 80 -j REJECT
sudo iptables -i enp0s3 -A INPUT -p udp --dport 80 -j REJECT
sudo iptables -i enp0s3 -A FORWARD -p tcp --dport 80 -j REJECT
sudo iptables -i enp0s3 -A FORWARD -p udp --dport 80 -j REJECT

sudo iptables -L

