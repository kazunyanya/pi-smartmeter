#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pip3

import os
import time
import datetime
import json
import traceback
import logging
from azure.iot.device import ProvisioningDeviceClient
from azure.iot.device import IoTHubDeviceClient, Message

# Azure
id_scope = "0ne005EC119"
registration_id = "12sj55trtt7"
symmetric_key = "ayXDW1NEBSevaQpetY09PFu7Ts7JtE6kAG8iZ7Hp8uo="
provisioning_host = "global.azure-devices-provisioning.net"

# ログ出力
logging.basicConfig(format='<%(levelname)s>%(message)s', level=logging.INFO)

def message_received_handler(message):
    # ログ出力のみ
    print("the data in the message received was ")
    print(message.data)
    print("custom properties are")
    print(message.custom_properties)

def main():
    print("@@@@@ main() start")

    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    registration_result = provisioning_device_client.register()
    print("@@@@ regist:" + str(registration_result))

    if registration_result.status == "assigned":
        print("Will send telemetry from the provisioned device")
        # Create device client from the above result
        device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=symmetric_key,
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
        )

        # Connect the client.
        print("@@@@@ connect IoT central")
        device_client.connect()
        device_client.on_message_received = message_received_handler

        print("@@@@@ connected")
        telemetry = {}
        for i in range(1, 100):
            telemetry.update({'TEST' : float(i * 1.01)})
            telemetry["MsgId"] = i
            print("@@@@@ send" + str(telemetry))
            data = json.dumps(telemetry)
            device_client.send_message(data)

            time.sleep(3)

        # finally, disconnect
        device_client.disconnect()
    else:
        print("Can not send telemetry from the provisioned device")

if __name__ == '__main__':
    main()

