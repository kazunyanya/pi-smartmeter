#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from threading import Event, Thread
import time
import datetime
import binascii
import serial
import queue
import traceback
import logging
import RPi.GPIO as GPIO

from wisun_smartmeter import smartMeterClient, wisunBp35xx

# 動作設定 - 使用するデバイスのみコメントアウトを外す
# DEVICE = "BP35A3"
DEVICE = "BP35C0"

# Bルート認証ID
ID_WISUN  = "00000000000000000000000000000000"
# Bルート認証パスワード
PWD_WISUN = "SSSSSSSSSSSS"

# シリアルポートデバイス名
SERIAL_PORT = "/dev/ttyS0"

# データ取得周期
WAIT_TIME  = 60

# ログ出力
logging.basicConfig(format='<%(levelname)s>%(message)s', level=logging.INFO)

def main():
    print("@@@@@ main() start")

    # WiSUNデバイスのリセット解除
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, 0)
    time.sleep(1)
    GPIO.output(18, 1)
    time.sleep(1)

    try:
        wisunDevice = wisunBp35xx.wisunBp35xx(DEVICE,SERIAL_PORT)
        echonet = smartMeterClient.smartMeterClient(wisunDevice)

        while True:
            # print("@@@@@ main() loop")
            if not wisunDevice.isConnected():
                print("connecting SmartMeter")
                if wisunDevice.connect(ID_WISUN,PWD_WISUN):
                    print("SmartMeter connected")
                else:
                    print("SmartMeter connection error!")

            if wisunDevice.isConnected():
                print("request for SmartMeter")

                # 動作状態
                flag,stat,dummy = echonet.request(echonet.DOUSA)
                if flag:
                    print("dousa 0x{:02x}\r\n".format(stat))
                time.sleep(3)

                # 積算電力計測値単位
                flag,valPwrUnit,dummy = echonet.request(echonet.SEKISAN_DENRYOKU_TANNI)
                if flag:
                    print("sekisan tanni {0}[kWh]\r\n".format(valPwrUnit))
                time.sleep(3)

                # 積算電力計測値
                flag,valPower,dummy = echonet.request(echonet.SEKISAN_DENRYOKU)
                if flag:
                    print("sekisan {0}[kWh]\r\n".format(valPower))
                time.sleep(3)

                # 瞬時電力計測値
                flag,valPower,dummy = echonet.request(echonet.SHUNJI_DENRYOKU)
                if flag:
                    print("denryoku {0}[W]\r\n".format(valPower))
                time.sleep(3)

                # 積算電力計測値
                flag,valCurR,valCurT = echonet.request(echonet.SHUNJI_DENRYU)
                if flag:
                    print("R={0}[A] T={1}[A]\r\n".format(valCurR,valCurT))
                # time.sleep(3)
 
            print("@@@@@ main() sleep")
            time.sleep(WAIT_TIME)
    except:
        print("@@@@@ main() except")
        traceback.print_exc()
        wisunDevice.disconnect()
        GPIO.output(18, 0)
        print("@@@@@ main() exit")

if __name__ == '__main__':
    main()

