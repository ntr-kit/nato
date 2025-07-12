import RPi.GPIO as GPIO
from flask import Flask, jsonify, render_template_string
from flask_socketio import SocketIO
import threading
import time
import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

BUTTON_PIN = 26  # タッチセンサーのGPIOピン
LED_PIN = 13     # LEDのGPIOピン

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

state = '空いてます'
occupied_time_start = None
occupied_duration = 0
timer_running = False
history = []
MAX_HISTORY_LENGTH = 5

# LEDの状態を追跡するための変数
led_state = False

def monitor_button():
    global state, occupied_time_start, occupied_duration, timer_running, history, led_state
    last_state = GPIO.input(BUTTON_PIN)

    while True:
        current_state = GPIO.input(BUTTON_PIN)

        # ボタンが押されている間、「入っています」
        if current_state == GPIO.LOW:  # ボタンが押されている時
            if state != '入ってます':
                state = '入ってます'
                occupied_time_start = time.time()
                timer_running = True
                threading.Thread(target=update_timer).start()
                GPIO.output(LED_PIN, True)  # LEDを点灯
            socketio.emit('state_update', {'state': state})

        # ボタンが離されている間、「空いています」
        elif current_state == GPIO.HIGH:  # ボタンが離されている時
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
                GPIO.output(LED_PIN, False)  # LEDを消灯
            socketio.emit('state_update', {'state': state})

        last_state = current_state
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
    return render_template_string('''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ボタンの状態</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: background-color 0.5s; }
        .state-text { font-size: 3em; font-weight: bold; margin: 0; }
        .duration-text { font-size: 1.5em; margin-top: 10px; color: #333; }
        .state-empty { color: green; }
        .state-occupied { color: red; }
        table { margin-top: 20px; border-collapse: collapse; width: 80%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f4f4f4; text-align: left; }
    </style>
    <script>
        const socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('state_update', function(data) {
            const stateElement = document.getElementById('state');
            stateElement.innerText = data.state;
            stateElement.className = 'state-text ' + (data.state === '入ってます' ? 'state-occupied' : 'state-empty');
            document.body.style.backgroundColor = data.state === '入ってます' ? 'lightcoral' : 'lightgreen';
        });

        socket.on('timer_update', function(data) {
            const durationElement = document.getElementById('duration');
            const elapsedTime = data.elapsed_time;
            const mins = Math.floor(elapsedTime / 60);
            const secs = Math.floor(elapsedTime % 60);
            durationElement.innerText = `経過時間: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        });

        socket.on('duration_update', function(data) {
            const durationElement = document.getElementById('duration');
            const elapsedTime = data.duration;
            const mins = Math.floor(elapsedTime / 60);
            const secs = Math.floor(elapsedTime % 60);
            durationElement.innerText = `経過時間: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        });

        window.onload = function() {
            fetch('/state')
                .then(response => response.json())
                .then(data => {
                    const stateElement = document.getElementById('state');
                    stateElement.innerText = data.state;
                    stateElement.className = 'state-text ' + (data.state === '入ってます' ? 'state-occupied' : 'state-empty');
                    document.body.style.backgroundColor = data.state === '入ってます' ? 'lightcoral' : 'lightgreen';

                    fetch('/duration')
                        .then(response => response.json())
                        .then(durationData => {
                            const durationElement = document.getElementById('duration');
                            const elapsedTime = durationData.duration;
                            const mins = Math.floor(elapsedTime / 60);
                            const secs = Math.floor(elapsedTime % 60);
                            durationElement.innerText = `経過時間: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
                        });

                    fetch('/history')
                        .then(response => response.json())
                        .then(historyData => {
                            const tableBody = document.getElementById('history-table-body');
                            tableBody.innerHTML = '';
                            historyData.forEach((entry, index) => {
                                const row = document.createElement('tr');
                                const cell1 = document.createElement('td');
                                cell1.innerText = entry.timestamp;
                                const cell2 = document.createElement('td');
                                const mins = Math.floor(entry.duration / 60);
                                const secs = Math.floor(entry.duration % 60);
                                cell2.innerText = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
                                row.appendChild(cell1);
                                row.appendChild(cell2);
                                tableBody.appendChild(row);
                            });
                        });
                });
        }
    </script>
</head>
<body>
    <div id="state" class="state-text">状態: 空いてます</div>
    <div id="duration" class="duration-text">経過時間: 00:00</div>
    <table>
        <thead>
            <tr>
                <th>時刻</th>
                <th>経過時間</th>
            </tr>
        </thead>
        <tbody id="history-table-body">
        </tbody>
    </table>
</body>
</html>
    ''')

@app.route('/state')
def get_state():
    global state
    return jsonify({'state': state})

@app.route('/duration')
def get_duration():
    global occupied_duration
    return jsonify({'duration': occupied_duration})

@app.route('/history')
def get_history():
    global history
    return jsonify(history)

if __name__ == '__main__':
    thread = threading.Thread(target=monitor_button)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)
