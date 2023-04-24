import os

ip_mqtt = os.getenv("IP_MQTT")
port_mqtt = os.getenv("PORT_MQTT")

print('ip_mqtt=', ip_mqtt)
print('type=', type(ip_mqtt))

print('port_mqtt=', port_mqtt)
print('type=', type(port_mqtt))