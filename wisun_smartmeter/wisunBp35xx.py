#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# sudo pip3 install adafruit-circuitpython-ssd1306
# sudo apt-get install fonts-ipafont
# sudo pip3 install Pillow
# sudo apt-get install libopenjp2-7-dev
# sudo apt install libtiff5
# pip3 install paho-mqtt
# pip3 

from threading import Event, Thread
import time
import datetime
import binascii
import serial
import queue
import traceback
import logging

# ログ出力
logging.basicConfig(format='<%(levelname)s>%(message)s', level=logging.INFO)

# Wi-Sun BP35A1,BP35C0 driver
class wisunBp35xx:
    def __init__(self, deviceName, serialDev):
        logging.debug('__init_(device=%s,serial,%s) start',deviceName,serialDev)
        self._connected = False
        self._device = deviceName
        # self._serial = serial.Serial(serialDev, 115200)
        self._serial = serial.Serial(serialDev, 115200, timeout=3)
        self._recvQueue = queue.Queue()
        self._id = ""
        self._passwd = ""
        self._runThread = False
        self._waitCmd = False
        self._respCmd = ""
        self._waitEvent = False
        self._recvEvent = ""
        self._foundDevice = False
        self.channel = ""
        self.panid = ""
        self.addr = ""
        self.addrV6 = ""

    def connect(self,id,passwd):
        logging.debug('wwisunBp35xx.connect()')
        self._foundDevice = False
        self._connected = False
        self.channel = ""
        self.panid = ""
        self.addr = ""
        self.addrV6 = ""
        if not self._runThread:
            self._rcvThread = Thread(target=self._recvTask)
            self._rcvThread.start()
            #self._runThread = True

        while not self._runThread:
            time.sleep(0.5)

        logging.info('init bp35c0x')
        cmdOK,cmdResp = self._sendCmd("SKVER\r\n")
        if not cmdOK:
            logging.error('No response from bp35c0x')
            self._connected = False
            return self._connected
        respSpl = cmdResp.strip().split(' ')
        logging.info('%s version %s',self._device,respSpl[1])

        # self._sendCmd("WOPT 1\r\n") # 購入後1回だけ実行

        self._sendCmd("SKSETPWD C " + passwd + "\r\n")
        self._sendCmd("SKSETRBID " + id + "\r\n")

        logging.info('finding echonet device')
        retryConnect = 3
        foundTarget = False
        while retryConnect > 0:
            # Active Scan
            if self._device == "BP35C0":
                self._sendCmd("SKSCAN 2 FFFFFFFF 6 0\r\n")
            else:
                self._sendCmd("SKSCAN 2 FFFFFFFF 6\r\n")
            eventStat = self.waitEvent("22",timeout=60) # Active Scan終了待ち
            if not self._foundDevice:
                #　デバイスが見つからなかったら再試行
                retryConnect = retryConnect -1
                if retryConnect <=0:
                    logging.error('echonet device not found')
                    print("<error> Device not found")
                    self._connected = False
                    return self._connected
                logging.info('echonet device not found -- Retry')
            else:
                # デバイスが見つかったらスキャン終了
                logging.info('echonet device found')
                retryConnect = 0

        cmdOK,addrV6 = self._sendCmd("SKLL64 " + self.addr + " \r\n")
        if not cmdOK:
            logging.error('wisunBp35xx.connect() error02')
            self._connected = False
            return self._connected
        self.addrV6 = addrV6

        logging.info('connecting echonet device')
        cmdOK,cmdResp = self._sendCmd("SKSREG S2 " + self.channel + " \r\n")
        cmdOK,cmdResp = self._sendCmd("SKSREG S3 " + self.panid + " \r\n")

        cmdOK,cmdResp = self._sendCmd("SKJOIN " + self.addrV6 + " \r\n")
        eventStat = self.waitEvent("25",timeout=60) # PANA connect を待つ
        if eventStat == "":
            logging.error('wisunBp35xx.connect() error03')
            self._connected = False
            return self._connected

        logging.info('echonet device connected')
        self._connected = True
        return self._connected

    def disconnect(self):
        logging.debug('wisunBp35xx.disconnect()')
        if self._runThread:
            self._runThread = False
            self._rcvThread.join()
        self._serial.close()
        self._connected = False
        return True

    def isConnected(self):
        # print("@@@@@ wisunBp35xx.isConnected() {0}".format(self._connected))
        return self._connected

    def waitEvent(self,event,timeout=10):
        logging.debug('wisunBp35xx.waitEvent() event=%s',event)
        self._waitEvent = True
        remain = timeout / 0.2 
        while remain > 0: 
            # logging.debug('wisunBp35xx._waitEvent()waiting')
            if not self._waitEvent:
                eventSpl = self._recvEvent.split(' ')
                if eventSpl[1] == event:
                    evStatus = "0"
                    if eventSpl[1] == "21":
                        evStatus = eventSpl[3]
                    logging.debug('wisunBp35xx._waitEvent()exit %s', evStatus)
                    return evStatus # 指定イベントだったらステータスコードを返す
            self._waitEvent = True # 指定以外のイベントだったら再度待機 
            remain = remain - 1 
            time.sleep(0.2)
        return ""


    # UDP受信バッファをフラッシュする
    def drainUdpQueue(self):
        logging.debug('wisunBp35xx.drainUdpQueue()')
        while not self._recvQueue.empty():
            buf = self._recvQueue.get()
            logging.debug('wisunBp35xx.drainUdpQueue() data%s',buf)
        return True

    # UDP受信待ち
    def waitUdpQueue(self,timeout=30):
        remain = timeout / 0.2 
        logging.debug('wisunBp35xx.waitUdpQueue()')
        while self._recvQueue.empty():
            time.sleep(0.2)
            remain = remain - 1 
            if remain <= 0:
                return False,""
        return True,self._recvQueue.get()

    def sendUDP(self,data):
        logging.debug('wisunBp35xx.send() data=%s',data.hex())
        self._recvEvent = ""
        if self._device == "BP35C0":
            cmd = "SKSENDTO 1 {0} 0E1A 1 0 {1:04X} ".format(self.addrV6, len(data))
        else:
            cmd = "SKSENDTO 1 {0} 0E1A 1 {1:04X} ".format(self.addrV6, len(data))
        cmdOK,cmdResp = self._sendCmd(cmd,data)
        if not cmdOK:
            return False # 不正データ

        # コマンド実行中に受け取ったイベントを受け取る
        if not self._recvEvent == "":
            eventSpl = self._recvEvent.split(' ')
            logging.debug('wisunBp35xx.send() event=%s',eventSpl[1])
            evStatus = "0"
            if eventSpl[1] == "21":
                if self._device == "BP35C0":
                    evStatus = eventSpl[4]
                else:
                    evStatus = eventSpl[3]
            logging.debug('wisunBp35xx.send() sta=%s',evStatus)
            if evStatus == "00":
                logging.debug('UDP send sucess')
                return True # 送信成功

        logging.error('UDP send failed')
        return False # 送信失敗

    def _sendCmd(self,cmd,data=b'',timeout=5):
        logging.debug('wisunBp35xx._sendCmd()')
        self._waitCmd = True
        self._respCmd = ""
        self._serial.write(cmd.encode())
        if len(data)>0:
            self._serial.write(data)
        remain = timeout / 0.2 
        while remain > 0: 
            logging.debug('wisunBp35xx._sendCmd()waiting')
            if not self._waitCmd:
                logging.debug('wisunBp35xx._sendCmd()exit %s',self._respCmd)
                return True,self._respCmd
            remain = remain - 1 
            time.sleep(0.2)
        logging.error('wisunBp35xx._sendCmd() timeout')
        return False,"timeout"

    def _recvTask(self):
        # logging.info('wisunBp35xx._recvTask() start')
        self._runThread = True
        prevLine =""
        prevLine =""
        devFound = False
        while self._runThread:
            line = self._serial.readline()
            lineStr = line.strip().decode('utf-8')
            if not lineStr == "":
                logging.debug('<UART>%s',lineStr)
                if lineStr.startswith("EVENT") :
                    lineSpl = lineStr.strip().split(' ')
                    logging.debug('recive EVENT:%s',lineSpl[1])

                    if lineSpl[1] == "20":
                        logging.debug('Recive Beacon')
                        self._foundDevice = True
                        devFound = True
                    if lineSpl[1] == "21":
                        if self._device == "BP35C0":
                            logging.debug('UDP send status=%s',lineSpl[4])
                        else:
                            logging.debug('UDP send status=%s',lineSpl[3])
                    if lineSpl[1] == "22":
                        logging.debug('finish Active Scan')
                        devFound = False
                    if lineSpl[1] == "24":
                        logging.error('PANA connection error')
                        self._connected = False
                    if lineSpl[1] == "25":
                        logging.debug('PANA connected')
                    if lineSpl[1] == "29":
                        logging.warning('PANA disconnected')
                        self._connected = False
                    self._recvEvent = lineStr
                    self._waitEvent = False

                elif lineStr.startswith("ERXUDP") :
                    lineSpl = lineStr.strip().split(' ')
                    if self._device == "BP35C0":
                        logging.debug('recive ERXUDP len:%s',lineSpl[8])
                        logging.debug('recive ERXUDP data:%s',lineSpl[9])
                        self._recvQueue.put(lineSpl[9])
                    else:
                        logging.debug('recive ERXUDP len:%s',lineSpl[7])
                        logging.debug('recive ERXUDP data:%s',lineSpl[8])
                        self._recvQueue.put(lineSpl[8])

                if devFound:
                    if lineStr.startswith("Channel:") :
                        # print("@@@@@ recive Channel: " + lineStr[8:])
                        self.channel = lineStr[8:]

                    if lineStr.startswith("Pan ID:") :
                        # print("@@@@@ recive Pan ID: " + lineStr[7:])
                        self.panid = lineStr[7:]

                    if lineStr.startswith("Addr:") :
                        # print("@@@@@ recive addr: " + lineStr[5:])
                        self.addr = lineStr[5:]

                elif lineStr.startswith("FAIL") :
                    logging.error('command error:%s',lineStr)
                    self._waitCmd = False
                    self._respCmd = lineStr

                elif lineStr.startswith("OK 0") : # ROPTは"OK 0x"形式で返すので特例
                    logging.debug('recive OK:%s',lineStr)
                    self._waitCmd = False
                    self._respCmd = lineStr

                elif lineStr == "OK":
                    logging.debug('recive OK:%s',prevLine)
                    self._waitCmd = False
                    self._respCmd = prevLine

                elif lineStr.startswith("FE80:") : # SKLLはOKを返さないので特例判定
                    self._waitCmd = False
                    self._respCmd = lineStr

                prevLine = lineStr
                time.sleep(0.1)

