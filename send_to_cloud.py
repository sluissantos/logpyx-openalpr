import paho.mqtt.client as mqtt
import time
import json

class Send_to_cloud_Mqtt:

    def __init__(self):
        self.broker_host = 'gwqa.revolog.com.br'
        self.broker_port = 1884
        self.username = 'tecnologia'
        self.password = '128Parsecs!'
        self.publish_topic = 'aperam/plate'
        self.client = mqtt.Client()
        self.client.username_pw_set(self.username, self.password)
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
                self.client.connect(self.broker_host, self.broker_port)
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
            self.client.publish(self.publish_topic, json_string)
        del json_string
        json_data.clear()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == '__main__':
    test = Send_to_cloud_Mqtt()

    if test.connect():
        print("MQTT client connected successfully.")
    else:
        print("MQTT client failed to connect.")

    test.disconnect()
