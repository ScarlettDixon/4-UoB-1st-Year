#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:58:51 2019

@author: scarlett
"""

def extendedeuc(a,b):
    r = 0
    q = 0
    lamda11 = 1
    lamda22 = 1
    lamda12 = 0
    lamda21 = 0
    t21 = 0
    t22 = 0
    while b != 0:
        q = int(a / b)
        r = a % b
        a = b
        b = r
        t21 = lamda21
        t22 = lamda22
        lamda21 = lamda11 - q * lamda21
        lamda22 = lamda12 - q * lamda22
        lamda11 = t21
        lamda12 = t22
    return lamda11, lamda12


M = 7
N = 23
g = 6
#z = 0
x = 9
y = 8
q = 11
p = 23
#Totientp = 22
outc1 = 3
outc2 = 10

for z in range(0, q):
   h1 = (g**x)%p
   h2 = (g**y)%p 
   c1 = (g**z)%p
   inp = (h1**z)%p
   (alpha, beta) = extendedeuc(p,inp)
   c2 = (M * beta * (h2**z))%p
   if (outc1 == c1) or (outc2 == c2):
       print("c1:", c1)
       print("c2:", c2)
       print("z:", z)
   
