#!/bin/bash

sudo iptables -L
sudo iptables -P INPUT ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -F
sudo iptables -X
echo -e "\n----Table Cleared ----\n"
sudo iptables -L
