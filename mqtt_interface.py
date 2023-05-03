import paho.mqtt.client as mqtt
import time
import json
import os

class Mqtt_Interface:

    def __init__(self):
        self.ip_mqtt = os.getenv("IP_MQTT")
        self.port_mqtt = os.getenv("PORT_MQTT")
        self.username_mqtt = os.getenv("USER_NAME_MQTT")
        self.password_mqtt = os.getenv("PASSWORD_MQTT")
        self.publish_topic = os.getenv("PUBLISH_TOPIC")

        print('ip=', self.ip_mqtt)
        print('port=', self.port_mqtt)
        print('user=', self.username_mqtt)
        print('pass=', self.password_mqtt)
        print('publish=', self.publish_topic)
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username_mqtt, self.password_mqtt)
        self.client.connected_flag = False
        self.client.bad_connection_flag = False
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully.")
            client.connected_flag = True
        else:
            print("Connection failed with code %d." % rc)
            client.bad_connection_flag = True

    def on_disconnect(self, client, userdata, rc):
        client.connected_flag = False
        client.bad_connection_flag = True

    def connect(self):
        while True:
            try:
                self.client.connect(self.ip_mqtt, int(self.port_mqtt))
                self.client.loop_start()
                while not self.client.connected_flag and not self.client.bad_connection_flag:
                    time.sleep(1)

                if self.client.connected_flag:
                    return True

            except:
                self.client.bad_connection_flag = True

            self.client.disconnect()
            print("Connection failed. Retrying in 5 seconds.")
            time.sleep(5)

    def send_message_to_cloud(self, plate):
        json_data = {}
        json_data["plate"] = plate
        json_string = json.dumps(json_data)
        print(json_string)
        print("\n")
        if (self.client.connected_flag == True):
            result = self.client.publish(self.publish_topic, json_string, 1)
            #print('result[0]=', result[0])
            #print('resutl[1]=', result[1])
        del json_string
        json_data.clear()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == '__main__':
    test = Mqtt_Interface()
    test.connect()
    if test.connect():
        test.send_message_to_cloud('teste')
        test.send_message_to_cloud('teste')
        print('test.connect()=', test.connect())
        print("MQTT client connected successfully.")
    else:
        print("MQTT client failed to connect.")

    test.disconnect()
