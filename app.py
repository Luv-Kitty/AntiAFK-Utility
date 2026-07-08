import os
import sys
import time
import random
import threading
import ctypes
from http.server import SimpleHTTPRequestHandler, HTTPServer
import webbrowser

VK_MAP = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47,
    'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E,
    'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55,
    'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    'ф': 0x41, 'и': 0x42, 'с': 0x43, 'в': 0x44, 'у': 0x45, 'а': 0x46, 'п': 0x47,
    'р': 0x48, 'ш': 0x49, 'о': 0x4A, 'л': 0x4B, 'д': 0x4C, 'ь': 0x4D, 'т': 0x4E,
    'щ': 0x4F, 'з': 0x50, 'й': 0x51, 'к': 0x52, 'ы': 0x53, 'е': 0x54, 'г': 0x55,
    'м': 0x56, 'ц': 0x57, 'ч': 0x58, 'н': 0x59, 'я': 0x5A,
    'space': 0x20, 'пробел': 0x20, ' ': 0x20
}

active_keys = [0x57, 0x41, 0x53, 0x44, 0x20]
user_keys_string = "W, A, S, D, SPACE"
VK_L = 0x4C

running = False
hotkey_listening = True
min_delay = 5.0
max_delay = 15.0


def press_key(vk_code): ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)


def release_key(vk_code): ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)



def afk_worker():
    global running, min_delay, max_delay, active_keys
    while running:
        if not active_keys:
            time.sleep(1)
            continue

        if len(active_keys) > 1 and random.random() < 0.30:
            key1 = random.choice(active_keys)
            key2 = random.choice(active_keys)
            press_key(key1)
            time.sleep(random.uniform(0.05, 0.1))
            press_key(key2)
            time.sleep(random.uniform(0.1, 0.25))
            release_key(key2)
            release_key(key1)
        else:
            key = random.choice(active_keys)
            press_key(key)
            time.sleep(random.uniform(0.1, 0.3))
            release_key(key)

        current_min = min(min_delay, max_delay)
        current_max = max(min_delay, max_delay)
        delay = random.uniform(current_min, current_max)

        for _ in range(int(delay * 2)):
            if not running: break
            time.sleep(0.5)


def toggle_service():
    global running
    if not running:
        running = True
        threading.Thread(target=afk_worker, daemon=True).start()
    else:
        running = False


def global_hotkey_loop():
    global hotkey_listening
    user32 = ctypes.windll.user32
    while hotkey_listening:
        if user32.GetAsyncKeyState(VK_L) & 0x8000:
            pressed_time = 0
            is_held = True
            while pressed_time < 5.0:
                time.sleep(0.1)
                pressed_time += 0.1
                if not (user32.GetAsyncKeyState(VK_L) & 0x8000):
                    is_held = False
                    break
            if is_held:
                toggle_service()
                while user32.GetAsyncKeyState(VK_L) & 0x8000:
                    time.sleep(0.1)
        time.sleep(0.1)


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>luv_kitty's AntiAFK | Dashboard</title>
    <style>
        :root {
            --bg-color: #f4f6f9;
            --panel-bg: #ffffff;
            --inner-bg: #edf0f5;
            --text-main: #2c3e50;
            --text-muted: #7f8c8d;
            --accent-color: #1b4d3e;
            --accent-hover: #2c6b56;
            --border-color: #dcdde1;
            --shadow: rgba(0, 0, 0, 0.05);
        }

        [data-theme="dark"] {
            --bg-color: #0b0b0f;
            --panel-bg: #111116;
            --inner-bg: #07070a;
            --text-main: #cdd6f4;
            --text-muted: #6c7086;
            --accent-color: #2e7d32;
            --accent-hover: #4caf50;
            --border-color: #1f1f28;
            --shadow: rgba(0, 0, 0, 0.4);
        }

        body { 
            background-color: var(--bg-color); 
            color: var(--text-main); 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            padding: 40px 20px; 
            margin: 0; 
            transition: background-color 0.3s, color 0.3s;
        }

        .container { max-width: 850px; margin: 0 auto; }

        .header-box { 
            background: var(--panel-bg); 
            padding: 30px; 
            border-radius: 16px; 
            box-shadow: 0 4px 20px var(--shadow); 
            border: 1px solid var(--border-color); 
            text-align: center; 
            margin-bottom: 20px; 
            position: relative;
        }

        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--inner-bg);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: 0.2s;
        }
        .theme-toggle:hover {
            border-color: var(--accent-color);
        }

        h1 { 
            color: var(--text-main); 
            font-size: 32px; 
            margin-top: 0; 
            margin-bottom: 5px; 
            font-weight: 800; 
            letter-spacing: 1px; 
        }

        h1 span { 
            color: var(--accent-color); 
            transition: color 0.3s;
        }

        .subtitle { 
            color: var(--text-muted); 
            font-size: 14px; 
            margin-bottom: 25px; 
        }

        .status-card { 
            margin: 10px auto 0 auto; 
            padding: 12px; 
            border-radius: 8px; 
            background: var(--inner-bg); 
            font-weight: bold; 
            font-size: 14px; 
            letter-spacing: 1px; 
            transition: 0.3s; 
            border: 1px solid var(--border-color); 
            max-width: 400px; 
        }

        .status-stopped { color: #d32f2f; border-color: rgba(211, 47, 47, 0.2); }
        .status-active { color: #2e7d32; border-color: rgba(46, 125, 50, 0.2); }

        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { 
            background: var(--panel-bg); 
            padding: 25px; 
            border-radius: 16px; 
            box-shadow: 0 8px 24px var(--shadow); 
            border: 1px solid var(--border-color); 
            display: flex; 
            flex-direction: column; 
        }

        .panel-title { 
            font-size: 15px; 
            font-weight: bold; 
            color: var(--accent-color); 
            margin-bottom: 20px; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            border-bottom: 1px solid var(--border-color); 
            padding-bottom: 10px; 
        }

        .btn { 
            background-color: var(--accent-color); 
            color: #ffffff; 
            border: none; 
            width: 100%; 
            padding: 16px; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 10px; 
            cursor: pointer; 
            transition: 0.2s; 
            margin-bottom: 20px; 
        }

        .btn:hover { background-color: var(--accent-hover); transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .btn.active { background-color: #2e7d32; color: #ffffff; }

        .input-keys { 
            width: 100%; 
            background: var(--inner-bg); 
            border: 1px solid var(--border-color); 
            padding: 12px; 
            border-radius: 8px; 
            color: var(--text-main); 
            font-size: 14px; 
            box-sizing: border-box; 
            margin-bottom: 10px; 
            font-family: inherit; 
        }
        .input-keys:focus { border-color: var(--accent-color); outline: none; }

        .save-btn { 
            background: var(--inner-bg); 
            color: var(--text-main); 
            border: 1px solid var(--border-color); 
            padding: 8px 16px; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 12px; 
            font-weight: bold; 
            transition: 0.2s; 
            width: max-content; 
            margin-bottom: 15px; 
        }
        .save-btn:hover { background: var(--accent-color); color: #fff; border-color: var(--accent-color); }

        .info-box { 
            background: var(--inner-bg); 
            padding: 15px; 
            border-radius: 8px; 
            font-size: 13px; 
            line-height: 1.6; 
            color: var(--text-muted); 
            border: 1px solid var(--border-color); 
            flex-grow: 1; 
        }

        .range-group { margin-bottom: 20px; }
        .range-group:last-child { margin-bottom: 0; }
        .range-labels { display: flex; justify-content: space-between; font-size: 13px; color: var(--text-muted); margin-bottom: 8px; }
        input[type="range"] { width: 100%; accent-color: var(--accent-color); background: var(--inner-bg); height: 6px; border-radius: 5px; cursor: pointer; }

        .accent-text { color: var(--accent-color); font-weight: bold; }
        .red-text { color: #d32f2f; font-weight: bold; }
        .green-text { color: #2e7d32; font-weight: bold; }
    </style>
    <script>
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', targetTheme);
            document.getElementById('theme-btn').innerText = targetTheme === 'dark' ? '☀️ СВЕТЛАЯ' : '🌙 ТЁМНАЯ';
            localStorage.setItem('theme', targetTheme);
        }

        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            document.getElementById('theme-btn').innerText = savedTheme === 'dark' ? '☀️ СВЕТЛАЯ' : '🌙 ТЁМНАЯ';
        }

        function toggle() {
            fetch('/toggle').then(() => updateStatus());
        }

        function saveKeys() {
            let keys = document.getElementById('keys-input').value;
            fetch(`/set_keys?keys=${encodeURIComponent(keys)}`).then(() => {
                let sBtn = document.getElementById('save-btn');
                sBtn.innerText = "сохранено";
                sBtn.style.borderColor = "#2e7d32";
                setTimeout(() => {
                    sBtn.innerText = "применить";
                    sBtn.style.borderColor = "var(--border-color)";
                }, 1500);
            });
        }

        function updateDelay() {
            let min = document.getElementById('min-range').value;
            let max = document.getElementById('max-range').value;
            document.getElementById('min-val').innerText = min + 'с';
            document.getElementById('max-val').innerText = max + 'с';
            fetch(`/set_delay?min=${min}&max=${max}`);
        }

        function updateStatus() {
            fetch('/status').then(r => r.json()).then(data => {
                let btn = document.getElementById('action-btn');
                let card = document.getElementById('status-card');
                let text = document.getElementById('status-text');

                if (!document.getElementById('min-range').matches(':active')) {
                    document.getElementById('min-range').value = data.min;
                    document.getElementById('min-val').innerText = data.min + 'с';
                }
                if (!document.getElementById('max-range').matches(':active')) {
                    document.getElementById('max-range').value = data.max;
                    document.getElementById('max-val').innerText = data.max + 'с';
                }
                if (!document.getElementById('keys-input').matches(':focus')) {
                    document.getElementById('keys-input').value = data.keys_str;
                }

                if (data.running) {
                    btn.innerText = "остановить"; btn.classList.add('active');
                    card.className = "status-card status-active";
                    text.innerHTML = "статус: <span class='green-text'>активен</span>";
                } else {
                    btn.innerText = "запустить"; btn.classList.remove('active');
                    card.className = "status-card status-stopped";
                    text.innerHTML = "статус: <span class='red-text'>остановлен</span>";
                }
            });
        }
        setInterval(updateStatus, 1000);
    </script>
</head>
<body onload="initTheme(); updateStatus()">
    <div class="container">

        <div class="header-box">
            <button id="theme-btn" class="theme-toggle" onclick="toggleTheme()">🌙 ТЁМНАЯ</button>
            <h1>AntiAFK by <span>luv_kitty</span></h1>
            <div class="subtitle">AntiAFK — симуляция активности в фоне</div>
            <div id="status-card" class="status-card status-stopped">
                <span id="status-text">статус : остановлен</span>
            </div>
        </div>

        <div class="main-grid">

            <div class="panel">
                <div class="panel-title">управление и клавиши</div>
                <button id="action-btn" class="btn" onclick="toggle()">запустить</button>

                <div style="font-size: 13px; margin-bottom: 8px; color: var(--text-muted);">какие клавиши нажимать (через запятую):</div>
                <input type="text" id="keys-input" class="input-keys" value="W, A, S, D, SPACE">
                <button id="save-btn" class="save-btn" onclick="saveKeys()">применить</button>

                <div class="info-box">
                    зажми <span class="accent-text">'L' (Д)</span> прямо в игре на 5 секунд для быстрого переключения макроса.
                </div>
            </div>

            <div class="panel">
                <div class="panel-title">настройка таймингов</div>

                <div class="range-group">
                    <div class="range-labels">
                        <span>минимальная пауза:</span>
                        <span id="min-val" class="accent-text">5с</span>
                    </div>
                    <input type="range" id="min-range" min="1" max="30" value="5" oninput="updateDelay()">
                </div>

                <div class="range-group">
                    <div class="range-labels">
                        <span>максимальная пауза:</span>
                        <span id="max-val" class="accent-text">15с</span>
                    </div>
                    <input type="range" id="max-range" min="2" max="60" value="15" oninput="updateDelay()">
                </div>

                <div class="info-box" style="margin-top: auto; flex-grow: 0;">
                    задержки и комбинации клавиш подбираются случайно для эффективной симуляции присутствия игрока.
                </div>
            </div>

        </div>

    </div>
</body>
</html>
"""


class WebServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        global running, min_delay, max_delay, active_keys, user_keys_string
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/toggle':
            toggle_service()
            self.send_response(200)
            self.end_headers()
        elif self.path.startswith('/set_delay'):
            try:
                from urllib.parse import urlparse, parse_qs
                query = parse_qs(urlparse(self.path).query)
                min_delay = float(query.get('min', [5.0])[0])
                max_delay = float(query.get('max', [15.0])[0])
            except:
                pass
            self.send_response(200)
            self.end_headers()
        elif self.path.startswith('/set_keys'):
            try:
                from urllib.parse import urlparse, parse_qs
                query = parse_qs(urlparse(self.path).query)
                raw_keys = query.get('keys', [""])[0]
                user_keys_string = raw_keys

                new_codes = []
                parts = [p.strip().lower() for p in raw_keys.split(',')]
                for p in parts:
                    if p in VK_MAP:
                        new_codes.append(VK_MAP[p])

                active_keys = new_codes
            except:
                pass
            self.send_response(200)
            self.end_headers()
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            status_data = {
                "running": running,
                "min": min_delay,
                "max": max_delay,
                "keys_str": user_keys_string
            }
            self.wfile.write(json.dumps(status_data).encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    threading.Thread(target=global_hotkey_loop, daemon=True).start()

    port = 1337
    server = HTTPServer(('127.0.0.1', port), WebServer)
    webbrowser.open(f'http://127.0.0.1:{port}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    hotkey_listening = False