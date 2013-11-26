#python modules
import time
import os
import sys
import string
import math

#rgb-pi modules
import utils
import config




# elementary function to change the color of the LED strip
def changeColor(r, g, b):
    global RED
    global GREEN
    global BLUE
    RED = r
    GREEN = g
    BLUE = b

    cmdR = "echo " + str(config.RED_PIN_1) + "=" + str(g) + " > /dev/pi-blaster"
    cmdG = "echo " + str(config.GREEN_PIN_1) + "=" + str(r) + " > /dev/pi-blaster"
    cmdB = "echo " + str(config.BLUE_PIN_1) + "=" + str(b) + " > /dev/pi-blaster"
    os.system(cmdR + " & " + cmdG + " & " + cmdB)

def setColor(color):
    changeColor()


#color string format {x|b|f:string}
#example1 hex-string:	{x:FF00A1}
#example2 byte:			{b:255,0,161}
#example3 float:		{f:1,0,0.63}
class Color():
    def __init__(self, colorString):
        colorString = string.strip(colorString)
        self.colorString = colorString
        self.R = 0.0
        self.G = 0.0
        self.B = 0.0

        if colorString[0] != '{' or colorString[len(colorString)-1] != '}':
            raise ValueError('color must defined within {} brackets')

        colorString = colorString[1:len(colorString)-1]
        colorParts = string.split(colorString, ':')

        if not (colorParts[0] in ['x', 'b', 'f']):
            raise ValueError('unknown color type: '+colorParts[0])

        if colorParts[0] == 'x':
            rgbcomps = utils.getIntComponents(colorParts[1])
            self.R = rgbcomps[0] / 255.0
            self.G = rgbcomps[1] / 255.0
            self.B = rgbcomps[2] / 255.0

        if colorParts[0] == 'b':
            rgbcomps = string.split(colorParts[1], ',')
            self.R = int(rgbcomps[0])
            self.G = int(rgbcomps[1])
            self.B = int(rgbcomps[2])

        if colorParts[0] == 'f':
            rgbcomps = string.split(colorParts[1], ',')
            self.R = float(rgbcomps[0])
            self.G = float(rgbcomps[1])
            self.B = float(rgbcomps[2])


    def redByte(self):
        return int(self.R * 255)
    def greenByte(self):
        return int(self.G * 255)
    def blueByte(self):
        return int(self.B * 255)

    def getHexString(self):
        return utils.getColorString([self.redByte(), self.greenByte(), self.blueByte()])


# clips the value between 0 and 1 
def clip(value):
    if value < 0.0:
        return 0.0
    elif value > 1.0:
        return 1.0
    else:
        return value


#global rgb values
COLOR = Color('{x:000000}')