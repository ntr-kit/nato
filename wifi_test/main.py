import ujson
import network
import uasyncio as asyncio
import time

# 設定ファイルを読み込む
with open("config.json", "r") as f:
    config = ujson.load(f)

wifi_ssid = config["WifiSsid"]
wifi_password = config["WifiPassword"]

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)

    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        print("connect status", wlan.status())
        time.sleep(1)
        pass

    print("Wi-Fi Connected:", wlan.ifconfig())


async def main():
    connect_wifi()

# 実行
asyncio.run(main())