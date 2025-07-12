import RPi.GPIO as GPIO
import time

# GPIOの設定
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

BUTTON_PIN = 19  # タッチセンサーのGPIOピン
LED_PIN = 13     # LEDのGPIOピン

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

led_state = False  # LEDの初期状態（消灯）

def button_callback(channel):
    global led_state
    led_state = not led_state  # LEDの状態を反転
    GPIO.output(LED_PIN, led_state)  # LEDの状態を更新
    if led_state:
        print("LED点灯")
    else:
        print("LED消灯")

# タッチセンサーのイベントリスナーを設定
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    print("タッチセンサーを待機中...")
    while True:
        time.sleep(1)  # メインループは1秒待機
except KeyboardInterrupt:
    print("プログラムを終了します")
finally:
    GPIO.cleanup()  # GPIOのクリーンアップ
