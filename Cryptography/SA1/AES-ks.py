#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for i:= 1to10do
        T:=W4i−1≪8
        T:= SubBytes(T)
        T:=T⊕RCi - XOR T with a round constant RCi
        W4i:=W4i−4⊕T - Define next W word by XORing with T or the previous word
        W4i+1:=W4i−3⊕W4i
        W4i+2:=W4i−2⊕W4i+1
        W4i+3:=W4i−1⊕W4i+2
    end

"""
T = "101"
W1 = ""
W2 = ""
W3 = ""
W4 = ""

for i in range(1,11):
    print(i)
    T = W1
