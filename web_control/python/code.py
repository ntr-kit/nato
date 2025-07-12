#!/usr/bin/python
# -*- coding: utf-8 -*-
import webiopi
import subprocess
import Adafruit_DHT

@webiopi.macro
def run_code1():
    CMD = "sudo python3 /home/pi/my_webiopi/python/light_on.py"
    subprocess.call(CMD, shell=True)

@webiopi.macro
def run_code2():
    CMD = "sudo python3 /home/pi/my_webiopi/python/fan_on.py"
    subprocess.call(CMD, shell=True)

@webiopi.macro
def run_code3():
    CMD = "sudo python3 /home/pi/my_webiopi/python/bot_press.py"
    subprocess.call(CMD, shell=True)

@webiopi.macro
def run_code4():
    CMD = "sudo python3 /home/pi/my_webiopi/python/TV_on.py"
    subprocess.call(CMD, shell=True)

@webiopi.macro
def run_code5():
    CMD = "sudo python3 /home/pi/my_webiopi/python/TV_volume.py"
    subprocess.call(CMD, shell=True)

@webiopi.macro
def run_code6():
    CMD = "sudo python3 /home/pi/my_webiopi/python/TV_volume2.py"
    subprocess.call(CMD, shell=True)
    
@webiopi.macro
def run_code7():
    CMD = "sudo python3 /home/pi/my_webiopi/python/TV_channel.py"
    subprocess.call(CMD, shell=True)

@webiopi.macro
def run_code8():
    CMD = "sudo python3 /home/pi/my_webiopi/python/TV_channel2.py"
    subprocess.call(CMD, shell=True)


SENSOR_PIN = 23  # データピン (GPIO 4)
SENSOR = Adafruit_DHT.DHT22

# WebIOPiのマクロとして関数を定義
@webiopi.macro
def getTemperature():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, SENSOR_PIN)
    return "{:.2f}".format(temperature)

@webiopi.macro
def getHumidity():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, SENSOR_PIN)
    return "{:.2f}".format(humidity)
