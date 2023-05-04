from mqtt_interface import Mqtt_Interface
import threading
import time
import json
import os

class Send_to_cloud_Mqtt:

    def __init__(self):
        mqtt_init = Mqtt_Interface()
        mqtt_init.connect()
        while mqtt_init.connect() is not True:
            mqtt_init.connect()
        s

def create_mqtt ():
    send_mqtt = Mqtt_Interface()
    p1 = threading.Thread(target=send_mqtt)
    p1.start()

if __name__ == '__main__':
    test = Send_to_cloud_Mqtt()
    p1 = threading.Thread(target=send, args=())
    p1.start()