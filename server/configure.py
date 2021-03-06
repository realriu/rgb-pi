#!/usr/bin/env python

# this file will be used by the config.sh script to easily set-up the server
# and the configuration of the RGB-channels of your LED stripes.
# It's also able to install pigpio and configure communication with xbmc.

#python modules
import string
import os
import time
import re
import sys

#install_service.py modules
import log
import install_service


#config parameters
CONFIG = {
    'LED_PINS' : '[[5, 2, 6]]',

    'MIN_VALUE': '0.08',

    'DELAY': '0.01',

    'SERVER_PORT': '4321',

    'CONNECTION_TIMEOUT': '1.0',

    'ENABLE_XBMC_REMOTE': '0',
    'XBMC_HOST': '\"127.0.0.1\"',
    'XBMC_PORT': '80'
}

GPIOMapping_BCM = [4, 17, 18, 21, 22, 23, 24, 25]

#contains a string with the contents of the config file
configData = ''

##### MESSAGE BOXES START #####

#clears console
def cls():
    pass#os.system(['clear', 'cls'][os.name == 'nt'])


def messageBoxAnyKey():
    raw_input("\npress any key to continue...")

#shows a message box with question and the choices 'y' for yes and 'n' for no
#returns 1 if yes was chosen and 0 if no, otherwise it loops til one of them was chosen
def messageBoxYesNo(question):
    while 1:
        answer = string.lower(raw_input(question + ' (y | n): '))
        if answer == 'y': return 1
        if answer == 'n': return 0

#shows a message box with question and the choices 'r' for RED, 'g' for GREEN, 'b' for BLUE or 'n' for NONE
#returns 'r', 'g' or 'b' corresponding to the pressed key.
#cycles questioning 'til the user answers with one of the 4 choises
def messageBoxRGB():
    while 1:
        answer = string.lower(raw_input('What color do you see?' + ' (r=RED | g=GREEN | b=BLUE | n=NONE): '))
        if answer == 'r': return 'r'
        if answer == 'g': return 'g'
        if answer == 'b': return 'b'
        if answer == 'n': return 'n'

#shows a message box with a question for an integer number
#returns the typed number
def messageBoxINT(question, min=-2147483648, max=2147483647):
    while 1:
        try:
            answer = int(raw_input(question + ': '))
            if answer < min or answer > max:
                raise ValueError
            else:
                return answer
        except ValueError:
            print 'please input an integer value between ' + str(min) + ' and ' + str(max)

#shows a message box with a question for an float number
#returns the typed number
def messageBoxFLOAT(question, min=0.0, max=1.0):
    while 1:
        try:
            answer = float(raw_input(question + ': '))
            if answer < min or answer > max:
                raise ValueError
            else:
                return answer
        except ValueError:
            print 'please input a float value between ' + str(min) + ' and ' + str(max)

#shows a message box with a question for a string with a min and max lenght and an optional pattern
#returns the typed string
def messageBoxSTRING(question, pattern = None, patternDescription = None, min=0, max=2147483647):
    while 1:
        try:
            answer = raw_input(question + ': ')
            if len(answer) < min or len(answer) > max:
                raise ValueError
            elif pattern is not None:
                regX = re.compile(pattern)
                if not regX.match(answer):
                    raise SyntaxWarning
                else:
                    return answer
            else:
                return answer
        except ValueError:
            print 'please input a string with a length between ' + str(min) + ' and ' + str(max)+" characters"
        except SyntaxWarning:
            if patternDescription is None:
                print "please input a string, that matches the given regex pattern: \'"+pattern+"\'"
            else:
                print "please input a string, that matches the pattern of: "+patternDescription


#shows a message box with a question and multiple choises to answer (in the format key: description)
#returns the entered key
def messageBoxChoose(question, **answers):
    choises = ''
    for key in sorted(answers):
        choises += '\n' + key + ': ' + answers[key]

    while 1:
        cls()
        answer = string.lower(raw_input(question + '\n' + choises + '\n: '))
        for key in answers:
            if (answer == string.lower(key)):
                return answer

##### MESSAGE BOXES END #####


##### READ/WRITE CONFIG START #####

#reads the config file (if not existent, it's created with the data of the 'defaultconfig'-file)
#checks if config data is complete and contains only valid data. if not it tries to autocorrect the data
def readConfig():
    if not os.path.exists('./config.py'):
        dcFile = open('defaultconfig', 'r+')
        cFile = open('config.py', 'w+')
        cFile.write(dcFile.read())
        cFile.close()
        dcFile.close()

    cFile = open('config.py', 'r+')
    global configData
    configData = cFile.read()
    neededCorrection = 0
    global CONFIG
    for k in CONFIG:
        index = configData.find(k)
        if index == -1:
            configData += '\n' + k + ' = ' + CONFIG[k]
            neededCorrection = 1
            index = configData.find(k)

        #this extracts a relevant config line with the format: 'key = value'
        line = configData[index:configData.find('\n', index)]
        regex = re.compile(r"\s*[a-zA-Z]\w*\s*=\s*\S+\s*")
        found = regex.search(line)

        if found is None: #not a valid config entry
            print "ERROR in line: " + line + " ... corrected"
            configData = configData.replace(line, k + ' = ' + CONFIG[k])
            line = k + ' = ' + CONFIG[k]
            neededCorrection = 1

        # set value of the key into the config array
        CONFIG[k] = line.split("=", 1)[1].strip()

    cFile.close()
    if neededCorrection:
        writeConfig()

def writeConfig():
    global configData
    if not (configData is None) and len(configData) > 0:
        cFile = open('config.py', 'w+')
        for k in CONFIG:
            index = configData.find(k)
            line = configData[index:configData.find('\n', index)]
            configData = configData.replace(line, k + ' = ' + CONFIG[k])

        cFile.write(configData)
        cFile.close()
    else:
        raise IOError('configData variable is empty!')

def printConfig():
    readConfig()
    print "RGB-Pi configuration:\n"
    global CONFIG
    for k in CONFIG:
        print str(k)+((3-len(str(k))/8)*'\t')+"=\t"+str(CONFIG[k])

##### READ/WRITE CONFIG END #####

##### LED CONFIG START #####
def ledConfig():
    cls()
    readConfig()
    global CONFIG
    global GPIOMapping_BCM
    stripes = messageBoxINT(
        'How many LED-stripes do you have?\n(If two stripes are connected to the same channels, they count as one)', 0, 8)

    stripeConfig = []
    abort = 0

    #filling array with disabled ports
    for i in range(0, stripes):
        stripeConfig.append([-1, -1, -1])

    for i in range(0, 8):
        #set one of the pins to '1', and let the user say which stripe/color it represents
        for p in range(0, 8):
            if i==p:
                os.system("echo \"w "+str(GPIOMapping_BCM[p])+" 1\" > /dev/pigpio")
                #led.setPin(led.GPIOMapping_BCM[p], 1.0)
            else:
                os.system("echo \"w "+str(GPIOMapping_BCM[p])+" 0\" > /dev/pigpio")
                #led.setPin(led.GPIOMapping_BCM[p], 0.0)

        cls()
        rgb = messageBoxRGB()
        stripe = 0

        if rgb != 'n':
            if stripes > 1:
                stripe = messageBoxINT('Which LED-stripe shows the color? (0 = None of them)', 0, stripes+1)
            else:
                stripe = 1

        if stripe != 0:
            if rgb == 'r': stripeConfig[stripe-1][0] = i
            if rgb == 'g': stripeConfig[stripe-1][1] = i
            if rgb == 'b': stripeConfig[stripe-1][2] = i

    if not abort:
        #configuration finished, now showing the configured values an let the user confirm it.
        ledC = ""
        for i in range(0, stripes):
            ledC += "Stripe "+str(i+1)+": "
            if stripeConfig[i][0] >= 0: ledC+="red = "+str(stripeConfig[i][0])+" "
            if stripeConfig[i][1] >= 0: ledC+="green = "+str(stripeConfig[i][1])+" "
            if stripeConfig[i][2] >= 0: ledC+="blue = "+str(stripeConfig[i][2])+" "
            ledC+="\n\n"

        cls()
        ans = messageBoxYesNo("This is your new LED-Configuration:\n\n"+ledC+"\nDo you want to save this configuration?")

        #write to config
        if ans:
            CONFIG['LED_PINS'] = str(stripeConfig)
            writeConfig()
            print "\n\n...configuration saved"
            messageBoxAnyKey()
        else:
            choises = {'1': 'start over', 'x': 'back to main menu'}
            a = messageBoxChoose('Choose the next operation', **choises)
            if a == '1':
                ledConfig()
    else:
        print "\n\npigpio seems not to be running.\nYou need it to light up LEDs, that are connected to the GPIO interface.\nPlease install it via main menu, "
        messageBoxAnyKey()

##### LED CONFIG END #####

##### SERVER CONFIG START #####
def serverConfig():
    readConfig()
    global CONFIG
    exit = 0

    while not exit:

        preQ = "Current properties:\n"

        choises = {'x': 'exit'}
        i = 0
        for k in CONFIG:
            if k == 'SERVER_PORT' or k == 'MIN_VALUE' or k == 'DELAY' or k == 'CONNECTION_TIMEOUT':
                choises[str(i+1)] = k
                i = i+1
                preQ += k+" = "+CONFIG[k]+"\n"
        answer = messageBoxChoose(preQ+'\nWhat property do you want to change?', **choises)
        if answer == 'x':
            exit = 1
        else:
            v = None
            if choises[answer] == 'SERVER_PORT': v = messageBoxINT('Please enter the port, the server should be bound to', 1, 65535)
            if choises[answer] == 'CONNECTION_TIMEOUT': v = messageBoxFLOAT('Enter the timeout in seconds for the network communication (0.0 activates the non-blocking mode). (default value: 1.0)', 0.0, 1.7976931348623157e+308)
            if choises[answer] == 'DELAY': v = messageBoxFLOAT('Enter the delay between fade-color-change-iterations (good value: 0.01)', 0.0001, 1)
            if choises[answer] == 'MIN_VALUE': v = messageBoxFLOAT("Enter the minimum value the RGB Pins can be set to before the LEDs start \"blinking\"", 0.0, 0.999)
            CONFIG[choises[answer]] = str(v)
            writeConfig()

    messageBoxAnyKey()

def xbmcConfig():
    readConfig()
    global CONFIG
    exit = 0

    while not exit:

        preQ = "Current XBMC settings:\n"

        choises = {'x': 'exit'}
        i = 0
        for k in CONFIG:
            if k == 'ENABLE_XBMC_REMOTE' or k == 'XBMC_HOST' or k == 'XBMC_PORT':
                choises[str(i+1)] = k
                i = i+1
                preQ += k+" = "+CONFIG[k]+"\n"
        answer = messageBoxChoose(preQ+'\nWhat property do you want to change?', **choises)
        if answer == 'x':
            exit = 1
        else:
            v = None
            if choises[answer] == 'ENABLE_XBMC_REMOTE': v = messageBoxYesNo('Enable XBMC remote control?')
            if choises[answer] == 'XBMC_HOST': v = "\""+messageBoxSTRING('Enter the host/IP of the XBMC remote server (\'localhost\' in case it\'s locally on this Pi)', r'^(\d(1,3)\.\d(1,3)\.\d(1,3)\.\d(1,3))|(\w+(\w*|\.)*)$', "an IP-address, computer name or domain")+"\""
            if choises[answer] == 'XBMC_PORT': v = messageBoxINT("Enter the XBMC remote port (usually \'80\' or \'8080\')", 1, 65535)
            CONFIG[choises[answer]] = str(v)
            writeConfig()

    messageBoxAnyKey()

##### SERVER CONFIG END #####


##### MENU START #####
def showMenu():
    choises = {'1': 'install/uninstall pigpio (necessary to control LEDs)',
               '2': 'configure LED-channels',
               '3': 'configure server',
               '4': 'configure xbmc remote control',
               '5': 'enable/disable autostart (root)',
               'x': 'exit'
    }

    return messageBoxChoose(
        'Welcome to the RGB-Pi configuration!\nChoose the configuration steps you want to proceed with:', **choises)




def createConfig():
    exit = 0
    while not exit:
        menuitem = showMenu()

        if menuitem == '1':
            choises = {'1': 'install pigpio',
                       '2': 'uninstall pigpio'}
            a = messageBoxChoose('choose the next operation', **choises)

            if '1' == a:
                print 'installing pigpio'
                time.sleep(1)
                os.system("mkdir ../temp")
                os.system("wget abyz.co.uk/rpi/pigpio/pigpio.zip -O ../temp/pigpio.zip")
                os.system("unzip ../temp/pigpio.zip -d ../temp")
                os.system("make -C ../temp/PIGPIO/")
                os.system("cp -avr ../temp/PIGPIO/ ../PIGPIO/")
                os.system("sudo rm -R ../temp")
                os.system("sudo make -C ../PIGPIO/ install")
            elif a == '2':
                print 'uninstalling pigpio'
                time.sleep(1)
                os.system("sudo make -C ../PIGPIO/ uninstall")
                os.system("sudo rm -R ../PIGPIO")

            messageBoxAnyKey()

        if menuitem == '2':
            ledConfig()

        if menuitem == '3':
            serverConfig()

        if menuitem == '4':
            xbmcConfig()
        
        if menuitem == '5':
            choises = {'1': 'enable autostart',
                       '2': 'disable autostart'}
            a = messageBoxChoose('choose the next operation', **choises)

            if '1' == a:
                print 'installing start script in /etc/init.d/rgb-pi'
                time.sleep(1)
                install_service.writeInitD(os.getcwd(), os.path.dirname(os.getcwd())+"/PIGPIO/pigpiod")
                os.system("sudo chmod +x /etc/init.d/rgb-pi")
                os.system("sudo update-rc.d rgb-pi defaults")
                print '\n...done'

            elif a == '2':
                print 'uninstalling start script'
                time.sleep(1)
                os.system("sudo rm /etc/init.d/rgb-pi")
                print 'done'

            messageBoxAnyKey()

        if menuitem == 'x':
            exit = 1

##### MENU END #####

# start
if len(sys.argv) > 1:
    if sys.argv[1] == "config": createConfig()