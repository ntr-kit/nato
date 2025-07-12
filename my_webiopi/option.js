// 時刻を表示する関数
function clock() {
    document.getElementById("view_clock").innerHTML = getNow();
}

// 現在の日時を取得し、フォーマットする関数
function getNow() {
    var now = new Date();
    var year = now.getFullYear();
    var mon = now.getMonth() + 1; // 月を1足す
    var day = now.getDate();
    var hour = now.getHours();
    var min = now.getMinutes();
    var sec = now.getSeconds();

    // 各値が10未満の場合、前に0を追加
    mon = mon < 10 ? '0' + mon : mon;
    day = day < 10 ? '0' + day : day;
    hour = hour < 10 ? '0' + hour : hour;
    min = min < 10 ? '0' + min : min;
    sec = sec < 10 ? '0' + sec : sec;

    // フォーマットされた文字列を返す
    return year + "年" + mon + "月" + day + "日　" + hour + ":" + min + ":" + sec;
}

// WebIOPiを使って温度と湿度を取得して表示する関数
function updateData() {
    webiopi().callMacro("getTemperature", [], function(macro, args, result) {
        var temperature = parseFloat(result).toFixed(2); // 小数点2桁にフォーマット
        document.getElementById("temperature").innerHTML = temperature + " °C";
    });

    webiopi().callMacro("getHumidity", [], function(macro, args, result) {
        var humidity = parseFloat(result).toFixed(2); // 小数点2桁にフォーマット
        document.getElementById("humidity").innerHTML = humidity + " %";
    });
}

function calculateDI(temperature, humidity) {
    // 不快指数の計算式
    var di = 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3;
    return di.toFixed(2); // 小数点以下2桁に丸める
}

// 不快指数を表示する関数
function updateDI() {
    var tempElement = document.getElementById("temperature").innerHTML;
    var humidityElement = document.getElementById("humidity").innerHTML;
    
    // 数値部分のみ取得
    var temperature = parseFloat(tempElement.split(" ")[0]);
    var humidity = parseFloat(humidityElement.split(" ")[0]);
    
    // 不快指数を計算し表示
    var di = calculateDI(temperature, humidity);
    document.getElementById("discomfortIndex").innerHTML = di + " DI";
}

var temperatureData = [];
// 温度データを更新し、最高気温を計算して表示する関数
function updateTemperature() {
    webiopi().callMacro("getTemperature", [], function(macro, args, result) {
        var currentTemp = parseFloat(result).toFixed(2); // 小数点2桁にフォーマット
        temperatureData.push(currentTemp); // 温度データを配列に追加

        // 最高気温を計算
        var maxTemp = Math.max(...temperatureData).toFixed(2); // 小数点2桁にフォーマット
        document.getElementById("temperature").innerHTML = currentTemp + " °C";
        document.getElementById("maxTemperature").innerHTML = maxTemp + " °C";
    });
}

// ボタンがクリックされたときの視覚的フィードバックを提供する関数
function buttonClick(button) {
    button.disabled = true; // ボタンを無効化
    button.classList.add("button-clicked"); // ボタンの色を変える

    // 5秒後にボタンを再度有効化し、元のスタイルに戻す
    setTimeout(function() {
        button.disabled = false;
        button.classList.remove("button-clicked");
    }, 5000);
}

// ページが読み込まれたときに実行する処理
window.onload = function() {
    updateData(); // 初回データ取得
    setInterval(updateData, 10000);  // 10秒ごとにデータを更新
    setInterval(updateDI, 10000);
    setInterval(updateTemperature, 10000);
    timerID = setInterval(clock, 500); // 0.5秒ごとに時計を更新
};
