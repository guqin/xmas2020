# some code adapted from DanStach/rpi-ws2811
import time
import board
import neopixel
import requests
import blynklib
import random
import multiprocessing as mp
import numpy as np

BLYNK_AUTH = open('blynk_auth.txt').read().strip()

# initialize blynk
blynk = blynklib.Blynk(BLYNK_AUTH)



# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 100

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)




wait_time = .5
wait_animate = .1
cycleFactor = 1

cred = (255, 0, 0)
cblue = (0, 0, 255)
cgreen = (0, 255, 0)
cyellow = (255, 255, 0)
ccyan = (0, 255, 255)
cpurple = (160, 32, 240)
cpurple2 = (76,0,200)
cpurple3 = (100,0,200)
corange = (255, 165, 0)
cwhite = (255, 255, 255)
cblk = (0, 0, 0)


def brightnessRGB(red, green, blue, bright):
    r = (bright/256.0)*red
    g = (bright/256.0)*green
    b = (bright/256.0)*blue
    return (int(r), int(g), int(b))
        

def off():
    pixels.fill((0, 0, 0))
    pixels.show()

def red():
    pixels.fill((255, 0, 0))
    pixels.show()

def green():
    pixels.fill((0, 255, 0))
    pixels.show()

def blue():
    pixels.fill((0, 0, 255))
    pixels.show()
    
def magenta():
    pixels.fill((255, 0, 255))
    pixels.show()

def yellow():
    pixels.fill((255, 255, 0))
    pixels.show()

def cyan():
    pixels.fill((0, 255, 255))
    pixels.show()

def white():
    pixels.fill((255, 255, 255))
    pixels.show()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def colorAll5Color(c1, c2, c3, c4, c5):
    for i in range(num_pixels):
        j = i % 5
        if(j == 1): # 
            pixels[i] = c1
        if(j == 2): # 
            pixels[i] = c2
        if(j == 3): # 
            pixels[i] = c3
        if(j == 4): # 
            pixels[i] = c4
        if(j == 0): 
            pixels[i] = c5

def rainbow_cycle(wait=0.001):
    while True:
        for j in range(255):
            for i in range(num_pixels):
                pixel_index = (i * 256 // num_pixels) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)

def knight_rider(wait=0.02):
    kernel = [(255,0,0)]*7
    while True:
        for i in list(range(3,num_pixels-3))+list(reversed(range(3,num_pixels-4))):
            pixels.fill((0, 0, 0))
            a = max(i-len(kernel)//2,0)
            b = min(i+len(kernel)//2+1, num_pixels)
            pixels[a:b] = kernel
            pixels.show()
            time.sleep(wait)

def dazzle(wait=0.02):
    i = 0
    while True:
        if i==0:
            pixels.fill((255, 0, 0))
            pixels.show()
        elif i==1:
            pixels.fill((0, 255, 0))
            pixels.show()
        else:
            pixels.fill((0, 0, 255))
            pixels.show()
        i = (i+1)%3
        time.sleep(wait)

def sine(wait=0.04):
    a = (np.sin(np.linspace(0,2*np.pi, num_pixels))*127).astype(np.int)
    a = a.clip(0,255)
    i = 0
    while True:
        pixels[:] = np.tile(np.roll(a,i),(3,1)).T
        pixels.show()
        i = (i+1)%num_pixels
        time.sleep(wait)

def twinkle(wait=0.02):
    p = 0.001
    maxDelay = int(4/wait)
    disableCount = np.zeros(num_pixels).astype(np.int)
    a = np.zeros(num_pixels).astype(np.int)
    while True:
        temp = np.random.rand(num_pixels) < p
        disableCount[temp] = (np.random.rand(temp.sum())*maxDelay).astype(np.int)
        a[disableCount>0] = 0
        a[disableCount==0] = 255
        disableCount = np.maximum(disableCount-1,0)
        pixels[:] = np.tile(a,(3,1)).T
        pixels.show()
        time.sleep(wait)        

def random(wait=0.1):
    while True:
        pixels[:] = np.random.randint(0,256,(num_pixels,3))
        pixels.show()
        time.sleep(wait)



# HalloweenExisiting - mimics a heart beat pulse, with 2 beats at different speeds. The existing colors 
# on the pixel strip are preserved, rather than a single color.
#
# HalloweenExisiting(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay,
#                     beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat1Delay, cycles):
# HalloweenExisiting(3, .005, .003, 0.001, 6, .002, .003, 0.05, 10)
#
#   beat1Step: (1-255) first beat color transition step
#   beat1FadeInDelay: (0-2147483647) first beat fade in trasition speed, in seconds
#   beat1FadeOutDelay: (0-2147483647) first beat fade out trasition speed, in seconds
#   beat1Delay: (0-2147483647)  beat time delay bewteen frist and sencond beat, in seconds
#   beat2Step: (1-255) second beat color transition step
#   beat2FadeInDelay: (0-2147483647) second beat fade in trasition speed, in seconds
#   beat2FadeOutDelay: (0-2147483647) second beat fade out trasition speed, in seconds
#   beat1Delay: (0-2147483647)  beat time delay bewteen sencond and first beat, in seconds
#   cycles: (1-2147483647) number of times this effect will run
def HalloweenExisiting(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay, beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat2Delay, cycles):
#HalloweenExisiting(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay, 
#                   beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat2Delay, cycles):
    # gather existing colors in strip of pixel
    stripExisting = []
    maxbright = 256
    minbright = 15 
    for i in range(num_pixels):
        stripExisting.append(pixels[i])

    for loop in range(cycles):               

        for ii in range(minbright, maxbright, beat1Step): #for ( ii = 1 ; ii <252 ; ii = ii = ii + x)
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat1FadeInDelay)

        for ii in range(maxbright, minbright, -beat1Step): #for (int ii = 252 ; ii > 3 ; ii = ii - x){
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat1FadeOutDelay)
            
        time.sleep(beat1Delay)
        
        for ii in range(minbright, maxbright, beat1Step): #for (int ii = 1 ; ii <255 ; ii = ii = ii + y){
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat2FadeInDelay)

        for ii in range(maxbright, minbright, -beat1Step): #for (int ii = 255 ; ii > 1 ; ii = ii - y){
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat2FadeOutDelay)
    


# HeartBeatExisiting - mimics a heart beat pulse, with 2 beats at different speeds. The existing colors 
# on the pixel strip are preserved, rather than a single color.
#
# HeartBeatExisiting(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay,
#                     beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat1Delay, cycles):
# HeartBeatExisiting(3, .005, .003, 0.001, 6, .002, .003, 0.05, 10)
#
#   beat1Step: (1-255) first beat color transition step
#   beat1FadeInDelay: (0-2147483647) first beat fade in trasition speed, in seconds
#   beat1FadeOutDelay: (0-2147483647) first beat fade out trasition speed, in seconds
#   beat1Delay: (0-2147483647)  beat time delay bewteen frist and sencond beat, in seconds
#   beat2Step: (1-255) second beat color transition step
#   beat2FadeInDelay: (0-2147483647) second beat fade in trasition speed, in seconds
#   beat2FadeOutDelay: (0-2147483647) second beat fade out trasition speed, in seconds
#   beat1Delay: (0-2147483647)  beat time delay bewteen sencond and first beat, in seconds
#   cycles: (1-2147483647) number of times this effect will run
def HeartBeatExisiting(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay, beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat2Delay, cycles):
#HeartBeatExisiting(beat1Step, beat1FadeInDelay, beat1FadeOutDelay, beat1Delay, 
#                   beat2Step, beat2FadeInDelay, beat2FadeOutDelay, beat2Delay, cycles):
    # gather existing colors in strip of pixel
    stripExisting = []
    maxbright = 220
    minbright = 10
    for i in range(num_pixels):
        stripExisting.append(pixels[i])

    for loop in range(cycles):               

        for ii in range(minbright, maxbright, beat1Step): #for ( ii = 1 ; ii <252 ; ii = ii = ii + x)
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat1FadeInDelay)

        for ii in range(maxbright, minbright, -beat1Step): #for (int ii = 252 ; ii > 3 ; ii = ii - x){
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat1FadeOutDelay)
            
        time.sleep(beat1Delay)
        
        for ii in range(minbright, maxbright, beat1Step): #for (int ii = 1 ; ii <255 ; ii = ii = ii + y){
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat2FadeInDelay)

        for ii in range(maxbright, minbright, -beat1Step): #for (int ii = 255 ; ii > 1 ; ii = ii - y){
            for index in range(num_pixels):
                r = stripExisting[index][0]
                g = stripExisting[index][1]
                b = stripExisting[index][2]
                pixels[index] = brightnessRGB(r,g,b, ii) 
                #pixels.fill( brightnessRGB(redo, greeno, blueo, ii) ) #strip.setBrightness(ii)
            pixels.show()
            time.sleep(beat2FadeOutDelay)
    


def CandleOrange(Count, FlickerDelay ):
    pixels.fill(corange) # start with orange
    for i in range(Count):
        flicknum = np.random.randint(0,num_pixels-1)
        for k in range(flicknum):
            index = np.random.randint(0,num_pixels-1)
            blueval = np.random.randint(0,75)
            pixels[index] = (255,128 + int(blueval/2),blueval)
        pixels.show()
        time.sleep(FlickerDelay)


def SnowSparkleExisting(Count, SparkleDelay, SpeedDelay):
    # gather existing colors in strip of pixel
    stripExisting = []
    for i in range(num_pixels):
        stripExisting.append(pixels[i])

    for i in range(Count):
        blinknum = np.random.randint(1,3)
        for k in range(blinknum):
            index = np.random.randint(0,num_pixels-1)
            pixels[index] = (255,255,255)
        pixels.show()
        time.sleep(SparkleDelay)
        for h in range(num_pixels):
            pixels[h] = stripExisting[h]
        pixels.show()
        speedvar = np.random.randint(1,3)
        time.sleep(SpeedDelay*speedvar)


def glow(wait=0.02):
    #a = (np.sin(np.linspace(0,2*np.pi, num_pixels))*127).astype(np.int)
    #a = a.clip(0,255)
    a = np.sin(np.linspace(0,2*np.pi*4, 463))+1
    i = 0
    j = 0
    while True:
        #pixels[:] = np.full((num_pixels,3), a[i])
        pixels[:] = np.clip((np.array([wheel(j)]*num_pixels)*a[i]).astype(np.int),0,255)
        pixels.show()
        i = (i+1)%463
        j = (j+1)%256
        time.sleep(wait)

def love_kisses():
	a = 0.75
	b = 0.25
	eight = "---.."
	while True:
		for j in range(2):
			for i in range(len(eight)):
				if i <= 2:
					pixels.fill((255, 0, 255))
					pixels.show()
					time.sleep(a)
					pixels.fill((0, 0, 0))
					pixels.show()
					time.sleep(b)
				if i > 2:
					pixels.fill((255, 0, 255))
					pixels.show()
					time.sleep(b)
					pixels.fill((0, 0, 0))
					pixels.show()
					time.sleep(b)
		time.sleep(5)


def sparkle():
    print("enter spark")
    colorAll5Color((255,0,0), cpurple ,(0,255,0), (0,0,255), (255,128,0  ))
    pixels.show()
    print("enter spark show")
    while True:
        SnowSparkleExisting(1000*cycleFactor, .1, .4)

def heart():
    while True:
      pixels.fill(cred) 
      HeartBeatExisiting(16, .001, .001, 0.001,16, .001, .001, 0.001, 10)

def candle():
      CandleOrange(1000*cycleFactor, .1)

 
#def stpatrick():

def halloween():
    while True:
      pixels.fill(cpurple2) 
      HalloweenExisiting(1, .002, .002, 0.002,1, .002, .002, 0.002, 10)

# register handler for virtual pin V11 reading
@blynk.handle_event('read V0')
def read_virtual_pin_handler(pin):
    READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"
    print(READ_PRINT_MSG.format(pin))
    #blynk.virtual_write(pin, random.randint(0, 255))


currentFunc = off
currentThread = mp.Process(target=currentFunc)
currentThread.start()

@blynk.handle_event('write V2')
def write_virtual_pin_handler(pin, value):
    print("Received write to V2: {}".format(value))

# register handler for virtual pin V4 write event
@blynk.handle_event('write V0')
def write_virtual_pin_handler(pin, value):
    global currentFunc
    global currentThread
    WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_PIN_EVENT] Pin: V{} Value: '{}'"
    print(WRITE_EVENT_PRINT_MSG.format(pin, value))
    #print(value, type(value))
    #print(pixels)
    val = int(value[0])
    
    funcDict = {
        0: off,
        1: red,
        2: green,
        3: blue,
        4: magenta,
        5: yellow,
        6: cyan,
        7: white,
        8: rainbow_cycle,
        9: knight_rider,
        10: dazzle,
        11: sine,
        12: twinkle,
        13: random,
        14: glow,
        15: love_kisses,
        16: sparkle,
        17: candle,
        18: heart,
        19: halloween,
        20: stpatrick
    }
    currentFunc = funcDict.get(val, off)
    print(currentFunc.__name__)
    blynk.virtual_write(1, currentFunc.__name__)
    currentThread.terminate()
    currentThread = mp.Process(target=currentFunc)
    currentThread.start()

###########################################################
# infinite loop that waits for event
###########################################################
while True:
    time.sleep(10)
    heart()
    blynk.run()
