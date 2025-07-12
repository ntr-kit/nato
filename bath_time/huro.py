from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
import threading
import time
import datetime
import RPi.GPIO as GPIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

BUTTON_PIN = 26
LED_PIN = 13

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

state = '空いてます'
occupied_time_start = None
occupied_duration = 0
timer_running = False
history = []
MAX_HISTORY_LENGTH = 5

def monitor_button():
    global state, occupied_time_start, occupied_duration, timer_running, history
    last_state = GPIO.input(BUTTON_PIN)
    while True:
        current_state = GPIO.input(BUTTON_PIN)
        if current_state == GPIO.LOW:
            if state != '入ってます':
                state = '入ってます'
                occupied_time_start = time.time()
                timer_running = True
                threading.Thread(target=update_timer).start()
                GPIO.output(LED_PIN, True)
            socketio.emit('state_update', {'state': state})
        elif current_state == GPIO.HIGH:
            if state != '空いてます':
                state = '空いてます'
                timer_running = False
                if occupied_time_start:
                    occupied_duration = time.time() - occupied_time_start
                    if len(history) >= MAX_HISTORY_LENGTH:
                        history.pop(0)
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    history.append({'duration': occupied_duration, 'timestamp': timestamp})
                    occupied_time_start = None
                    socketio.emit('duration_update', {'duration': occupied_duration})
                GPIO.output(LED_PIN, False)
            socketio.emit('state_update', {'state': state})
        time.sleep(0.1)

def update_timer():
    global occupied_duration
    while True:
        if timer_running:
            elapsed_time = time.time() - occupied_time_start
            occupied_duration = elapsed_time
            socketio.emit('timer_update', {'elapsed_time': elapsed_time})
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/state')
def get_state():
    return jsonify({'state': state})

@app.route('/duration')
def get_duration():
    return jsonify({'duration': occupied_duration})

@app.route('/history')
def get_history():
    return jsonify(history)

if __name__ == '__main__':
    thread = threading.Thread(target=monitor_button)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True, debug=True)
