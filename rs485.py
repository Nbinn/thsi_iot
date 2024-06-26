print("Sensors and Actuators")

import time
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import json


MQTT_SERVER = "demo.thingsboard.io"
MQTT_PORT = 1883
MQTT_ACCESS_TOKEN = "MNUrel9MvIV2iXce3LA1"
# MQTT_PASSWORD = ""
# MQTT_TOPIC_PUB_TEMP = MQTT_USERNAME + "/feeds/V1/mois/"
MQTT_TOPIC_PUB = "v1/devices/me/telemetry"
MQTT_TOPIC_SUB = "v1/devices/me/rpc/request/+"

def mqtt_connected(client, userdata, flags, rc):
    print("Connected succesfully!!")
    client.subscribe(MQTT_TOPIC_SUB)

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    #TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setRelay1":
            temp_data['relay1'] = jsonobj['params']
            # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if temp_data['relay1']:
                setDevice1(True) 
            else:
                setDevice1(False) 
        if jsonobj['method'] == "setRelay2":
            temp_data['relay2'] = jsonobj['params']
            # client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            # if temp_data['valueFAN']:
                # setDevice2(True) 
            # else:
                # setDevice2(False) 
    except:
        pass

mqttClient = mqtt.Client()
mqttClient.username_pw_set(MQTT_ACCESS_TOKEN)
mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

mqttClient.on_connect = mqtt_connected
mqttClient.on_subscribe = mqtt_subscribed
mqttClient.on_message = mqtt_recv_message

mqttClient.loop_start()

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort
    # return "/dev/ttyUSB1"

portName = getPort()
print(portName)



try:
    ser = serial.Serial(port=portName, baudrate=9600)
    print("Open successfully")
except:
    print("Can not open the port")

relay1_ON  = [2, 6, 0, 0, 0, 255, 201, 185]
relay1_OFF = [2, 6, 0, 0, 0, 0, 137, 249]

def setDevice1(state):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)
    time.sleep(1)
    print(serial_read_data(ser))

def serial_read_data(ser):
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        print(data_array)
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0

soil_temperature =[1, 3, 0, 6, 0, 1, 100, 11]
def readTemperature():
    serial_read_data(ser)
    ser.write(soil_temperature)
    time.sleep(1)
    return serial_read_data(ser)

soil_moisture = [1, 3, 0, 7, 0, 1, 53, 203]
def readMoisture():
    serial_read_data(ser)
    ser.write(soil_moisture)
    time.sleep(1)
    return serial_read_data(ser)

temp = 10
mois = 10
while True:
    print("TEST SENSOR")
    # mqttClient.publish(MQTT_TOPIC_PUB_TEMP,readTemperature())
    time.sleep(10)
    # temp = readTemperature()
    # mois = readMoisture()
    collect_data = {'temperature': temp, 'humidity': mois}
    mqttClient.publish(MQTT_TOPIC_PUB,json.dumps(collect_data))
    # time.sleep(1)