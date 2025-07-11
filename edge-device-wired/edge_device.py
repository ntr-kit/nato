from datetime import datetime
from zoneinfo import ZoneInfo
import json
import time
import requests
import math
import ADS1263
from datetime import datetime
import RPi.GPIO as GPIO
import serial
import uuid
import zlib
import base64
import os
import logging
from logging.handlers import TimedRotatingFileHandler

jst = ZoneInfo("Asia/Tokyo")
REF = 5.08
UPDATE_INTERVAL = 0.02  # 更新間隔
DURATION = 5  # データ収集時間
calc_value = 5
serial_port = ""
own_address = 0
own_channel = 0
target_address = 0
target_channel = 0
cts = []

# ロガーの初期化
logger = logging.getLogger(__name__)

def setup_logging(log_dir, base_filename, backup_count=7):
    with open("config.json", "r", encoding="utf-8") as file:
        config_json = json.load(file)

    """ロギングの設定"""
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, base_filename)

    handler = TimedRotatingFileHandler(
        filename=log_filename, when="midnight", backupCount=backup_count
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    if config_json.get("Log") == "True":
        logger.setLevel(logging.INFO)
    else:
        logging.disable(logging.CRITICAL)

    logger.info("Logger setup complete.")


def zip_str(text: str) -> str:
    original_data_bytes = text.encode('utf-8')
    compressed_data = zlib.compress(original_data_bytes)
    return  base64.b64encode(compressed_data).decode('utf-8')


def test_server_connection(health_check_url):
    """サーバーへの接続テストを行う"""
    while True:
        try:
            response = requests.get(health_check_url)
            if response.status_code == 200:
                print("Successfully connected to the server.")
                return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")

        print("Retrying in 10 seconds...")
        time.sleep(10)


def calculate_current(data, ct):
    if ct == "CTL 24 CLS":
        calc_value = 5
    min_val = min(data)
    max_val = max(data)
    data_value = (((max_val - min_val)) / 2  * 1000) / math.sqrt(2) / calc_value
    return data_value


def create_device_data_to_json(config_json):
    global channelList, cts
    """取得したデバイスデータをJsonにする"""

    data = {i: [] for i in channelList}
    end_time = time.time() + DURATION    
    print("get channel: %s" % channelList)
    while time.time() < end_time:
        current_time = time.time()
        ADC_Value = ADC.ADS1263_GetAll(channelList)  # get ADC1 value
        for i in channelList:
            if ADC_Value[i] >> 31 == 1:
                data[i].append(-(REF * 2 - ADC_Value[i] * REF / 0x80000000))
            else:
                data[i].append(ADC_Value[i] * REF / 0x7fffffff)

        time.sleep(UPDATE_INTERVAL)  # Wait for the next update
        
    jsn = {"v": []}
    for i in range(len(channelList)):
        if len(cts)-1 < i:
            cts.append(config_json["devices"][i]["ct"])
        jsn["v"].append(round(calculate_current(data[i], cts[i]), 2))
    return jsn


def send_device_data(server_url, config_json):
    global serial_port, own_address, own_channel, target_address, target_channel, cts
    """データを定期的に送信"""
    with serial.Serial(serial_port, 9600, timeout=None) as ser:
        isRetry = False
        while True:
            try:
                if not isRetry:
                    devices_data_json = create_device_data_to_json(config_json)

                    payload = bytes()
                    isMeasureStart = False
                    while True:
                        if ser.in_waiting > 0:
                            payload = payload + ser.read(ser.in_waiting)
                        elif ser.in_waiting == 0 and len(payload) != 0:
                            data = payload.decode("utf-8", "ignore")
                            logger.info(f"Receive start message payload:{payload}")
                            if data == "MEASURE START":
                                isMeasureStart = True
                                break
                            else:
                                logger.info(f"Receive error")
                                payload = bytes()
                        time.sleep(0.1)
                while True:
                    if ser.out_waiting == 0:
                        break
                send_start = time.time()

                t_addr_H = target_address >> 8
                t_addr_L = target_address & 0xFF
                payload = bytes([t_addr_H, t_addr_L, target_channel])

                unique_string = str(uuid.uuid4())
                # Send a specific hardcoded text string
                send_text = unique_string + ":begin:" + zip_str(json.dumps(devices_data_json))

                isEndOnly = True
                if len(send_text) > 198:
                    payload += send_text[0:197].encode("utf-8")

                    ser.write(payload)  # データをバイト列にエンコードして送信
                    ser.flush()
                    logger.info(f"Send1 data payload:{payload}")
                    isEndOnly = False

                while True:
                    while True:
                        if ser.out_waiting == 0:
                            break

                    if not isEndOnly:
                        send_text = send_text[197:]
                    payload = bytes([t_addr_H, t_addr_L, target_channel])
                    if len(unique_string + ":middle:" + send_text) > 198 and not isEndOnly:
                        send_text = unique_string + ":middle:" + send_text
                        payload += send_text[0:197].encode("utf-8")
                        ser.write(payload)  # データをバイト列にエンコードして送信
                        ser.flush()
                        logger.info(f"Send2 data payload:{payload}")
                        time.sleep(1.5)
                    else:
                        if not isEndOnly:
                            send_text = (unique_string + ":end" + own_address + "_" + own_channel + ":" + send_text)
                        else :
                            send_text = unique_string + ":end" + own_address + "_" + own_channel + ":" + zip_str(json.dumps(devices_data_json))
                        payload += send_text.encode("utf-8")
                        ser.write(payload)  # データをバイト列にエンコードして送信
                        ser.flush()
                        logger.info(f"Send end data json:{devices_data_json}")
                        logger.info(f"Send3 data payload:{payload}")

                        payload = bytes()

                        while True:
                            if ser.in_waiting > 0:
                                payload = payload + ser.read(ser.in_waiting)
                            elif ser.in_waiting == 0 and len(payload) != 0:
                                data = payload.decode("utf-8", "ignore")
                                logger.info(f"Receive message payload:{payload}")
                                sp = data.split(":")
                                if len(sp) > 1 and sp[0] == unique_string and sp[1].startswith("OK"):
                                    print("Receive ", sp[1])
                                    logger.info(f"Receive {sp[1]}")
                                    isRetry = False
                                    break
                                isRetry = not isRetry
                                if len(sp) > 1 and sp[0] == unique_string and sp[1].startswith("NG"):
                                    print("Receive ", sp[1])
                                    logger.error(f"Receive {sp[1]}")
                                    break
                                logger.error(f"Receive Param Error {data} {len(sp)} {unique_string}")
                                break
                            if ser.in_waiting == 0 and time.time() - send_start > 4:
                                print("Receive Timeout")
                                logger.error("Receive Timeout")
                                isRetry = not isRetry
                                break

                            # Add a small delay to prevent tight loop
                            time.sleep(0.1)

                        break

            except requests.RequestException as e:
                print(f"Error fetching data: {e}")
                return None


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, "log")
    log_filename = os.path.splitext(os.path.basename(__file__))[0]
    ser = None

    setup_logging(log_dir, log_filename)
    print("base edge Run!!!")
    with open("config.json", "r", encoding="utf-8") as file:
        config_json = json.load(file)

    server_url = f"http://{config_json.get('send_server_url')}:8000"

    ADC = ADS1263.ADS1263()

    if (ADC.ADS1263_init_ADC1('ADS1263_400SPS') == -1):
        exit()
    ADC.ADS1263_SetMode(0) # 0 is singleChannel, 1 is diffChannel

    M0_pin = config_json.get('M0_pin')
    M1_pin = config_json.get('M1_pin')

    serial_port = config_json.get('serial_port')
    own_address = config_json.get('own_address')
    own_channel = config_json.get('own_channel')
    target_address = int(config_json.get('target_address'))
    target_channel = int(config_json.get('target_channel'))
    channelList = []
    for i in [0,1,2,3,4,5,6,7,8,9]:
        if config_json["devices"][i]["ct"] != "-":
            channelList.append(i)

    # set output
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(M0_pin, GPIO.OUT)
    GPIO.setup(M1_pin, GPIO.OUT)

    # set M0=high,M1=high
    GPIO.output(M0_pin, False)
    GPIO.output(M1_pin, False)

    send_device_data(server_url, config_json)
