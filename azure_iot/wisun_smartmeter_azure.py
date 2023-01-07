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
import RPi.GPIO as GPIO
import os
import sys
import json
import asyncio
# from systemMoniter import SystemMoniter
#from deviceProvisioningService import Device
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient

# import paho.mqtt.publish as publish
# import board
# import adafruit_ssd1306
# from PIL import Image
# from PIL import ImageDraw
# from PIL import ImageFont

from wisun_smartmeter import smartMeterClient, wisunBp35xx
# import smartMeterClient
# import wisunBp35xx

# Azure
id_scope = "0ne005EC119"
registration_id = "21rtogeys3y"
symmetric_key = "0rzcFda3BXmfQl61Y28M2oxdYF5XXMe9/duGrpilokc="
provisioning_host = "global.azure-devices-provisioning.net" 

# 動作設定
DEVICE = "BP35A3"
# DEVICE = "BP35C0"
# Bルート認証ID
ID_WISUN  = "00000000000000000000000000000000"
# Bルート認証パスワード
PWD_WISUN = "XXXXXXXXXXXX"
# シリアルポートデバイス名
SERIAL_PORT = "/dev/ttyS0"
# データ取得周期
WAIT_TIME  = 900

# ログ出力
logging.basicConfig(format='<%(levelname)s>%(message)s', level=logging.INFO)

async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )
    return await provisioning_device_client.register()

async def main():
    print("@@@@@ main() start")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, 0)
    time.sleep(1)
    GPIO.output(18, 1)
    time.sleep(1)

    try:
        # Azure IoT-hubへの登録
        print("@@@@@ main() connect Azure")
        stration_result = await asyncio.gather(provision_device(
            provisioning_host, id_scope, registration_id, symmetric_key
        ))
        registration_result = stration_result[0]

        conn_str = 'HostName=' + registration_result.registration_state.assigned_hub + \
            ';DeviceId=' + registration_id + \
            ';SharedAccessKey=' + symmetric_key 
        # print("@@@@@ connection_string() conn_str: " + conn_str)
        device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
        await device_client.connect()
        msgId = 0

        print("@@@@@ main() connect smart meter")
        wisunDevice = wisunBp35xx.wisunBp35xx(DEVICE,SERIAL_PORT)
        echonet = smartMeterClient.smartMeterClient(wisunDevice)

        telemetry = {}
        while True:
            # print("@@@@@ main() loop")

            if not wisunDevice.isConnected():
                print("connecting SmartMeter")
                if wisunDevice.connect(ID_WISUN,PWD_WISUN):
                    print("SmartMeter connected")
                else:
                    print("SmartMeter connection error!")

            # telemetry = {}
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
                    telemetry.update({'sekisan' : float(valPower)})
                time.sleep(3)

                # 瞬時電力計測値
                flag,valPower,dummy = echonet.request(echonet.SHUNJI_DENRYOKU)
                if flag:
                    print("denryoku {0}[W]\r\n".format(valPower))
                    telemetry.update({'denryoku' : float(valPower)})
                time.sleep(3)

                # 積算電力計測値
                flag,valCurR,valCurT = echonet.request(echonet.SHUNJI_DENRYU)
                if flag:
                    print("R={0}[A] T={1}[A]\r\n".format(valCurR,valCurT))
                    telemetry.update({'R' : float(valCurR)})
                    telemetry.update({'T' : float(valCurT)})
                # time.sleep(3)

                if telemetry is not None:
                    msgId += 1
                    telemetry["MsgId"] = msgId
                    print(telemetry)
                    data = json.dumps(telemetry)
                    await device_client.send_message(data)
 
            print("@@@@@ main() sleep")
            time.sleep(WAIT_TIME)
    except:
        print("@@@@@ main() except")
        traceback.print_exc()
        wisunDevice.disconnect()
        GPIO.output(18, 0)
        print("@@@@@ main() exit")

if __name__ == '__main__':
    asyncio.run(main())
#    main()

