#!/usr/bin/python
#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import subprocess

PIN = 21
CMD = "python3 /home/pi/switchbot/bot_press.py" # 実行するプログラム

GPIO.setmode(GPIO.BCM)

# プルアップ抵抗を有効にする
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

p = None

print("start")
try:
    while True:
        # 立ち下がりエッジが検出されるまで待機する
        GPIO.wait_for_edge(PIN, GPIO.FALLING)
        if p is None:
            # プログラムを実行する
            p = subprocess.call(CMD, shell=True)
            print("pushed")

        else:
            # プログラムを終了する
            #p.kill()
            p = None
except KeyboardInterrupt:
    # Ctrl-C
    GPIO.cleanup()
