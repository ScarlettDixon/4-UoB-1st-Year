#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 14:16:54 2019

@author: scarlett
"""
Xoutzero="0000000000000000000000000000000000000000000000000000000000000000"   
Xoutone= "0000000000000000000000000000000011011000110110001101101110111100"
Xouttwo= "1101100011011000110110111011110011100111001110101110110101001111"
Xoutthr= "1110011100111010111011010100111101011011111110100110101110100110"
Xoutfou= "0101101111111010011010111010011001011110010001011110001001010111"
Xtab = [Xoutzero, Xoutone, Xouttwo, Xoutthr, Xoutfou]

Youtzero="0000000000001000000000000000000000000000000000000000000000000000"   
Youtone= "0000000000000000000000100000000011011000111110001101101110110100"
Youttwo= "1101100011111000110110111011010011100101001010001110001001101011"
Youtthr= "1110010100101000111000100110101110000111110101110000001000110110"
Youtfou= "1000011111010111000000100011011000111101000101001111010100111100"
Ytab = [Youtzero, Youtone, Youttwo, Youtthr, Youtfou]

check = 0

for i in range((len(Xtab) - 1)):
    check = 0
    for num, bina in enumerate(Xtab[i], start=0):
        indexer = Xtab[i + 1]
        if bina != indexer[num]:
            check +=1
    print("X:" + str(check) + " Percent:" + str((check/64) * 100))
    
print("")

for i in range((len(Ytab) - 1)):
    check = 0
    for num, bina in enumerate(Ytab[i], start=0):
        indexer = Ytab[i + 1]
        if bina != indexer[num]:
            check +=1
    print("Y:" + str(check) + " Percent:" + str((check/64) * 100))
    
print("")

for j in range(len(Xtab)):
    check = 0
    for num, bina in enumerate(Xtab[i], start=0):
        indexx = Xtab[j]
        indexy = Ytab[j]
        if indexx[num] != indexy[num]:
            check+=1
    print(str(j)+":" + str(check) + " Percent:" + str((check/64) * 100))
	
#print(len(Temp))
#for i in range(len(Xtab)):
#    if Xoutzero[count] != Xoutone[count]:
#        check+=1
#    #print(i)
#    #print (Xoutone[count]) 
#    count+=1
#print(check)
#colors = ["red", "green", "blue", "purple"]
#for i in range(len(colors)):
#    print(colors[i])
    
#presidents = ["Washington", "Adams", "Jefferson", "Madison", "Monroe", "Adams", "Jackson"]
#for num, name in enumerate(presidents, start=1):
#    print("President {}: {}".format(num, name))

