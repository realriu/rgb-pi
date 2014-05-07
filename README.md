# RGB-pi
======
**Controlling RGB LED Stripes using a Raspberry Pi and a mobile Device**

This project was build on the work of Michael Vitousek and his project [pi-blaster](https://github.com/mvitousek/pi-blaster)
	
This project provides a server, written in in python. It can be connected by a simple TCP stream socket and controlled by command strings. (protocoll in development)
	
To control the whole thing there are mobile apps planned for various platforms:
  * Windows Phone
  * Android
  * HTML
  * ...

======

## hardware parts needed:
  * Raspberry Pi
  * 3 x TIP120 power transistors for each LED strip (in case you wanna controll them seperatly)
  * RGB LED strip
  * Perfboard/Breadboard or Dupont cables
  * 12V power supply (_Watt amount needed depends on the used LED-stripe and its lenght_)
	
**sources & helpful links:**
  * [michael at mitchtech.net - Assembly](http://mitchtech.net/raspberry-pi-pwm-rgb-led-strip)
  * [thomas at tbideas.com - PWM](http://www.tbideas.com/blog/2013/02/controling-a-high-power-rgb-led-with-a-raspberry-pi)
	
======

## rgb-pi server
### configure
first you have to set the pin numbers according to the pins you connected the rgb-channels of your LEDs. This have to be done in the **config.py** file:
			
Pins on the raspberry pi GPIO interface. See: (https://github.com/mvitousek/pi-blaster)
Which represents the RGB channels of your LEDs
```python
RED_PIN_1 = 2 
GREEN_PIN_1 = 5 
BLUE_PIN_1 = 6
```

This value indicates the minimum value of the sum of red, green and blue channels.  
If a Color is set with **R + G + B < MIN_VALUE**, rgb-pi will set black (off) as color to prevent the LEDs from blinking.
			
```python
MIN_VALUE = 0.00
```

this is the minimum value threads wait between their processing intervals
increase this value to get more cpu time for other programs
decrease this value, to get smoother fading
don't set this value lower or equal 0!!!
```python
DELAY = 0.01
```

TCP Port the server is listening on: 
```python
SERVER_PORT = 4321
```
### use
simply changing color:
```bash
python rgb.py c 1.0 0.2 0.4
```

configuration of the server:
```bash
python configure.py config
```

starting the server:
```bash
python rgb.py server
```

#### communication protocol
The server can receive commands from third party applications, like mobile apps. To send a commands to the server, a TCP stream socket has to be initialized and connected to the raspberry pi host ip. The command has to be a string with a maximum size of 1024 bytes.

By default the server listens to <strong>port 4321</strong>, but this can be configured in **config.py**.

A documentation to the communication protocol can be found here (https://github.com/realriu/rgb-pi/blob/master/doc/protocol.html)


## Contributors
realkyton (https://github.com/realkyton)  
realriu (https://github.com/realriu)

## License
```
The MIT License (MIT)

Copyright (c) 2013 Creative RyU

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
