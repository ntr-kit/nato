#!/usr/bin/python
# -*- coding: utf-8 -*-
import webiopi
import subprocess

CMD = "sudo python3 /home/pi/my_webiopi/python/noise.py"
@webiopi.macro
def start():
    subprocess.call(CMD, shell=True)
    print("run_python")


