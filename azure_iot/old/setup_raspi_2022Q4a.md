# スマートメータのデータをAzure IoT に送る

![title](images/title.jpg "title") 

## 概要
本資料はスマートメータから取得したデータをAzure IoT Centralで収集しblobストレージに蓄積するまでの手順を記したものです  

### 参考資料
Azure IoT Central クイックスタート  
https://docs.microsoft.com/ja-jp/azure/iot-develop/quickstart-send-telemetry-central?pivots=programming-language-ansi-c  

Azure IoT Central デバイステンプレート  
https://docs.microsoft.com/ja-jp/azure/iot-central/core/howto-edit-device-template  

## 掲載内容
本資料は以下の内容に従いAzure Iot Centralとスマートメータからのデータ取得について掲載しています  

１．ハードウェアのセットアップ  
　1-1. Raspberry PiとWiSUNデバイスの接続

２．Raspberry Piのセットアップ  
　2-1. 書き込みツールのインストール  
　2-2. SDカードへの書き込み  
　2-3. Raspberry Piの起動と初期設定  
　2-4.ネットワーク経由の接続  
　2-5. タイムゾーンの設定  
　2-6. OSアップグレード  
　2-7. 必須パッケージのインストール  

３．スマートメータ  
　3-1. シリアルポートの有効化  
　3-2. ライブラリのインストール  
　3-3. サンプルコードの実行  

４．Azure IoT central  
　4-1. Azure IoTデバイスの作成  
　4-2. Azure IoT SDKのインストール  
　4-3. Azrure IoT centralとの接続確認  
  
５．スマートメータアプリの実行とIoT デバイス登録  
　5-1. スマートメータアプリの実行
　5-2. Azure IoT Central上でデバイス登録  
　5-3. データの可視化  

６．Blobストレージへのエクスポート  
　6-1. Blobストレージの作成
　6-2. エクスポート設定
　6-3. Blobストレージのエクスポート

## 必要なもの
本資料で掲載している内容を実施するためには以下の機材を用意しておく必要があります

・スマートメータ接続認証ID  
　電力メーター情報発信サービス（Bルートサービス）利用申込を行ったあとに郵送される書類に入っています  
　申し込みは各電力会社のWebページにて行ってください  
　東京電力: https://www.tepco.co.jp/pg/consignment/liberalization/smartmeter-broute.html  

・WiSUN通信デバイス
　ロームデバイスの代理店もしくはオンラインショップで購入可能です  
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

## 1.ハードウェアのセットアップ  
スマートメータからデータを取り出すためには次のようなハードウェアを準備します  

![raspi01](images/raspi01.jpg "raspi01") 
### 1-1. Raspberry PiとWiSUNデバイスの接続
スマートメータと接続するためにはWiSUN通信デバイス(BP35A3もしくはBP35C0)が必要となります  
これらはオンラインショップで購入可能です  

(参考)キットの購入  
ブレッドボードで組み立てる以外にも以下の場所で組み立てキットが販売されており購入することができます  
なおキットにはWiSUN通信デバイスは付属していないため別途購入してください  
https://www.switch-science.com/products/6467  

#### 信号線の結線
Raspberry PiとWiSUNデバイスを接続するためには次のような結線が必要です  

Raspberry Pi    WiSUNデバイス  
3.3V ---------- VCC  
GND -----+---- GND  
　　　　+---- P3C  
TXD ----------- RXD  
RXD ----------- TXD  
GPIO18 -------- RESET  

実際の配線は次のようになります  
![wisun_wire01.jpg](images/wisun_wire01.jpg "wisun_wire01.jpg") 

#### BP35A3を使用
WiWUNデバイス(BP35A3)を使用する場合は次のようにモジュールを搭載します  
![wisun_bp35a3.jpg](images/wisun_bp35a3.jpg "wisun_bp35a3.jpg") 

#### BP35C0を使用
WiWUNデバイス(BP35C0)を使用する場合は次のようにモジュールを搭載します  
モジュールの端子のうち内側のみ接続するようにしてください 
![wisun_bp35c0.jpg](images/wisun_bp35c0.jpg "wisun_bp35c0.jpg") 

## 2.Raspberry Piのセットアップ
Raspberry Piを使うためにはボードにOSを入れる必要があります  
本資料では 2022年１１月時点で最新のRaspberrypi OSをインストールします  

OSは以下の場所からダウンロードしてください  
```
https://www.raspberrypi.com/software/operating-systems/
```

今回はデスクトップ環境は不要であるためLite版(Raspberry Pi OS Lite)をダウンロードし使用します  
ダウンロードのリンクを開くと次のファイルがダウンロードされます  
```
2022-09-22-raspios-bullseye-armhf-lite.img.xz
```

また同サイトからOSイメージを書き込むツール(Raspberry Pi Imager)もダウンロードしておいてください  
```
https://www.raspberrypi.com/software/
```

### 2-1.書き込みツールのインストール
PCに前項でダウンロードしたRaspberry Pi Imagerをインストールを行います  
winddows版の場合.exeフォーマットのファイルとなっているためダブルクリックしてインストールを開始します    
インストールが成功すると Raspberry Pi Imagerという名称のアイコンが追加されます  

### 2-2.SDカードへの書き込み
microSDカードに前項で取得したファイルを書き込みを行います    
書き込みツールであるRaspberry Pi Imagerを起動  
起動すると次のような画面が表示されます  
![Imager01](images/Imager01.png "Imager01") 

まずインストールするOSを選択します  
![Imager02](images/Imager02.png "Imager02") 

今回は前項でダウンロードしたOSイメージを利用することから「カスタムイメージを使う」を選択  
![Imager03](images/Imager03.png "Imager03") 

ファイル選択ダイアログが表示されるのでダウンロードしたファイルを選択し[Open]を押下します  
![Imager04](images/Imager04.png "Imager04") 

つぎにUSB-SDカードリーダにmicroSDカード(16GB以上)を装着しPCに接続し「ストレージを選ぶ」を押下  
![Imager05](images/Imager05.png "Imager05") 

対象デバイスのリストが表示されるのでmicroSDカードの近似サイズのUSBストレージを選択  
![Imager06](images/Imager06.png "Imager06") 

全ての選択が終わったら「書き込む」ボタンを押下し、「はい」を押下します
![Imager07](images/Imager07.png "Imager07") 
![Imager08](images/Imager08.png "Imager08") 

microSDへの書き込みが開始されるので終了まで待つ  
書き込みが完了したらUSBカードリーダを外し、microSDを抜き取ります  
![Imager09](images/Imager09.png "Imager09") 
![Imager10](images/Imager10.png "Imager10") 

### 2-3. Raspberry Piの起動と初期設定
前項で書き込んだ microSDカードを Raspberry Piに装着し起動させます    
この際 HDMIコネクタにはディスプレイ、USBコネクタにはキーボードを接続しておいてください
またネットワークは有線ケーブル接続とします  
※ ルータ設定etcでリモート接続できない場合が多いのことから有線接続を推奨しています  

![raspi03](images/raspi03.jpg "raspi03") 

しばらくするとHDMI接続されたディスプレイ上に初期設定メニューが表示される  
初期設定ではキーボードの種類と初期ログインユーザの設定を行う  
今回は旧OSでデフォルト値として使っていたアカウントとパスワードを指定しています  
もしセキュリティ的に強化したい場合は別のユーザー名とパスワードを設定するようにしてください  
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

今回作成するシステムではディスプレイを使用しないヘッドレス運用になりますのでネットワーク経由でリモートログインできるようにします  
```
pi@raspberrypi:~$ sudo raspi-config
3 Interface Option
-> I2 SSH
--> <Yes>
<finish>
```

リモートログイン設定が終わったら Raspberry PiのIPアドレスを調べておきます  
次のようなコマンドを入力する inet行に IPアドレスが表示されます  
ここで表示されたIPアドレスは後で使用するためメモしておいてください(メモ①)  
```
pi@raspberrypi:~$ ifconfig eth0
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.10.145  netmask 255.255.255.0  broadcast 192.168.10.255
...
```


### 2-4.ネットワーク経由の接続
以降はディスプレイとキーボードによる操作は難しくなるので SSHによるリモート接続で操作を行います  
TeratermなどのSSHクライアントを用い先ほどメモ①したIPアドレスで接続します  
```
ユーザ名： pi
パスフレーズ: raspberry
```

Teratermでの例  
![teraterm01](images/teraterm01.png "teraterm01") 
![teraterm02](images/teraterm02.png "teraterm02") 

SSH接続が成功すると次のような画面となる  
![teraterm03](images/teraterm03.png "teraterm03")
 
Teratermでは次のような操作でコマンドラインのコピー/ペースト、ファイル送信ができます  
[ALT]+[C] 選択領域のコピー  
[ALT]+[V] コマンドラインへのペースト  
画面内へのファイルドラッグ ファイル送信  


### 2-5. タイムゾーンの設定
デフォルトではGMT(グリニッジ標準時間)となっているため日本標準時にセットします  
```
$ sudo timedatectl set-timezone Asia/Tokyo
```

### 2-6. OSアップグレード
ダウンロードしたOSが最新とは限らないためオンラインで更新を行います  
```sh
$ sudo apt-get update
$ sudo apt-get upgrade
```

### 2-7. 必須パッケージのインストール
AzureSDKとpython動作に必要なパッケージをインストールします  
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

## ３．スマートメータ
この章ではスマートメータ接続に必要な機能をセットアップします  

### 3-1. シリアルポートの有効化 
WiSUN通信デバイスを使うためには Raspberry Piのシリアルポートが必要となります 
デフォルトでは無効化されていることから次の操作を行いシリアルポートを有効化させます  
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
設定を有効化するためRaspberry Piが再起動されます  
再起動が終わったら再度SSHでログインしてください  

### 3-2. スマートメータライブラリのインストール
日本向けスマートメータのライブラリとしてgithub上で公開されているものを利用します
```https://github.com/kazunyanya/pi-smartmeter```

ライブラリは次のコマンドでインストールします    
```
$ cd ~/
$ git clone https://github.com/kazunyanya/pi-smartmeter.git
$ cd pi-smartmeter
$ pip3 install .
```

### 3-3. サンプルコードの実行
github配布ライブラリのフォルダにはサンプルコード sample.py が入っています  
実行前に以下の部分をviエディタ等で３か所編集を行います  

使用しているWiSUNデバイスの行にのみコメントアウトを外します  
```
 動作設定 - 使用するデバイスのみコメントアウトを外す
DEVICE = "BP35A3"
# DEVICE = "BP35C0"
```

スマートメータ接続認証IDとパスワードを設定します  
この情報は電力会社から郵送される書類に入っているものを設定してください    
```
# Bルート認証ID
ID_WISUN  = "00000000000000000000000000000000"
# Bルート認証パスワード
PWD_WISUN = "SSSSSSSSSSSS"
```

サンプルコードの修正が終わったらテストのため実行してみます  
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
{以降繰り返し}
```

## ４．Azure IoT central
本章ではAzure IoT centralを利用するための登録を行います  

### 4-1. Azure IoTデバイスの作成
Azure IoT centralの画面にてデバイス作成を行います  
画面上部にある[+作成]ボタンを押下します  
![azure01](images/azure01.png "azure01") 

デバイス作成画面となる  
デバイス名は任意の文字列を入力  
今回は新規デバイスであるため「デバイステンプレート」項目は未割り当てを行います  
入力が終わったら[作成]ボタンを押下します  
![azure02](images/azure02.png "azure02")

作成が成功するとリスト上に作成したデバイス名が表示されるようになる  
次に作成したデバイス名のリンクを開く   
![azure03](images/azure03.png "azure03")

デバイス情報のページが開きます  
まだデバイスとの接続が行われていないのでデータは空欄のままである   
ここで画面上部の[接続]ボタンを押下します  
![azure04](images/azure04.png "azure04") 

デバイス接続情報が表示されるのでメモしておきます  
例：  
```
ID スコープ: 0ne005EC119
デバイス ID: ac7hs9q2re
認証の種類: SAS  
主キー: bnRdgAa+3FsFqmJCoNXZN9yfjwqIlo/eUNMaWOLg8Og=
セカンダリ キー: cvo2+upGUMvtYXh41wMIDcWFUSRSm7j2NJKDJxMwJWI=
```

![azure05](images/azure05.png "azure05") 

### 4-2. Azure IoT SDKのインストール
Azure IoT Centralの登録が終わったら Raspberry Piに SDKをインストールします  
今回はpython3を使用使用しているので python版SDKをダウンロードします  
```
$ git clone https://github.com/Azure/azure-iot-sdk-python
```

ダウンロードしたSDKをインストールする  
```
$ pip3 install azure-iot-device
```

### 4-3. Azrure IoT centralとの接続確認
AzureクラウドとRasperry Piの設定が正しいか確認するため簡単なテストアプリを動作します  
今回は公開したリポジトリからazure-cent-sample.py のサンプルコードを実行します


実行する前にソースコードを編集し認証データをセットします

```
以下の{}部分を書き換えます  
# Azure
id_scope = "{ID スコープ}"
registration_id = "{デバイス ID}"
symmetric_key = "{主キー}"
```

#### サンプルコードの実行
サンプルコードを実行を行うと次のようなログが出力されます  
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
前項でデバイス登録した Azureクラウドを開くとテレメトリデータが入っていれば正常にデータ送信されています  
![azure10](images/azure10.png "azure10") 

## ５．スマートメータアプリの実行とIoT デバイス登録
### 5-1. スマートメータアプリの実行
今回は公開したリポジトリからwisun_smartmeter_azure.py のサンプルコードを実行します

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

### 5-2. Azure IoT Central上でデバイス登録
Raspberry側からAzure IoT Centralへデータ送信ができるようになったら Azureクラウド上でデバイス登録を行います  
Azure IoT Central画面上で前項で作成したデバイスを開きます  
![azure10](images/azure10.png "azure10") 

デバイスを開くと Raspberry Piが送信したデータが表示されているはずです

![azure11](images/azure11.png "azure11") 

画面上部にある「テンプレートの管理」から「テンプレートの自動作成」を選択します  
![azure12](images/azure12.png "azure12") 

Azure IoT Centralへ送信したデータからテンプレートが自動作成されました  
この画面上で緑枠の部分の項目を編集し[保存]ボタンを押下します  
```
積算電力(W) - sekisan
瞬間電力(W) - denryoku
R相(A) - R
T相(A) - T
```
![azure13](images/azure13.png "azure13") 

テンプレートの修正/保存が終わったらテンプレートを公開します  
公開することでAzrure IoT Central上でデータが扱えるようになります  
![azure14](images/azure14.png "azure14") 

### 5-3. データの可視化
前項で登録したテンプレートを用いて可視化を行います  
デバイス画面を開くとAzrure IoT Centralに保存されたスマートメータのテレメトリ情報が可視化されます  
![azure15](images/azure15.png "azure15") 

## ６．Blobストレージへのエクスポート
スマートメータ情報がAzrure IoT Centralに取り込めるようになったらテレメトリ情報をストレージに保存します  
### 6-1. Blobストレージの作成

Azure ホームからストレージアカウントを作成します  
例： azstorege1213  
![azure20](images/azure20.png "azure20") 

ストレージアカウントが作成できたら認証情報を取得しメモしておきます  
例：
```
azstorege1213 | アクセス キー
key1
 キー : sKL5KQ3KXzQOjmfTbMtW//pzWRUfYdVT66Z+GDKOr4MnPQngxWrEKeRMz6OukBmaenqu8kDBNy8b+AStVPFlFw==
 接続文字列: DefaultEndpointsProtocol=https;AccountName=azstorege1213;AccountKey=sKL5KQ3KXzQOjmfTbMtW//pzWRUfYdVT66Z+GDKOr4MnPQngxWrEKeRMz6OukBmaenqu8kDBNy8b+AStVPFlFw==;EndpointSuffix=core.windows.net
```
![azure24](images/azure24.png "azure24") 

次にblobストレージのコンテナを作成します  
前項で作成したblobストレージを開き「新しいコンテナ」を押下し名前を付けます  
例： cont1213  
![azure22](images/azure22.png "azure22") 

### 6-2. エクスポート設定
保存するblobストレージの準備ができたら IoT Centralからエクスポート設定を行います  
左側のリストから「データのエクスポート」を選択し、名前を付けます  
エクスポートするデータの種類は「テレメトリ」を選択  
宛先はまた登録していませんので「新しく作成」を押下します  
![azure25](images/azure25.png "azure25") 

新しい宛先ダイアログが開きますので次のように設定し「作成」を押下します  
```
宛先：任意(例：export1213)
ターゲットの種類：Azure Blob Storage
接続文字列： (ストレージアカウント作成時にメモした文字列)
コンテナ： (前項で作成したコンテナ 例：cont1213)
```
![azure26](images/azure26.png "azure26") 

宛先が登録されましたので次はデータ変換を登録します  
![azure27](images/azure27.png "azure27") 

データ変換の設定画面が表示されます  
まず１．の項目でデバイス名を指定  
２．の変換クエリを次ののものに置き換え  
入力が終わったら[保存]を押下して終了します  
```
# ここで指定した変換クエリを使用して、エクスポートされた各メッセージを
# 別の形式に変更します。次の例の使用を開始できます。
# 言語の詳細については、ドキュメントを参照してください: 
# https://aka.ms/dataexporttransformation
# 以下に、'RangeOfMotion' という名前の機能の値を検索して割り当てるサンプル クエリを示します'
# import 'iotc' as iotc;
# { RangeOfMotion: .telemetry | iotc::find(.name == 'RangeOfMotion').value }
import "iotc" as iotc;
# ここで指定した変換クエリを使用して、エクスポートされた各メッセージを
# 別の形式に変更します。次の例の使用を開始できます。
# 言語の詳細については、ドキュメントを参照してください: 
# https://aka.ms/dataexporttransformation
# 以下に、'RangeOfMotion' という名前の機能の値を検索して割り当てるサンプル クエリを示します'
# import 'iotc' as iotc;
# { RangeOfMotion: .telemetry | iotc::find(.name == 'RangeOfMotion').value }
import "iotc" as iotc;
{
    schema: "default@v1",
    applicationId: .applicationId,
    deviceId: .device.id,
    messageSource: .messageSource,
    enqueuedTime: .enqueuedTime | split(".")[0],
    sekisan: .telemetry | iotc::find(.name == "sekisan").value,
    denryoku: .telemetry | iotc::find(.name == "denryoku").value,
    module: .module
}

```

![azure28](images/azure28.png "azure28") 

エクスポート登録が終了しテレメトリデータがストレージに保存されるとエクスポートの状態が「正常」となります  
![azure29](images/azure29.png "azure29") 

エクスポートが正常に行われるようになったらコンテナを開きます  
![azure30](images/azure30.png "azure30") 

コンテナを開くとテレメトリデータが入ったフォルダが表示されるようになります    
![azure31](images/azure31.png "azure31") 

### 6-3. Blobストレージのエクスポート

![azure31](images/azure31.png "azure31") 
![azure32](images/azure32.png "azure32") 
![azure33](images/azure33.png "azure33") 
![azure34](images/azure34.png "azure34") 
![azure35](images/azure35.png "azure35") 
![azure36](images/azure36.png "azure36") 
![azure37](images/azure37.png "azure37") 
![azure38](images/azure38.png "azure38") 
![azure39](images/azure39.png "azure39") 
![azure40](images/azure40.png "azure40") 
![azure41](images/azure41.png "azure41") 
![azure42](images/azure42.png "azure42") 
