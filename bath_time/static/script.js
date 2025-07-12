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
                    historyData.forEach(entry => {
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
};
