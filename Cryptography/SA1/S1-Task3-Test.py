#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
https://stackoverflow.com/questions/32484504/using-random-to-generate-a-random-string-in-bash
http://www.algolist.net/Data_structures/Hash_table/Simple_example
https://docs.python.org/3/library/stdtypes.html#dict
https://docs.python.org/2/library/subprocess.html#module-subprocess
https://docs.python.org/2/library/hashlib.html
https://github.com/MarcoMorella/SHA1Collider
"""

#import subprocess
#import hashlib



#test = dict('hello'=1, 'world'=2)
#test = {'hello':1, 'world':2}
#print(list(test))

#subprocess.check_call(["ls"])
#print(subprocess.call(["ls", "-l"]))
#print(subprocess.check_output(["ls", "-l"]))
#out = subprocess.check_output(["echo", "-n", "str", "|", "sha1sum", "-","|""cut -c1-15"])
#out2 = subprocess.check_output(["echo", -n ,"str"])
#print(hashlib.algorithms_available)
#test2 = hashlib.sha1('hello')
#h = hashlib.new('sha1')
#hashlib.
#test = b"Hello"
#h = hashlib.md5()
#h.update(test)
#h.digest()
#h.digest("mark")
#h.digest()
#print(h.digest())
#hashlib.

import hashlib
import random
import string
import time

class Task_3:
    
    def get_random(stp):
        strcount = 0
        strleng = random.randint(1,10) #Choose a random integer between 1 and 20
        #print(strleng)
        output = []
        while strcount < strleng:
          output.append(random.choice(stp))
          #output2 = ''.join(random.choice(stp))
          #print (output2)
          strcount+=1
        #print(output)
        out = ''.join(output)
        return out#''.join(random.sample(s,N))
    
    def implement():
        #
        #N = 2 #String Length
        #M = 4 #Number of hexdigest's digit to check
        StrPoss = string.ascii_letters+string.digits #All possibile string characters
        #Strleng = string.digits
        #print(len(s))
        Tries = 0 #Tries done before finishing
        diction = {}
        
        run = True
        start_time = time.time()
        InputIntoMem = True
        while run == True :
            
            Tries +=1
            Input = Task_3.get_random(StrPoss)
            Hashed = hashlib.sha1(Input.encode("ascii")).hexdigest()
            Hashed = Hashed[0:8]
            #print(Hashed[-M:])
            #print(-M)
            if (Tries % 1000000) == 0:
                print("Number of tries made so far" ,Tries)
            if (Tries % 1000) == 0:
                InputIntoMem = False
            
            if (Hashed not in diction.keys()) and (InputIntoMem == True):
                try: #In case of too much memory usage
                    diction[Hashed] = Input
                except MemoryError:
                    print("LOG: MemoryError")
                    diction = {}
            elif (Hashed in diction.keys()) and (diction[Hashed] != Input):
                print ("Collision found")
                print("Number of tries made:" ,Tries)
                print("Taking %s seconds" % (time.time() - start_time))
                HashedInpOne = hashlib.sha1(Input.encode("ascii")).hexdigest()
                HashedInpTwo = hashlib.sha1(diction[Hashed].encode("ascii")).hexdigest()
                #HashedInp = HashedInp[1:8]
                print("Plaintext one is:", Input)
                print("Plaintext two is:", diction[Hashed])
                print("The full hash for the first plaintext is:",HashedInpOne)
                print ("The full hash for the first plaintext is:", HashedInpTwo)
                print ("The part of the hash shared is:", Hashed)
                #print ()
                #run = False
                break
                
                    #print("Found an already used string!")
                    #
                    #print("Key collision index" , Hashed[-M:])
                    #print("Ciphertext", Input)
                    #exit
                    #run = False
                #else :
                    
        #print("--- %s seconds ---" % (time.time() - start_time))
        #print("Number of tries made" ,Tries)
        
        #colliding = dict[Hashed[-M:]]
        #collHash = hashlib.sha1(colliding.encode("ascii")).hexdigest()
        #print (colliding+'\n'+collHash+'\n'+TryString+'\n'+Hashed)


if __name__ == "__main__":
    test = "mark"
    Hashedtest = hashlib.sha1(test.encode("ascii")).hexdigest()
    #print(Hashedtest)
    Task_3.implement()