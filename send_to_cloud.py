import paho.mqtt.client as mqtt
import time
import json
import socket

ip_local = socket.gethostbyname(socket.gethostname())
print(f'IP Local: {ip_local}')


class Send_to_cloud_Mqtt:

    def __init__(self):
        self.init_MQTT()

    def connect_MQTT(self):
        if (self.client.connected_flag == False):
            try:
                #self.client.connect("broker.hivemq.com", 1883, 60)
                self.client.connect("192.168.15.61", 1883, 60)
                self.client.loop_start()

            except:
                print("Fail connect to Cloud ")
                self.connect_MQTT()

    def init_MQTT(self):
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connected_flag = False

        #self.client.username_pw_set(username="tecnologia", password="128Parsecs!")
        #self.client.connect("gwqa.revolog.com.br", 1884, 60)
        self.client.username_pw_set(
            username="tecnologia", password="128Parsecs!")

        self.connect_MQTT()
        # try:
        #self.client.connect("gwqa.revolog.com.br", 1884, 60)
        # self.client.loop_start()
        # except:
        # self.client.loop_start()
        #print("Fail connect to Cloud ")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag = True
            print("Connected to Cloud ")
        else:
            print("Bad connection Returned code=", rc)
            self.init_MQTT()

    def on_disconnect(self, client, userdata, rc):
        print("disconnecting reason  " + str(rc))
        self.client.connected_flag = False
        client.loop_stop()

    # def send_message_to_cloud(self,client,position,security_dist,tags_data):
    def send_message_to_cloud(self, client, plate):
        json_data = {}
        json_data["plate"] = plate
        json_string = json.dumps(json_data)
        print(json_string)
        print("\n")
        if (self.client.connected_flag == True):
            self.client.publish("gateway/cba/status", json_string)

        del json_string
        json_data.clear()
