#!/bin/bash

#Start by clearing out the tables
sudo iptables -L

sudo iptables -t nat -A POSTROUTING -j SNAT --to-source 10.42.76.5


#sudo iptables -L
#sudo iptables -X
#sudo iptables -P INPUT ACCEPT
#sudo iptables -F
#echo -e "\n----Table Cleared ----\n"
#sudo iptables -L
