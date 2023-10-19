import paho.mqtt.client as mqtt
import time
import json
import os

ip_mqtt = os.getenv("IP_MQTT")
if ip_mqtt is None or ip_mqtt.strip() == "":
    ip_mqtt = "10.50.239.100"

port_mqtt = os.getenv("PORT_MQTT")
if port_mqtt is None or port_mqtt.strip() == "":
    port_mqtt = 1883

username_mqtt = os.getenv("USER_NAME_MQTT")
if username_mqtt is None or username_mqtt.strip() == "":
    username_mqtt = "tecnologia"

password_mqtt = os.getenv("PASSWORD_MQTT")
if password_mqtt is None or password_mqtt.strip() == "":
    password_mqtt = "128Parsecs!"

publish_topic = os.getenv("PUBLISH_TOPIC")
if publish_topic is None or publish_topic.strip() == "":
    publish_topic = "aperam/plate"

publish_topic_status = os.getenv("PUBLISH_TOPIC_STATUS")
if publish_topic_status is None or publish_topic_status.strip() == "":
    publish_topic_status = "aperam/status"

print('ip=', ip_mqtt)
print('port=', port_mqtt)
print('user=', username_mqtt)
print('pass=', password_mqtt)
print('publish=', publish_topic)
print('publish_status=', publish_topic_status)

client = mqtt.Client()

# Define configurações iniciais
def setup():
    client.username_pw_set(username_mqtt, password_mqtt)
    client.connected_flag = False
    client.bad_connection_flag = False
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    connect()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        #print("Connected successfully.")
        client.connected_flag = True
    else:
        print("Connection failed with code %d." % rc)
        client.bad_connection_flag = True

def on_disconnect(client, userdata, rc):
    client.connected_flag = False
    client.bad_connection_flag = True

def connect():
    while True:
        try:
            client.connect(ip_mqtt, int(port_mqtt))
            client.loop_start()
            while not client.connected_flag and not client.bad_connection_flag:
                time.sleep(1)

            if client.connected_flag:
                return True

        except:
            client.bad_connection_flag = True
            client.disconnect()
            
        print("Connection failed. Retrying in 5 seconds.")
        time.sleep(5)

def send_message_plate(id, plate):
    json_data = {
        "id" : id,
        "plate" : plate
    }
    json_string = json.dumps(json_data)
    print(json_string)
    try:
        if client.connected_flag:
            result = client.publish(publish_topic, json_string, 2)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print("Failed to publish message.")
    except Exception as e:
        print("Failed to publish message:", str(e))
    del json_string
    json_data.clear()

def send_message_status(string_source, status):
    json_data = {
        "tmst": int(time.time()),
        "ip": string_source,
        "status": status
    }
    json_string = json.dumps(json_data)
    print(json_string)
    try:
        if client.connected_flag:
            result = client.publish(publish_topic_status, json_string, 2)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print("Failed to publish message.")
    except Exception as e:
        print("Failed to publish message:", str(e))
    del json_string
    json_data.clear()

def cleanup():
    client.loop_stop()
    client.disconnect()

def publish_plate(id, plate):
    setup()
    if(plate is not None):
        send_message_plate(id, plate)
    cleanup()
    
def publish_status(source, status):
    setup()
    send_message_status(source, status)
    cleanup()

def reconnect():
    if not client.is_connected():
        setup()
    time.sleep(5) 

if __name__ == '__main__':
    publish_plate('test','test')