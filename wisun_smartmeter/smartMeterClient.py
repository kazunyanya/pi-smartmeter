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

# ログ出力
logging.basicConfig(format='<%(levelname)s>%(message)s', level=logging.INFO)

# スマートメーター(HEMS端末側)
# ３．３．２５ 低圧スマート電力量メータクラス規定
class smartMeterClient:
    # 要求種別
    DOUSA = "80" # 動作状態
    SEKISAN_DENRYOKU = "E0" # 積算電力量 計測値 (正方向計測値)
    SEKISAN_DENRYOKU_TANNI = "E1" # 積算電力量単位
    SEKISAN_DENRYOKU_RIREKI = "E2"
    SEKISAN_DENRYOKU_REV = "E3"
    SEKISAN_DENRYOKU_RIREKI_REV = "E4"
    SEKISAN_RIREKI_DAYS = "E5"
    SHUNJI_DENRYOKU = "E7" # 瞬時電力計測値
    SHUNJI_DENRYU = "E8"
    floatPwrUnit = 0.1 # 積算電力の単位(0.0001-1.0 watt)

    # 初期化
    def __init__(self,wisun):
        self._wisun = wisun

    # データ要求
    def request(self,reqEPC="80"):
        if not self._wisun.isConnected():
            return False,-1,-1

        # 要求データを作成
        hexEPC = "0x" + reqEPC
        intEPC = int(hexEPC,16)
        byteEPC = intEPC.to_bytes(1,'big')
        echonetLiteFrame = b''
        echonetLiteFrame += b'\x10\x81'    # EHD (参考:EL p.3-2)
        echonetLiteFrame += b'\x00\x01'    # TID (参考:EL p.3-3)
        echonetLiteFrame += b'\x05\xFF\x01'  # SEOJ -- souce object(コントローラ)
        echonetLiteFrame += b'\x02\x88\x01'  # DEOJ -- 低圧スマート電力量メータクラス
        echonetLiteFrame += b'\x62'        # ESV(62: Get)
        echonetLiteFrame += b'\x01'        # OPC(1個)(参考:EL p.3-7)
        echonetLiteFrame += byteEPC
        echonetLiteFrame += b'\x00'

        self._wisun.drainUdpQueue() # UDP 受信キューをフラッシュする

        # UDP送信
        if not self._wisun.sendUDP(echonetLiteFrame):
            logging.debug('smartMeterClient.request() UDP transmit failded')
            return False,-1,-1 # 送信失敗 

        # UDP 受信待ち 
        retry = 5 
        while retry > 0:
            flag,udp =  self._wisun.waitUdpQueue()
            if not flag:
                logging.error('smartMeterClient.request() UDP revive timeout')
                return False,-1,-1 # 受信タイムアウト 

            # 応答データを解析
            logging.debug('smartMeterClient.request() recv data=%s',udp)
            seoj = udp[8:8+6]
            logging.debug('SEOJ =%s',seoj)
            deoj = udp[14:14+6]
            logging.debug('DEOJ =%s',deoj)
            esv = udp[20:20+2]
            logging.debug('ESV =%s',esv)
            # print("@@@@@ ESV=" + esv)
            if seoj == "028801" and esv == "72" : # SEOJ(028801: smart meter),ESV(72: Resp)
                opc = udp[22:22+2]
                logging.debug('OPC =%s',opc)
                epc = udp[24:24+2]
                logging.debug('EPC =%s',epc)
                pdc = udp[26:26+2]
                logging.debug('PDC =%s',pdc)
                edt = udp[28:]
                logging.debug('EDT =%s',edt)

                if not epc == reqEPC:
                    logging.error('message no match =%s',udp)
                    continue

                logging.debug('smartMeterClient.request() step2')
                # 動作状態
                if epc == self.DOUSA:
                    intStat = int(edt,16)
                    return True,intStat,-1

                # 積算電力量 計測値 (正方向計測値)
                if epc == self.SEKISAN_DENRYOKU:
                    intPower = int(edt,16)
                    floatPower = float(intPower) * self.floatPwrUnit
                    # print("@@@@@ sekisan={0}".format(floatPower))
                    return True,floatPower,-1

                # 瞬時電力計測値
                if epc == self.SHUNJI_DENRYOKU:
                    intPower = int(edt,16)
                    floatPower = float(intPower)
                    # print("@@@@@ sekisan={0}".format(floatPower))
                    return True,floatPower,-1

                # 積算電力量単位
                if epc == self.SEKISAN_DENRYOKU_TANNI:
                    intPwrUnit = int(edt,16)
                    if intPwrUnit == 0:
                        self.floatPwrUnit = 1.0
                    elif intPwrUnit == 1:
                        self.floatPwrUnit = 0.1
                    elif intPower == 2:
                        intPwrUnit= 0.01
                    elif intPower == 3:
                        self.floatPwrUnit = 0.001
                    elif intPwrUnit == 4:
                        self.floatPwrUnit = 0.0001
                    return True,self.floatPwrUnit,-1

                if epc == self.SHUNJI_DENRYU:
                    intCurR = int(edt[:4],16)
                    intCurT = int(edt[4:],16)
                    valCurR = float(intCurR) /10
                    valCurT = float(intCurT) /10
                    # print("@@@@@ R={0} T={1}".format(valCurR,valCurT))
                    return True,valCurR,valCurT
            retry = retry -1

        # スマートメーターから応答がなかったらエラー
        return False,-1,-1

