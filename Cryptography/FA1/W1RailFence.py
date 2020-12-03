# -*- coding: utf-8 -*-
"""
Rail Fence Cipher -
    Key - Column Size K
    Encryption - Arrange in column of size K, writing downwards until key length reached
    Ciphertext - read across columns
    Decryption - Divide Length into key number of parts, arrange message in rows of this size. Plaintext consists of columns
    
    Example
    To be or not to be
    Key 2
    
    tbontoe
    oerotb
    
    ciphertext output - tbontoeoerotb
    Insecure becuase the key can't be greater than the message, can try all the keys very quickly
    Secure is subjective, based on situation and adversary
    
DES -  
    DES has 56 bit keys. Can re-use a key as often as you want. you can encrypt text that is as long as you want
    Key size is too small for todays computers
    Variants - 3DES, 
        DES 3 times, still quite secure but AES has overtaken
        Block length is 64 bits 
        Key lenght is 56 bits - 64 bits but 8 are parity
        DES consists of 16 "rounds", each round uses a roundkey created from the main key 
    Operations - 
        Cyclic Shifts - On bitstring blocks, Will denote by b <<< n the move of block b by n to the left. Bits that would have fallen out are added at the right side of the b.
        Permutations on the position of bits - Written down as the output order of the input bits, {look into this}
    Key Schedule - 
        First apply a permutation PC-1 which removes the parity bits. This results in 56 bits
        Split result into half to obtain (Co, Do)
        
        
        Task 3: What is the output of the first round of the DES algorithm when the plaintext and the key are both all zeros?
        Task 4: Remember that it is desirable for good block ciphers that a change in one
            input bit affects many output bits, a property that is called diffusion or
            avalanche effect. We will try to get a feeling for the avalanche property of
            DES. Let x be all zeros (0x0000000000000000) and y be all zeros except 1
            in the 13th bit (0x0008 000000000000). Let the key be all zeros.
            After just one round, how many bits in the block are different when x is
            the input, compared to when y is the input? What about after two rounds?
            Three? Four?
            (For this exercise, you might like to search for an implementation of DES
             on the web, and download it and modify it to output the answers.)

"""

import numpy as np
import math as m
import binascii as biasc
import cryptography as crypto

class RailFence:
    def initialise():
        print("Hello World")
        usr_inp = "hello world"
        usr_inp = "To be or not to be"
        usr_inp = "tobeornottobe"
        exerone="AVUEVLETSEISBNACBOOLEOBTILBDLCOBOOE" #
        key = 5
        keytest = 5
        inp = "ALICELOVESBOBBUTBOBDOESNOTLOVEALICE"
        cipher = RailFence.Encrypt(key, usr_inp)
        cipher2 = RailFence.Encrypt(keytest, inp)
        print(cipher2)
        #print (cipher)
        for i in range(2,len(exerone)):
            orig = RailFence.Decrypt(i, exerone)
            print(orig)
        for j in range(2, len(usr_inp)):
            orig = RailFence.Decrypt(j, cipher)
            print(orig)
    
    
    def Encrypt(k, inp):
        print("Encrypting...")
        print("Key is " + str(k))
        colsize = k
        colcount = 0
        rowsize = m.ceil(len(inp) / colsize)
        #print(rowsize)
        rowcount = 0
        store = np.empty([colsize, rowsize], dtype = str)
        #print(store.shape)
        for chars in inp:
            #print(chars)
            if colcount < colsize:
                store[colcount, rowcount] = chars
                colcount+=1
            else :
                colcount = 0
                rowcount+=1
                store[colcount, rowcount] = chars
                colcount+=1
    
        ciphertext = ""
        colcount = 0
        rowcount = 0
        for char2 in inp:
            if rowcount < rowsize:
                temp = str(store[colcount, rowcount])
                #print (temp)
                ciphertext += temp
                rowcount+=1
            else :
                rowcount = 0
                colcount+=1
                ciphertext += str(store[colcount, rowcount])
                rowcount+=1
        print(store)
        print("Done")
        return ciphertext
        
       
    def Decrypt(k, inp):
        print("Decrypting...")
        print("Key is " + str(k))
        origplain = ""
        colsize = m.ceil(len(inp) / k)
        colcount = 0
        rowsize = k
        rowcount = 0
        store = np.empty([rowsize, colsize], dtype = str)
        for chars in inp:
            if rowcount < rowsize:
                store[rowcount, colcount] = chars
                rowcount+=1
            else :
                rowcount = 0
                colcount+=1
                store[rowcount, colcount] = chars
                rowcount+=1
        #print(store)
        colcount = 0
        rowcount = 0
        for chars2 in inp:
            #print(str(rowcount) + " " + str(colcount))
            if colcount < colsize:
                origplain += store[rowcount, colcount]
                colcount+=1
            else :
                colcount = 0
                rowcount+=1
                #print(rowcount)
                origplain += store[rowcount, colcount]
                
                colcount+=1
        return origplain
    
class feistel:
    def initialise():
        print("initialising")
        #https://stackoverflow.com/questions/3114107/modulo-in-order-of-operation
        Keyprime = 89
        Keyzero = ((Keyprime + 75 * 0)%256)
        Keyone = ((Keyprime + 75 * 1)%256)
        print(Keyone)
        Leftinp = 86
        Rightinp = 83
        feistel.encr(Leftinp, Rightinp, Keyzero, Keyone)
        Leftinp = 9
        Rightinp = 2
        feistel.decr(Leftinp, Rightinp, Keyzero, Keyone)
        
    def encr (left, right, kz, ko):
        leftout = right
        feistfunczero = ((127 * (kz + right))% 256)
        rightout = left ^ feistfunczero 
        left = leftout
        right = rightout
        rightout = right
        feistfuncone= ((127 * (ko + right))% 256)
        leftout = left ^ feistfuncone
        ciphertext = str(leftout) + " " + str(rightout)
        print(ciphertext)
        
    def decr (left, right, kz, ko):
        leftout = right
        feistfunczero = ((127 * (ko + right))% 256)
        rightout = left ^ feistfunczero 
        left = leftout
        right = rightout
        rightout = right
        feistfuncone= ((127 * (kz + right))% 256)
        leftout = left ^ feistfuncone
        plaintext = str(leftout) + " " + str(rightout)
        print(plaintext)
        
        
class DES:
    def init(choice):
        PI = [58, 50, 42, 34, 26, 18, 10, 2,
              60, 52, 44, 36, 28, 20, 12, 4,
              62, 54, 46, 38, 30, 22, 14, 6,
              64, 56, 48, 40, 32, 24, 16, 8,
              57, 49, 41, 33, 25, 17, 9, 1,
              59, 51, 43, 35, 27, 19, 11, 3,
              61, 53, 45, 37, 29, 21, 13, 5,
              63, 55, 47, 39, 31, 23, 15, 7]
        
        PC_1 = [57, 49, 41, 33, 25, 17, 9,
                1, 58, 50, 42, 34, 26, 18,
                10, 2, 59, 51, 43, 35, 27,
                19, 11, 3, 60, 52, 44, 36,
                63, 55, 47, 39, 31, 23, 15,
                7, 62, 54, 46, 38, 30, 22,
                14, 6, 61, 53, 45, 37, 29,
                21, 13, 5, 28, 20, 12, 4]
        
        PC_2 = [14, 17, 11, 24, 1, 5, 3, 28,
                15, 6, 21, 10, 23, 19, 12, 4,
                26, 8, 16, 7, 27, 20, 13, 2,
                41, 52, 31, 37, 47, 55, 30, 40,
                51, 45, 33, 48, 44, 49, 39, 56,
                34, 53, 46, 42, 50, 36, 29, 32]
        
        InitPerm = [57, 49, 41, 33, 25, 17,  9,
                    1, 58, 50, 42, 34, 26, 18,
                    10,  2, 59, 51, 43, 35, 27,
                    19, 11,  3, 60, 52, 44, 36,
                    63, 55, 47, 39, 31, 23, 15,
                    7, 62, 54, 46, 38, 30, 22,
                    14,  6, 61, 53, 45, 37, 29,
                    21, 13,  5, 28, 20, 12,  4]
        FinalPerm = [40,  8, 48, 16, 56, 24, 64, 32,
                     39,  7, 47, 15, 55, 23, 63, 31,
                     38,  6, 46, 14, 54, 22, 62, 30,
                     37,  5, 45, 13, 53, 21, 61, 29,
                     36,  4, 44, 12, 52, 20, 60, 28,
                     35,  3, 43, 11, 51, 19, 59, 27,
                     34,  2, 42, 10, 50, 18, 58, 26,
                     33,  1, 41,  9, 49, 17, 57, 25]
        Expansion = [32,  1,  2,  3,  4,  5,  4,  5,
                     6,  7,  8,  9,  8,  9, 10, 11,
                     12, 13, 12, 13, 14, 15, 16, 17,
                     16, 17, 18, 19, 20, 21, 20, 21,
                     22, 23, 24, 25, 24, 25, 26, 27,
                     28, 29, 28, 29, 30, 31, 32,  1]
        Rotations = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
        SBox = [
       [14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7,
        0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8,
        4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0,
       15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13],
 
       [15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10,
        3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5,
        0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15,
       13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9],
     
       [10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8,
       13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1,
       13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7,
        1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12],
     
       [ 7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15,
       13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9,
       10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4,
        3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14],
     
       [ 2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9,
       14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6,
        4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14,
       11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3],
     
       [12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11,
       10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8,
        9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6,
        4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13],
     
       [ 4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1,
       13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6,
        1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2,
        6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12],
       
       [13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7,
       1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2,
       7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8,
       2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11]]
        
        #print(SBox)
        PBox = [16,  7, 20, 21, 29, 12, 28, 17,
                1, 15, 23, 26,  5, 18, 31, 10,
                2,  8, 24, 14, 32, 27,  3,  9,
                19, 13, 30,  6, 22, 11,  4, 25]
        #Some code taken from https://jhafranco.com/2012/01/16/des-implementation-in-python-3/
        
        Input = np.zeros([64])
        Inchoice = 1
        if choice == 3:
            DES.initialisethree(SBox, PBox)
        else:
            DES.initialisefour(Input, InitPerm, FinalPerm, Expansion, Rotations, Inchoice)
        
    def initialisethree(SB, PB):
        print("initialising")
        #All values are zero so Initial permutation, final permutation and the key schedule/rotations will do nothing to change the items
        #This is the same within the feistel function for expansion and round key addition, all of which will just output 0s
        #The SBox and PBox are where changes may occur
        #byte_inp = bytes(6)
        plainbits = np.zeros([64])
        leftIn = np.zeros([48]) #Assuming an expansion has already been completed
        rightIn =np.zeros([32])
        leftOut = rightIn
        print(leftOut)
        #for i in range(leftIn):
        #feistFunc = np.zeros([48])
        #rightOut = feistFunc ^ leftIn
        #print(str(leftOut) + str(rightOut))
        #keybits = np.zeros([64])
        #Firstperm
        #Finperm
        #print(plainbits)
        #print(type(byte_inp))
        #print(byte_inp)
        #print(int.from_bytes(byte_inp, "little"))
        #print(biasc.unhexlify(byte_inp))
        #print(int(byte_inp, 64))
        #crypto
#        plaint = 0000000000000000
        #inp = "test"
        #outp = biasc.hexlify(inp)
        #print (outp)
        
    def initialisefour(In, IP, FP, EP, RO, IC):
        print("Initialising")
        if IC == 0:
            print("Inputting x")
        else:
            print("Inputting y")
            In[12] = 1
        Key = np.zeros([64])
        #print(Key)
        InitPerm = np.zeros([64])
        Leftin = np.zeros([32])
        Rightin = np.zeros([32])
        Leftout = np.zeros([32])
        Rightout = np.zeros([32])
        Expand = np.zeros([48])
        PBox = np.zeros([32])
        FinPerm = np.zeros([64])    
        count = 0
        for i in IP:
            #print(i)
            InitPerm[count] = In[i]
            count+=1
        (Leftin, Rightin) = np.split(InitPerm, 2)
        #print(Leftiny, Rightiny)
        for j in range(1,5):
            Leftout = np.copy(Rightin)
            print(Leftout)
            Rightout = np.bitwise_xor(Leftin, Leftout)
            print(Rightout)
            
            
       

        
        
if __name__ == "__main__":
    #RailFence.initialise()
    #Task 1: Key is 7
    #ALICELOVESBOBBUTBOBDOESNOTLOVEALICE
    #feistel.initialise()
    DES.init(4)
    print("Done")
    

    