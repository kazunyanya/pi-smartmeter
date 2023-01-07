# スマートメータのデータをAzure IoT に送る

## 概要
本資料はスマートメータから取得したデータをAzure IoT Centralで収集しblobストレージに蓄積するまでの手順を記したものである  

### 参考資料
Azure IoT Central クイックスタート  
https://docs.microsoft.com/ja-jp/azure/iot-develop/quickstart-send-telemetry-central?pivots=programming-language-ansi-c  

Azure IoT Central デバイステンプレート  
https://docs.microsoft.com/ja-jp/azure/iot-central/core/howto-edit-device-template  

## 掲載内容
本資料は以下の内容に従いAzure Iot Centralとスマートメータからのデータ取得について掲載している  
１．Raspberry Piのセットアップ  
　1-1. 書き込みツールのインストール  
　1-2. SDカードへの書き込み  
　1-3. Raspberry Piの起動と初期設定  
　1-4.ネットワーク経由の接続  
　1-5. タイムゾーンの設定  
　1-6. OSアップグレード  
　1-7. 必須パッケージのインストール  
２．Azure IoT central  
　2-1. Azure IoTデバイスの作成  
　2-2. Azure IoT SDKのインストール  
　2-3. Azrure IoT centralとの接続確認    
３．スマートメータ  
　3-1. ハードウェアのセットアップ  
  3-2. シリアルポートの有効化 
　3-3. ライブラリのインストール  
　3-4. サンプルコードの実行  
４．スマートメータアプリの実行とIoT デバイス登録  
　4-1. Azure IoT Central上でデバイス登録  
　4-2. データの可視化  
５．Blobストレージへのエクスポート  

## 必要なもの
本資料で掲載している内容を実施するためには以下の機材を用意しておく必要がある

・スマートメータ接続認証ID  
　電力メーター情報発信サービス（Bルートサービス）利用申込を行ったあとに郵送される書類に入っている  
　申し込みは各電力会社のWebページにて行う必要がある  
　東京電力: https://www.tepco.co.jp/pg/consignment/liberalization/smartmeter-broute.html  

・WiSUN通信デバイス
　ロームデバイスの代理店もしくはオンラインショップで購入可能である  
　BP35A3(+変換基板)  
　BP35C0(+専用アンテナ)  

・Raspberry Pi本体 (3B,4,ZeroW)  
・Raspberry Pi用 ACアダプタ  
・microSDカード  
・SDカードリーダ  
・HDMIモニタ(+ケーブル)  
・USBキーボード  

・PC (Windowsもしくはそれ以外)  
・有線LANケーブルおよび有線ルータ  

・ブレッドボードもしくはWiSUN組み立てキット  
https://www.switch-science.com/products/6467  

## 1.Raspberry Piのセットアップ
Raspberry Piを使うためにはボードにOSを入れる必要がある  
本資料では 2022年１１月時点で最新のRaspberrypi OSをインストールしている    

OSは以下の場所からダウンロードすることができる
```
https://www.raspberrypi.com/software/operating-systems/
```

今回はデスクトップ環境は不要であるためLite版(Raspberry Pi OS Lite)をダウンロードし使用する  
ダウンロードのリンクを開くと次のファイルがダウンロードされる  
```
2022-09-22-raspios-bullseye-armhf-lite.img.xz
```

また同サイトからOSイメージを書き込むツール(Raspberry Pi Imager)もダウンロードしておく  
```
https://www.raspberrypi.com/software/
```

### 1-1.書き込みツールのインストール
PCに前項でダウンロードしたRaspberry Pi Imagerをインストールする  
winddows版の場合.exeフォーマットのファイルとなっているためダブルクリックしてインストールを開始する    
インストールが成功すると Raspberry Pi Imagerという名称のアイコンが追加される  

### 1-2.SDカードへの書き込み
microSDカードに前項で取得したファイルを書き込みを行う    
書き込みツールであるRaspberry Pi Imagerを起動する  
起動すると次のような画面が表示される  
![Imager01](images/Imager01.png "Imager01") 

まずインストールするOSを選択する  
![Imager02](images/Imager02.png "Imager02") 

今回は前項でダウンロードしたOSイメージを利用することから「カスタムイメージを使う」を選択  
![Imager03](images/Imager03.png "Imager03") 

ファイル選択ダイアログが表示されるのでダウンロードしたファイルを選択し[Open]を押下する  
![Imager04](images/Imager04.png "Imager04") 

つぎにUSB-SDカードリーダにmicroSDカード(16GB以上)を装着しPCに接続し「ストレージを選ぶ」を押下する  
![Imager05](images/Imager05.png "Imager05") 

対象デバイスのリストが表示されるのでmicroSDカードの近似サイズのUSBストレージを選択する  
![Imager06](images/Imager06.png "Imager06") 

全ての選択が終わったら「書き込む」ボタンを押下し、「はい」を押下する
![Imager07](images/Imager07.png "Imager07") 
![Imager08](images/Imager08.png "Imager08") 

microSDへの書き込みが開始されるので終了まで待つ  
書き込みが完了したらUSBカードリーダを外し、microSDを抜き取ります  
![Imager09](images/Imager09.png "Imager09") 
![Imager10](images/Imager10.png "Imager10") 

### 1-3. Raspberry Piの起動と初期設定
前項で書き込んだ microSDカードを Raspberry Piに装着し起動する    
この際 HDMIコネクタにはディスプレイ、USBコネクタにはキーボードを接続しておく
またネットワークは有線ケーブル接続とする  
※ ルータ設定etcでリモート接続できない場合が多いので有線接続を推奨  

![raspi01](images/raspi01.jpg "raspi01") 


しばらくするとHDMI接続されたディスプレイ上に初期設定メニューが表示される  
初期設定ではキーボードの種類と初期ログインユーザの設定を行う  
今回は旧OSでデフォルト値として使っていたアカウントとパスワードを指定しているが、セキュリティ的に強化したい場合は別のユーザー名とパスワードを設定すること  
```
Configurating keyboard-configuration:
Keyboard layout:
-> Other
--> Japanese
---> Japanese
----> OK

Please enter new username:
 pi

Please set a password for pi:
 raspberry
Please confirm the password:
 raspberry
```

設定が終わるとログイン入力となるので先ほど設定したユーザ名とパスワードを入力する  
```
raspberrypi login: pi
Password: raspberry
```

ログインが成功するとコマンド入力プロンプトが表示される  
```
pi@raspberrypi:~$ 
```

今回作成するシステムではディスプレイを使用しないヘッドレス運用とするのでネットワーク経由でリモートログインできるようにする  
```
pi@raspberrypi:~$ sudo raspi-config
3 Interface Option
-> I2 SSH
--> <Yes>
<finish>
```

リモートログイン設定が終わったら Raspberry PiのIPアドレスを調べる  
次のようなコマンドを入力する inet行に IPアドレスが表示される  
ここで表示されたIPアドレスは後で使用するためメモしておく(メモ①)  
```
pi@raspberrypi:~$ ifconfig eth0
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.10.145  netmask 255.255.255.0  broadcast 192.168.10.255
...
```


### 1-4.ネットワーク経由の接続
以降はディスプレイとキーボードによる操作は難しくなるので SSHによるリモート接続で操作を行う  
TeratermなどのSSHクライアントを用い先ほどメモ①したIPアドレスで接続する  
```
ユーザ名： pi
パスフレーズ: raspberry
```

Teratermでの例  
![teraterm01](images/teraterm01.png "teraterm01") 
![teraterm02](images/teraterm02.png "teraterm02") 

SSH接続が成功すると次のような画面となる  
![teraterm03](images/teraterm03.png "teraterm03")
 
Teratermでは次のような操作でコマンドラインのコピー/ペースト、ファイル送信が可能である  
[ALT]+[C] 選択領域のコピー  
[ALT]+[V] コマンドラインへのペースト  
画面内へのファイルドラッグ ファイル送信  


### 1-5. タイムゾーンの設定
デフォルトではGMT(グリニッジ標準時間)となっているため日本標準時にセットする  
```
$ sudo timedatectl set-timezone Asia/Tokyo
```

### 1-6. OSアップグレード
ダウンロードしたOSが最新とは限らないためオンラインで更新を行う  
```sh
$ sudo apt-get update
$ sudo apt-get upgrade
```

### 1-7. 必須パッケージのインストール
```sh
$ sudo apt-get install -y git cmake build-essential curl libcurl4-openssl-dev libssl-dev uuid-dev
$ sudo apt-get install python3-pip
$ pip3 install pyserial
```

インストールされたパッケージのバージョンを確認する  
cmake のバージョンが 2.8.12 より大きく、GCC のバージョンが 4.4.7 より大きいことを確認  
```sh
$ cmake --version
cmake version 3.18.4

CMake suite maintained and supported by Kitware (kitware.com/cmake).


$ gcc --version
gcc (Raspbian 10.2.1-6+rpi1) 10.2.1 20210110
Copyright (C) 2020 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

## ２．Azure IoT central
Raspberry PiとAzure IoT centralを接続するための登録を行う  


### 2-1. Azure IoTデバイスの作成
Azure IoT centralの画面にてデバイス作成を行う  
画面上部にある[+作成]ボタンを押下する  
![azure01](images/azure01.png "azure01") 

デバイス作成画面となる  
デバイス名は任意の文字列を入力  
今回は新規デバイスであるため「デバイステンプレート」項目は未割り当てのままとする  
入力が終わったら[作成]ボタンを押下する  
![azure02](images/azure02.png "azure02")

作成が成功するとリスト上に作成したデバイス名が表示されるようになる  
次に作成したデバイス名のリンクを開く   
![azure03](images/azure03.png "azure03")

デバイス情報のページが開く  
まだデバイスとの接続が行われていないのでデータは空欄のままである   
ここで画面上部の[接続]ボタンを押下する  
![azure04](images/azure04.png "azure04") 

デバイス接続情報が表示されるのでメモしておく  
例：  
```
ID スコープ: 0ne005EC119
デバイス ID: ac7hs9q2re
認証の種類: SAS  
主キー: bnRdgAa+3FsFqmJCoNXZN9yfjwqIlo/eUNMaWOLg8Og=
セカンダリ キー: cvo2+upGUMvtYXh41wMIDcWFUSRSm7j2NJKDJxMwJWI=
```

![azure05](images/azure05.png "azure05") 


### 2-2. Azure IoT SDKのインストール
Azure IoT Centralの準備が整ったら Raspberry Piに SDKをインストールする  
今回はpython3を使用使用しているので python版SDKをダウンロードする  
```
$ git clone https://github.com/Azure/azure-iot-sdk-python
```

ダウンロードしたSDKをインストールする  
```
$ pip3 install azure-iot-device
```

### 2-3. Azrure IoT centralとの接続確認
AzureクラウドとRasperry Piの設定が正しいか確認するため簡単なテストアプリを動作させる  
今回は公開したリポジトリからazure-cent-sample.py のサンプルコードを実行する


実行する前にソースコードを編集し認証データをセットする

```
以下の{}部分を書き換える  
# Azure
id_scope = "{ID スコープ}"
registration_id = "{デバイス ID}"
symmetric_key = "{主キー}"
```

#### 2-3-1. サンプルコードの実行
サンプルコードを実行を行うと次のようなログが出力される  
```
$ python3 azure-cent01.py
@@@@@ main() start
<INFO>Creating client for connecting using MQTT over TCP
<INFO>Registering with Provisioning Service...
<INFO>Enabling reception of response from Device Provisioning Service...
<INFO>Connect using port 8883 (TCP)
<INFO>connected with result code: 0
<INFO>_on_mqtt_connected called
<INFO>subscribing to $dps/registrations/res/# with qos 1
<INFO>suback received for 1
<INFO>Successfully subscribed to Device Provisioning Service to receive responses
<INFO>publishing on $dps/registrations/PUT/iotdps-register/?$rid=5acc20d5-8f00-42b0-b743-e7fb041d675d
<INFO>payload published for 2
<INFO>message received on $dps/registrations/res/202/?$rid=5acc20d5-8f00-42b0-b743-e7fb041d675d&retry-after=3
<INFO>RegistrationStage(RequestAndResponseOperation): polling
<INFO>publishing on $dps/registrations/GET/iotdps-get-operationstatus/?$rid=07147be3-7917-4455-af80-a87bd0ff53c2&operationId=5.0111a09938d21874.7b0682c2-2bd5-4858-9d9a-a75acd062712
<INFO>payload published for 3
<INFO>message received on $dps/registrations/res/200/?$rid=07147be3-7917-4455-af80-a87bd0ff53c2
<INFO>Successfully registered with Provisioning Service
<INFO>Forcing paho disconnect to prevent it from automatically reconnecting
@@@@ regist:ac7hs9q2re
iotc-7e352a34-21c1-46f2-81c9-2e6ebf46ee59.azure-devices.net
initialAssignment
null
assigned
Will send telemetry from the provisioned device
<INFO>Creating client for connecting using MQTT over TCP
@@@@@ connect IoT central
<INFO>Connecting to Hub...
<INFO>Connect using port 8883 (TCP)
<INFO>connected with result code: 0
<INFO>_on_mqtt_connected called
<INFO>Connection State - Connected
<INFO>Successfully connected to Hub
<INFO>Enabling feature:c2d...
<INFO>subscribing to devices/ac7hs9q2re/messages/devicebound/# with qos 1
<INFO>suback received for 1
<INFO>Successfully enabled feature:c2d
@@@@@ connected
@@@@@ send{'TEST': 1.01, 'MsgId': 1}
<INFO>Sending message to Hub...
<INFO>publishing on devices/ac7hs9q2re/messages/events/
<INFO>payload published for 2
<INFO>Successfully sent message to Hub
@@@@@ send{'TEST': 2.02, 'MsgId': 2}
<INFO>Sending message to Hub...
<INFO>publishing on devices/ac7hs9q2re/messages/events/
<INFO>payload published for 3
<INFO>Successfully sent message to Hub
...
```
前項でデバイス登録した Azureクラウドを開くとテレメトリデータが入っていれば正常にデータ送信されている  
![azure10](images/azure10.png "azure10") 

## ３．スマートメータ

### 3-1. ハードウェアのセットアップ
スマートメータと接続するためにはWiSUN通信デバイス(BP35A3もしくはBP35C0)が必要となる  
これらはオンラインショップで購入可能である  
以下の写真に従って Raspberry Piと WiSUN通信デバイスを接続する

・BP35A3  
{写真}  
・BP35C0  
{写真}  

ブレッドボードで組み立てる以外にも以下の場所で組み立てキットが販売されているので購入すると便利である  
なおキットにはWiSUN通信デバイスは付属していないため別途購入する必要がある  
https://www.switch-science.com/products/6467  

### 3-2. シリアルポートの有効化 
WiSUN通信デバイスを使うためには Raspberry Piのシリアルポートが必要となる 
デフォルトでは無効化されていることから次の操作を行いシリアルポートを有効化しておく  
```
$ sudo raspi-config

Raspberry Pi Software Configuration Tool (raspi-config)
3 Interface Options
<Select>
I6 Serial Port
<Select>
Would you like a login shell to be accessible over serial?
<No>
Would you like the serial port hardware to be enabled?
<Yes>
The serial login shell is disabled
The serial interface is enabled
<Ok>
<Finish>
Would you like to reboot now?
<Yes>
```
設定を有効化するため　Raspberry Piが再起動する  

### 3-3. スマートメータライブラリのインストール
日本向けスマートメータのライブラリはgithub上で公開されている
次のコマンドでインストールを行う    
```
$ cd ~/
$ git clone https://github.com/kazunyanya/pi-smartmeter.git
$ cd pi-smartmeter
$ pip3 install .
```

### 3-4. サンプルコードの実行
github配布ライブラリのフォルダにはサンプルコード sample.py が入っています  
実行前に以下の部分をviエディタ等で３か所編集を行います  

使用しているWiSUNデバイスの行にのみコメントアウトを外す
```
 動作設定 - 使用するデバイスのみコメントアウトを外す
DEVICE = "BP35A3"
# DEVICE = "BP35C0"
```

スマートメータ接続認証IDとパスワードを設定する  
この情報は電力会社から郵送される書類に入っている    
```
# Bルート認証ID
ID_WISUN  = "00000000000000000000000000000000"
# Bルート認証パスワード
PWD_WISUN = "SSSSSSSSSSSS"
```

以下のコマンドでサンプルコードの実行する
数分ごとにスマートメータの値が表示されていれば正常に動作しています    
```
$ cd ~/pi-smartmeter
$ python3 sample.py

@@@@@ main() start
connecting SmartMeter
<INFO>init bp35c0x
<INFO>BP35A3 version 1.2.10
<INFO>finding echonet device
<INFO>echonet device found
<INFO>connecting echonet device
<INFO>echonet device connected
SmartMeter connected
request for SmartMeter
dousa 0x30

sekisan tanni 0.1[kWh]

sekisan 3871.2000000000003[kWh]

denryoku 226.0[W]

R=0.0[A] T=3.0[A]

@@@@@ main() sleep
```

## ４．スマートメータアプリの実行とIoT デバイス登録
今回は公開したリポジトリからwisun_smartmeter_azure.py のサンプルコードを実行する

まずサンプルコードをWiSUNライブラリの中にコピーします  
```
$ cp wisun_smartmeter_azure.py ~/pi-smartmeter/
```

次にサンプルコードを編集します  
編集する内容な前項で変更したパラメータと同一になります
```
$ cd ~/pi-smartmeter
$ vi wisun_smartmeter_azure.py

 Azure
id_scope = "{ID スコープ}"
registration_id = "{デバイス ID}"
symmetric_key = "{主キー}"
provisioning_host = "global.azure-devices-provisioning.net"

# 動作設定
DEVICE = "BP35A3"
# DEVICE = "BP35C0"
# Bルート認証ID
ID_WISUN  = "00000000000000000000000000000000"
# Bルート認証パスワード
PWD_WISUN = "SSSSSSSSSSSS"
```

次のようなコマンドを実行するとスマートメータアプリが起動し電力量がAzrue IoT Centralに送信されます
```
$ cd ~/pi-smartmeter
$ python3 sample.py

@@@@@ main() start
/home/pi/pi-smartmeter/wisun_smartmeter_azure.py:75: RuntimeWarning: This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.
  GPIO.setup(18, GPIO.OUT)
@@@@@ main() connect Azure
<INFO>Creating client for connecting using MQTT over TCP
<INFO>Registering with Provisioning Service...
<INFO>Enabling reception of response from Device Provisioning Service...
<INFO>Connect using port 8883 (TCP)
....
martMeter connected
request for SmartMeter
dousa 0x30

sekisan tanni 0.1[kWh]

sekisan 3871.3[kWh]

denryoku 175.0[W]

R=0.0[A] T=2.0[A]

{'sekisan': 3871.3, 'denryoku': 175.0, 'R': 0.0, 'T': 2.0, 'MsgId': 1}
<INFO>Sending message to Hub...
<INFO>publishing on devices/ac7hs9q2re/messages/events/
<INFO>payload published for 1
<INFO>Successfully sent message to Hub
```
### 4-1. Azure IoT Central上でデバイス登録
Raspberry側からAzure IoT Centralへデータ送信ができるようになったら Azureクラウド上でデバイス登録を行う  


![azure10](images/azure10.png "azure10") 
![azure11](images/azure11.png "azure11") 
![azure12](images/azure12.png "azure12") 
![azure13](images/azure13.png "azure13") 
![azure14](images/azure14.png "azure14") 
![azure15](images/azure15.png "azure15") 



### 4-2. データの可視化

## ５．Blobストレージへのエクスポート

