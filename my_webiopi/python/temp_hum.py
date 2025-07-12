#!/usr/bin/python
import Adafruit_DHT

sensor = Adafruit_DHT.DHT22

pin = 23

def get_data1():
    humidity, temperature = Adafruit_DHT.read_retry(sensor,pin)

    temp = round(temperature,1)

    return temp

def get_data2():
    humidity, temperature = Adafruit_DHT.read_retry(sensor,pin)

    hum = round(humidity,1)

    return hum

