#!/bin/bash

#Start by clearing out the tables
sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
#sudo iptables -X
sudo iptables -F
echo -e "\n----Table Cleared ----\n"


sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -P INPUT DROP
#Initially no outbound connections were occuring when rules were in place
#researched new, established and related connections
sudo iptables -A INPUT -p tcp  --dport 22  -j ACCEPT
sudo iptables -A INPUT -p tcp  --sport 22  -j ACCEPT
#sudo iptables -A INPUT -p tcp  --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
#sudo iptables -A INPUT -p tcp  --sport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
#sudo iptables -P FORWARD DROP
#sudo iptables -P OUTPUT DROP
sudo iptables -L


#sudo iptables -X
#sudo iptables -P INPUT ACCEPT
#sudo iptables -F
#echo -e "\n----Table Cleared ----\n"
#sudo iptables -L
