#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

import time
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
#from matplotlib.pyplot import imread
import random
#from PIL import Image
#import cv2

#--------------------------------
#All csvs
#--------------------------------
#map_centre='centre.csv'
map_player='player.csv'
map_otherp='otherplayers.csv'
map_loot='loot.csv'
map_egg='eggs.csv'
map_shop='shops.csv'
map_monsters='monsters.csv'
teleport="clickteleport.csv"
#map_align='align.csv'

x_max_Glo=100000
y_max_Glo=100000  
x_min_Glo=-100000
y_min_Glo=-100000  
point_size_Glo=15

x_max_Loc=10000
y_max_Loc=10000 
x_min_Loc=-10000
y_min_Loc=-10000   
#play_Loc=[1000,1000] 
point_size_Loc=30


#--------------------------------
#Function for Debugging
#Outputs random data to different csvs (currently player position)
#Used to check the ability of the map to update and then for checking where lag came from
#--------------------------------
def update(z): 
    try:
        num = random.randint(1,5)
        data = np.zeros(shape=(num, 3))
        for i in range(0, num):
            out1 = random.randint(x_min_Glo,x_max_Glo)
            out2 = random.randint(y_min_Glo,y_max_Glo)
            data[i,0] = out1
            data[i,1] = out2
            data[i,2] = z
            np.savetxt(map_player, data, delimiter=",")
    except:
        print("Exiting")

#--------------------------------
#The teleport function
#When the plots are clicked (Need to check if local works)
#The xdata and ydata are taken and outputted to a csv file to be used by preload
#--------------------------------
def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
    out=np.empty((1,4), dtype=object)
    out[0,0] = "click"
    out[0,1] = event.xdata
    out[0,2] = event.ydata
    out[0,3] = 15500
    print(out)
    np.savetxt(teleport, out, delimiter=",", fmt="%s %f %f %f")




if __name__ == "__main__":
    #try:
        x = 0.0
        y = 0.0
        #All these only need to be generated once as they are static
        #Attempts were made to have interactions be noted by the map
        #Such as when picking up the egg, but unfortunately this was not possible in time given
        data4 = genfromtxt(map_loot,delimiter=',', names=['id','x', 'y', 'z'], dtype=("S20,f8,f8,f8"))
        data5 = genfromtxt(map_egg,delimiter=',', names=['id','x', 'y', 'z'], dtype=("S20,f8,f8,f8"))
        data6 = genfromtxt(map_shop,delimiter=',', names=['id','x', 'y', 'z'], dtype=("S20,f8,f8,f8"))
        #Used to align the image of the map with the plotted data
        #Went to viable location on map (near coast or centre), noted position and then aligned it to plot
        #Had to edit the image seperately in gimp
        #data6 = genfromtxt(map_align,delimiter=',', names=['id','x', 'y', 'z'], dtype=("S20,f8,f8,f8"))
        
        #Creates one figure with two plots
        plt.ion()
        fig = plt.figure(figsize=(10,10))
        #--------------------------------
        #Global setup
        #--------------------------------
        subGlobal = fig.add_subplot(121)
        subGlobal.set_title('Global Map')
        #subGlobal = fig.add_subplot(111)
        subGlobal.set_xlim([x_min_Glo,x_max_Glo])
        subGlobal.set_ylim([y_min_Glo,y_max_Glo])
        
        p1, = subGlobal.plot(x, y, 'k.')#, label="Centre")
        p2, = subGlobal.plot(x, y, 'g.', label="Player")
        p3, = subGlobal.plot(x, y, 'b.', label="Other Players")
        p4, = subGlobal.plot(x, y, 'w.', label="Loot")
        p5, = subGlobal.plot(x, y, 'y.', label="Eggs")
        p6, = subGlobal.plot(x, y, 'm.', label="Shops")
        p7, = subGlobal.plot(x, y, 'r.', label="Monsters")
        #p11,= subGlobal.plot(x, y, 'k.', label="Aligner")
        p1.set_markersize(5)
        p2.set_markersize(point_size_Glo)
        p3.set_markersize(point_size_Glo)
        p4.set_markersize(point_size_Glo)
        p5.set_markersize(point_size_Glo)
        p6.set_markersize(point_size_Glo)
        p7.set_markersize(point_size_Glo)
        #p11.set_markersize(point_size_Glo)
        
        p4.set_xdata(data4['x'])
        p4.set_ydata(data4['y'])
        p5.set_xdata(data5['x'])
        p5.set_ydata(data5['y'])
        p6.set_xdata(data6['x'])
        p6.set_ydata(data6['y'])
        
        #p11.set_xdata(data6['x'])
        #p11.set_ydata(data6['y'])
        #print(data3['x'].shape[0])
        #subGlobal.annotate(data3['id'], xy=(data3['x'],data3['y']))
        plt.legend(loc="upper left")
        plt.grid()
        #img = Image.open("island_final.png")
        img = plt.imread("island_final.png")
        #img = img.resize((370000,370000))
        plt.imshow(img, extent = [x_min_Glo, x_max_Glo, y_min_Glo, y_max_Glo])#,interpolation='nearest', aspect='auto')#origin='upper'
        
        #--------------------------------
        #Local setup
        #--------------------------------
        subLocal = fig.add_subplot(122)
        subLocal.set_title('Local Map')
        #subLocal.margins(2,2)
        subLocal.set_xlim([0,x_max_Loc])
        subLocal.set_ylim([0,y_max_Loc])
        p8, = subLocal.plot(x, y, 'k.', label="Centre")
        p9, = subLocal.plot(x, y, 'g.', label="Player")
        p10,= subLocal.plot(x, y, 'b.', label="Other Players")
        p11,= subLocal.plot(x, y, 'w.', label="Loot")
        p12,= subLocal.plot(x, y, 'y.', label="Egg")
        p13,= subLocal.plot(x, y, 'm.', label="Shop")
        p14,= subLocal.plot(x, y, 'r.', label="Monsters")
        
        p8.set_markersize(point_size_Loc)
        p9.set_markersize(point_size_Loc)
        p10.set_markersize(point_size_Loc)
        p11.set_markersize(point_size_Loc)
        p12.set_markersize(point_size_Loc)
        p13.set_markersize(point_size_Loc)
        p14.set_markersize(point_size_Loc)
        
        
        
        p11.set_xdata(data4['x'])
        p11.set_ydata(data4['y'])
        p12.set_xdata(data5['x'])
        p12.set_ydata(data5['y'])
        p13.set_xdata(data6['x'])
        p13.set_ydata(data6['y'])
        
        plt.legend(loc="upper right")
        plt.grid()
        #plt.imshow(img,interpolation='nearest', aspect='auto')#origin='upper'
        #img = Image.open("radar.png")
        #img = plt.imread("radar.png")
        
        #img = img.resize((2000,2000))
        #plt.imshow(img, extent = [x_min_Loc, x_max_Loc,y_min_Loc,y_max_Loc])
        
        while True:
            #--------------------------------
            #Updating data
            #--------------------------------
            #update(5)
            time.sleep(0.01)
            #plt.close()
            #data  = genfromtxt(map_centre, delimiter=',', names=['id','x', 'y', 'z'])
            data2 = genfromtxt(map_player, delimiter=',', names=['id','x', 'y', 'z'])
           # img = Image.open("radar.png")
            #plt.imshow(img, extent = [(data2['x'] + x_min_Loc), (data2['x'] + x_max_Loc),(data2['y'] + y_min_Loc), (data2['y'] + y_max_Loc)])
            #destroyWindow(img)
            #img.close()
            #img.close()
            data3 = genfromtxt(map_otherp, delimiter=',', names=['id', 'x', 'y', 'z'])
            data7 = genfromtxt(map_monsters, delimiter=',', names=['id', 'x', 'y', 'z'])
            
            #Sets the local graph parameters depending on the player position
            subLocal.set_xlim([data2['x'] + x_min_Loc, data2['x'] + x_max_Loc])
            subLocal.set_ylim([data2['y'] + y_min_Loc, data2['y'] + y_max_Loc])
            
            #p1.set_xdata(data['x'])
            #p1.set_ydata(data['y'])
            p2.set_xdata(data2['x'])
            p2.set_ydata(data2['y'])
            p3.set_xdata(data3['x'])
            p3.set_ydata(data3['y'])
            p7.set_xdata(data7['x'])
            p7.set_ydata(data7['y'])
            
            #p6.set_xdata(data['x'])
            #p6.set_ydata(data['y'])
            p9.set_xdata(data2['x'])
            p9.set_ydata(data2['y'])
            p10.set_xdata(data3['x'])
            p10.set_ydata(data3['y'])
            p14.set_xdata(data7['x'])
            p14.set_ydata(data7['y'])
            
            cid = fig.canvas.mpl_connect('button_press_event', onclick)
            
            fig.canvas.draw()
            fig.canvas.flush_events()




#subGlobal.annotate(data3['id'], xy=(data3['x'],data3['y']))
            #for xy in p3:
            #    p3.annotate(data3['id'], xy)
#            p3.set_xdata(data['x'])
#            p3.set_ydata(data['y'])
#            p4.set_xdata(data2['x'])
#            p4.set_ydata(data2['y'])
            #if data['z'] == 5:
            #    p1.set_color('blue')
            #p1.set_gid("Group")
            #fig.savefig('test.png')
            #fig.close()