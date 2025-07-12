import RPi.GPIO as GPIO
import requests
import time
from header import make_request_header, token, secret, base_url

# GPIO の設定
BUTTON_PIN = 21  # ボタンが接続されているGPIOピン番号
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

deviceId = "ECE9EE43A387"

def send_command(command_str):
    """デバイスに対して制御コマンドを送信"""
    headers = make_request_header(token, secret)
    devices_url = base_url + "/v1.1/devices/" + deviceId + "/commands"
    data = {
        "commandType": "command",
        "command": command_str,
    }

    try:
        res = requests.post(devices_url, headers=headers, json=data)
        res.raise_for_status()
        print(f"Command '{command_str}' sent successfully: {res.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    print("Waiting for toggle switch...")
    prev_input = GPIO.input(BUTTON_PIN)
    last_sent_time = 0  # 最後にコマンドを送った時間（初期値0）
    cooldown = 5  # クールダウン時間（秒）

    try:
        while True:
            current_input = GPIO.input(BUTTON_PIN)
            now = time.time()

            if current_input != prev_input:
                # 状態が変化したとき
                if now - last_sent_time >= cooldown:
                    if not prev_input and current_input:
                        # OFF → ON
                        print("Switch toggled ON! Sending 'press' command...")
                        send_command("press")
                        last_sent_time = now
                    elif prev_input and not current_input:
                        # ON → OFF
                        print("Switch toggled OFF! Sending 'release' command...")
                        send_command("press")
                        last_sent_time = now
                else:
                    print("Switch toggled, but still in cooldown period. Ignored.")

                prev_input = current_input

            time.sleep(0.05)  # チャタリング防止

    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
