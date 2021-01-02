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
num_pixels = 50

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)


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
        14: glow
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
    blynk.run()
