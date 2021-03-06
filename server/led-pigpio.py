#python modules
import os
import time

#rgb-pi modules
import datatypes
import config
import log
import server
import utils
import mock

GPIOMapping_BCM = [4, 17, 18, 21, 22, 23, 24, 25]
PIGPIO = None

try:
    import pigpio
    PIGPIO = pigpio.pi() # connect to local Pi
    log.l("starting pigpio...", log.LEVEL_UI)
    time.sleep(1)
except ImportError:
    log.l("Error importing RPi.GPIO!  This is probably because you need superuser privileges.", log.LEVEL_ERRORS)
    log.l("Mocking RPi.GPIO ...", log.LEVEL_ERRORS)
    PIGPIO = mock.PiGPIO_Mock.pi()



#global rgb values
COLOR = [datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}'),
         datatypes.Color('{x:000000}')]


# elementary function to change the color of LED stripes
def changeColor(r, g, b, address=0xF):
    global COLOR
    global PIGPIO
    global GPIOMapping_BCM

    for i in range(0, len(config.LED_PINS)):
        if ((i+1) & address) != 0:
            COLOR[i].R = r
            COLOR[i].G = g
            COLOR[i].B = b

            # if lower than min value turn LEDs off
            r = 0.0 if r<=0.0 else utils.clip(r, config.MIN_VALUE)
            g = 0.0 if g<=0.0 else utils.clip(g, config.MIN_VALUE)
            b = 0.0 if b<=0.0 else utils.clip(b, config.MIN_VALUE)

            #pigpio works with values between 0-255
            PIGPIO.set_PWM_dutycycle(GPIOMapping_BCM[config.LED_PINS[i][0]], r*255)
            PIGPIO.set_PWM_dutycycle(GPIOMapping_BCM[config.LED_PINS[i][1]], g*255)
            PIGPIO.set_PWM_dutycycle(GPIOMapping_BCM[config.LED_PINS[i][2]], b*255)


def setPin(pin, value):
    global PIGPIO
    PIGPIO.set_PWM_dutycycle(GPIOMapping_BCM[pin], utils.clip(value)*255)

def setColor(color):
    for i in range(0, len(server.CurrentFilters)):
        color = server.CurrentFilters[i].onChangeColor(color)
    changeColor(color.R, color.G, color.B)