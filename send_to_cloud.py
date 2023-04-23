import paho.mqtt.client as mqtt
import time
import json
import os

ip_mqtt = os.getenv("IP_MQTT")
port_mqtt = os.getenv("PORT_MQTT")
user_name_mqtt = os.getenv("USER_NAME_MQTT")
password_mqtt = os.getenv("PASSWORD_MQTT")
publish_topic = os.getenv("PUBLISH_TOPIC")

print('ip=', ip_mqtt)
print('port=', port_mqtt)
print('user=', user_name_mqtt)
print('pass=', password_mqtt)
print('pub=', publish_topic)


class Send_to_cloud_Mqtt:

    def __init__(self):
        self.init_MQTT()
        self.connect_MQTT()

    def connect_MQTT(self):
        if (self.client.connected_flag == False):
            try:
                self.client.connect(ip_mqtt, int(port_mqtt), 60)
                self.client.loop_start()

            except:
                print("Fail connect to Cloud ")
                self.connect_MQTT()

    def init_MQTT(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connected_flag = False
        self.client.connect(ip_mqtt, int(port_mqtt), 60)
        self.client.username_pw_set(username=user_name_mqtt, password=password_mqtt)
        self.connect_MQTT()


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

    def send_message_to_cloud(self, client, plate):
        json_data = {}
        json_data["plate"] = plate
        json_string = json.dumps(json_data)
        print(json_string)
        print("\n")
        if (self.client.connected_flag == True):
            self.client.publish(publish_topic, json_string)
        del json_string
        json_data.clear()
