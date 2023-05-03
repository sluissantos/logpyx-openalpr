from mqtt_interface import Mqtt_Interface
import threading
import time
import json
import os

class Send_to_cloud_Mqtt:

    def __init__(self):
        self.send_mqtt = Mqtt_Interface()
        self.send_mqtt.connect()
        while self.send_mqtt.connect() is not True:
            self.send_mqtt.connect()

    def publish (self, message):
        self.send_mqtt.send_message_to_cloud(message)
        
def init ():
    test = Send_to_cloud_Mqtt()

if __name__ == '__main__':
    p1 = threading.Thread(target=init, args=())
    p1.start()