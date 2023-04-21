from binascii import hexlify, a2b_base64, unhexlify
import paho.mqtt.client as mqtt
import time
import json


class Mqtt_Interface:

    def __init__(self):

        self.time_reference_variable = time.time()

        self.init_MQTT()

    def init_MQTT(self):
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(username="root", password="128Parsecs!")
        self.client.connect("localhost", 1883, 60)
        self.client.subscribe("dwm/node/+/uplink/data")
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.connected_flag = True
            subs = "dwm/node/+/uplink/data"
            self.client.subscribe(subs)

            print("Connected OK Gateway: ")
            print(subs)
        else:
            print("Bad connection Returned code=", rc)

    def process_message(self, message):
        json_message_parse = json.loads(message.payload.decode("utf-8"))
    '''        # print(json_message_parse['data'])

        payload_recv = hexlify(a2b_base64(json_message_parse["data"]))
        tag_addr = int.from_bytes(unhexlify(message.topic[9:13]), 'big')
        #print("tag addr %04x, payload %s" % (tag_addr,payload_recv))
        ret = process_data().data_received(tag_addr, payload_recv)

        if (ret['ret_type'] == 1):
            # for mobile_tag in ret['all_mobile_tags']: For all mobile tags
            #    print("send mobile tag %04x, data: %s" % (mobile_tag,ret['message']))
            #    self.send_message_to_tag(mobile_tag, ret['message'])

            # only one tag
            #print("send mobile tag %04x, data: %s" % (ret['mobile_tag'],hexlify(a2b_base64(ret['message']))))
            self.send_message_to_tag(ret['mobile_tag'], ret['message'])
        elif (ret['ret_type'] == 2):
            self.time_reference_variable = time.time()
    '''

    def send_message_to_tag(self, tag_addr, message_to_tag):
        json_data = "{ \"data\": \"%s\",\"overwrite\":false}" % message_to_tag
        self.client.publish(
            "dwm/node/"+str(format(tag_addr, '04x'))+"/downlink/data", json_data)

    def on_message(self, client, userdata, message):
        self.process_message(message)
    