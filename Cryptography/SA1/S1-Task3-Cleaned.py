#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import random
#import string
import time

class Task_3:
    def __init__(self):
        self.implement()
    
    def get_random(stp): #Unused for final run
        strcount = 0
        strleng = random.randint(1,20) #Choose a random integer between 1 and 20
        output = []
        while strcount < strleng:
          output.append(random.choice(stp)) #Append on a random char from StrPoss
          strcount+=1
        out = ''.join(output)
        return out
    
    def implement(self):
        #StrPoss = string.ascii_letters+string.digits #All possibile string characters
        Tries = 0 #Number of Tr
        diction = {}
        run = True
        start_time = time.time() #Calculates time taken to find collision
        InputIntoMem = True #Implimented in later i
        while run == True:
            Tries +=1
            #Input = Task_3.get_random(StrPoss) #Initially used but was drastically slowing down speed
            Input = str(Tries)
            Hashed = hashlib.sha1(Input.encode("ascii")).hexdigest() #Hashes the Input with SHA1
            Hashed = Hashed[0:15] # Cuts down the Hash to the length needed: 8 and 10 in testing, 15 final
            if (Tries % 1000000) == 0: #Used to keep reasonably track of how many tries taken place
                print("Number of tries made so far" ,Tries) 
                print(Input)
            if (Tries % 20000000) == 0: #Put into place to stop new input into RAM
                InputIntoMem = False
            if (Hashed not in diction.keys()) and (InputIntoMem == True): 
                    diction[Hashed] = Input 
                    #Was initially a memory error trycatch statement but removed as not needed anymore
            elif (Hashed in diction.keys()) and (diction[Hashed] != Input):
                print ("Collision found")
                print("Number of tries made:" ,Tries)
                print("Taking %s seconds" % (time.time() - start_time))
                HashedInpOne = hashlib.sha1(Input.encode("ascii")).hexdigest()
                HashedInpTwo = hashlib.sha1(diction[Hashed].encode("ascii")).hexdigest()
                print("Plaintext one is:", Input)
                print("Plaintext two is:", diction[Hashed])
                print("The full hash for the first plaintext is:",HashedInpOne)
                print ("The full hash for the first plaintext is:", HashedInpTwo)
                print ("The part of the hash shared is:", Hashed)
                break
                
if __name__ == "__main__":
    t3 = Task_3()
    
