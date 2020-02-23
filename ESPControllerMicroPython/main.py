

from MicroWebSrv2 import *
import json
from time import sleep
import os
import machine, neopixel
import gc
import time
WS_CHAT_SUB_PROTOCOL = 'myGreatChat-v1'

gc.enable()

#configs = ['a', 'badfasdfa', 'c', 'd', 'e']

#colors = {'a':[0x123456, 0x234567, 0x345678]}

NUM_LED = 250
np = neopixel.NeoPixel(machine.Pin(3), NUM_LED)

BRIGHT = 1.0

position = 0
steps = 50
seqLen = 0

oldPixelCopy = [0 for i in range(250)]


try:

    def OnTextMessage(webSocket, msg):
        print(gc.mem_free())
        global BRIGHT
        name = msg
        if name == 'new':
            c = {'command': 'data', 'config-name': 'new', 'data': []}
            j = json.dumps(c)
            webSocket.SendTextMessage(j)
        elif name == 'configs':
            files = os.listdir()
            configs = []
            for f in files:
                if '.txt' in f:
                    configs.append(f.split('.txt')[0])
            c = {'command': 'config', 'config':configs}
            j = json.dumps(c)
            webSocket.SendTextMessage(j)
        elif 'detail' in name:
            configName = name.split(':')[1]
            mostRecent = configName
            colors = []
            f = open('%s.txt' % configName, 'r')
            for line in f:
                colors.append("{0:0{1}x}".format(int(line),6))
                #colors.append(hex(int(line))[2:])
            c = {'command': 'data', 'config-name':configName, 'data':colors}
            j = json.dumps(c)
            webSocket.SendTextMessage(j)
            f.close()
        elif 'bright' in name:
            print(name)
            val = name.split(':')[1]
            scaler = float(float(val)/255.0)
            print(scaler)
            BRIGHT = scaler
            print(BRIGHT)
            f = open('bright', 'w')
            f.write(val)
            f.close()
            f = open('last', 'r')
            colors = []
            for line in f:
                colors.append(int(line))
            f.close()
            dat = colors
            mod = len(dat)
            for i in range(NUM_LED):
                r = int(float((dat[i % mod] >> 16))*BRIGHT)
                g = int(float((dat[i % mod] >> 8) & 0xff)*BRIGHT)
                b = int(float((dat[i % mod]) & 0xff)*BRIGHT)
                np[i] = (g, r, b)
            np.write()
        else:
            data = name.split(',')
            name = data[1]
            mostRecent = name

            dat = []
            for color in data[2:]:
                print(color)
                dat.append(int(color[1:], 16))
            f = open('%s.txt' % name, 'w')
            g = open('last', 'w')
            for d in dat:
                f.write("%d\n" % d)
                g.write("%d\n" % d)
            f.close()
            g.close()

            mod = len(dat)
            for i in range(NUM_LED):
                r = int(float((dat[i % mod] >> 16)) *BRIGHT)
                g = int(float((dat[i % mod] >> 8) & 0xff) * BRIGHT)
                b = int(float((dat[i % mod]) & 0xff) * BRIGHT)
                np[i] =(g,r,b)
            np.write()
        print(gc.mem_free())
        webSocket.Close()
        #gc.collect()
        print(gc.mem_free())

    def OnBinaryMessage(webSocket, msg):
        print("received")
        print(msg)

    def OnWebSocketProtocol(microWebSrv2, protocols) :
        if WS_CHAT_SUB_PROTOCOL in protocols :
            return WS_CHAT_SUB_PROTOCOL

    def OnWebSocketAccepted(microWebSrv2, webSocket) :
        print('New WebSocket (myGreatChat proto) accepted from %s:%s.' % webSocket.Request.UserAddress)
        webSocket.OnTextMessage = OnTextMessage
        webSocket.OnBinaryMessage = OnBinaryMessage

    def runLast():
        print(gc.mem_free())
        global seqLen
        try:
            try:
                f = open('bright', 'r')
                bb = 0
                for line in f:
                    bb = float(line)
                BRIGHT = float(bb/255.0)
                f.close()
            except:
                print('fail')
            colors = []
            f = open('%s' % 'last', 'r')
            for line in f:
                colors.append(int(line))
            dat = colors
            mod = len(dat)
            seqLen = len(dat)
            for i in range(NUM_LED):
                r = int(float((dat[i % mod] >> 16)) * BRIGHT)
                g = int(float((dat[i % mod] >> 8) & 0xff) * BRIGHT)
                b = int(float((dat[i % mod]) & 0xff) * BRIGHT)
                np[i] = (g, r, b)
            np.write()
            f.close()
        except:
            print("fail")
            pass
        #gc.collect()
        print(gc.mem_free())

    runLast()




    def SetBarebonesConfig(mws_s):
        mws_s._backlog = 2
        mws_s._slotsCount = 2
        mws_s._slotsSize = 1024
        mws_s._keepAlloc = True
        mws_s._maxContentLen = 2 * 1024

    print(gc.mem_free())
    gc.collect()

    wsMod = MicroWebSrv2.LoadModule('WebSockets')
    wsMod.OnWebSocketProtocol = OnWebSocketProtocol
    wsMod.OnWebSocketAccepted = OnWebSocketAccepted


    mws2 = MicroWebSrv2()
    print(gc.mem_free())

    mws2.BindAddress = ('192.168.1.235', 12345)


    SetBarebonesConfig(mws2)

    mws2.BufferSlotsCount = 2

    # All pages not found will be redirected to the home '/',
    mws2.NotFoundURL = '/'

    # Starts the server as easily as possible in managed mode,
    mws2.StartManaged()

    print(gc.mem_free())
    # Main program loop until keyboard interrupt,

    #GRB
    try :
        while mws2.IsRunning:
            posOff = 0
            for i in range(NUM_LED):
                oldPixelCopy[i] = np[i]
            while(posOff < seqLen):
                #s = np[0]
                #for i in range(NUM_LED-1):
                #    oldPixelCopy[i] = np[i+1]
                #oldPixelCopy[249] = s

                for s in range(steps):
                    for i in range(NUM_LED):
                        deltaG = float(oldPixelCopy[(i-1+posOff)%NUM_LED][0] - oldPixelCopy[(i+posOff)%NUM_LED][0])/steps
                        deltaR = float(oldPixelCopy[(i-1+posOff)%NUM_LED][1] - oldPixelCopy[(i+posOff)%NUM_LED][1])/steps
                        deltaB = float(oldPixelCopy[(i-1+posOff)%NUM_LED][2] - oldPixelCopy[(i+posOff)%NUM_LED][2])/steps

                        newG = oldPixelCopy[(i-1+posOff)%NUM_LED][0] - int(deltaG * s)
                        newR = oldPixelCopy[(i-1+posOff)%NUM_LED][1] - int(deltaR * s)
                        newB = oldPixelCopy[(i-1+posOff)%NUM_LED][2] - int(deltaB * s)

                        np[i] = (newG,newR,newB)
                        if i == 1:
                            print(i, s, deltaG, deltaR, deltaB, np[i], oldPixelCopy[(i+posOff)%NUM_LED], oldPixelCopy[(i-1+posOff)%NUM_LED])
                    np.write()
                    gc.collect()
                    time.sleep_ms(5)
                sleep(1)
                posOff+=1
                print(seqLen, posOff)
            runLast()

    except Exception as e:
        print(e)
        pass

    # End,
    print()
    mws2.Stop()
    print('Bye')
    print()
except:
    machine.reset()

