import paho.mqtt.client as mqtt
import time
import json
import os
'''
# variáveis globais atribúidas à partir das variáveis de ambiente inicializadas no sistema.
ip_mqtt = "gwqa.revolog.com.br"
port_mqtt = "1884"
username_mqtt = "tecnologia"
password_mqtt = "128Parsecs!"
publish_topic = "aperam/plate"
publish_topic_status = "aperam/status"

'''
ip_mqtt = os.getenv("IP_MQTT")
port_mqtt = os.getenv("PORT_MQTT")
username_mqtt = os.getenv("USER_NAME_MQTT")
password_mqtt = os.getenv("PASSWORD_MQTT")
publish_topic = os.getenv("PUBLISH_TOPIC")
publish_topic_status = os.getenv("PUBLISH_TOPIC_STATUS")

client = mqtt.Client()

# Define configurações iniciais
def setup():
    print('ip=', ip_mqtt)
    print('port=', port_mqtt)
    print('user=', username_mqtt)
    print('pass=', password_mqtt)
    print('publish=', publish_topic)
    print('publish_status=', publish_topic_status)
    client.username_pw_set(username_mqtt, password_mqtt)
    client.connected_flag = False
    client.bad_connection_flag = False
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    connect()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully.")
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

def send_message_plate(plate):
    json_data = {}
    json_data["plate"] = plate
    json_string = json.dumps(json_data)
    print(json_string)
    print("\n")
    try:
        if (client.connected_flag == True):
            result = client.publish(publish_topic, json_string, 2)
    except:
        print("Failed to publish message.")
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

def publish_plate(plate):
    setup()
    send_message_plate(plate)
    cleanup()
    
def publish_status(source, status):
    setup()
    send_message_status(source, status)
    cleanup()

if __name__ == '__main__':
    publish_plate('test')
