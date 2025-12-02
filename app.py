from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import os
import subprocess
import psutil

UPLOAD_DIR = 'uploaded_bots'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = Flask(__name__)
bot_scripts = {}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Dashboard Bot Python</title>
<style>
body {
    font-family: Arial;
    padding: 25px;
    background: linear-gradient(#ffe6f0, #ffd1e6);
    overflow-x: hidden;
    position: relative;
}

/* Tuyết rơi CSS */
.snowflake {
    position: fixed;
    top: -10px;
    color: #fff;
    font-size: 12px;
    z-index: 9999;
    user-select: none;
    pointer-events: none;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}
@keyframes fall {
    0% { transform: translateY(0px); }
    100% { transform: translateY(100vh); }
}

/* Container */
.container { max-width: 950px; margin:auto; background: rgba(255,255,255,0.9); padding:25px; border-radius:15px; box-shadow:0 4px 10px rgba(0,0,0,0.1); }

/* Tiêu đề */
h1 { font-size:32px; color:#333; }

/* Upload Section */
.upload-section { padding:20px; border-radius:15px; margin-bottom:30px; background: #ffe6f0; }
.upload-section h3 { margin-bottom:15px; font-size:22px; color:#333; }

/* Ẩn input file thật */
input[type=file] { display:none; }

/* Nút giả chọn file */
.custom-file-upload {
  display: inline-block;
  padding: 15px 35px;
  font-size: 20px;
  cursor: pointer;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff8a8a, #ffb3c6);
  color: white;
  font-weight: bold;
  transition: 0.3s;
  margin-right: 15px;
}
.custom-file-upload:hover { opacity:0.85; }

/* Nút Upload */
button.upload { background:#ff66b2; color:white; padding:15px 35px; border:none; border-radius:12px; cursor:pointer; font-size:20px; transition:0.2s; }
button.upload:hover { opacity:0.85; }

/* File List */
.file-item { background: #fff0f5; padding:20px; margin-bottom:18px; border-radius:15px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
.file-name { font-weight:bold; font-size:20px; color:#333; }
.status { padding:8px 18px; border-radius:10px; font-weight:bold; font-size:16px; color:white; }
.running { background:#4CAF50; }  /* xanh lá */
.stopped { background:#f44336; } /* đỏ */
.file-actions button { font-size:18px; padding:12px 28px; margin-left:8px; border:none; border-radius:12px; cursor:pointer; transition:0.2s; }
.file-actions button:hover { opacity:0.85; }
.run { background:#4CAF50; color:white; }
.stop { background:#f44336; color:white; }
.delete { background:#888; color:white; }
a { text-decoration:none; font-weight:bold; font-size:18px; margin-left:15px; color:#ff3399; }

/* Nút bật/tắt nhạc */
.audio-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 22px;
    font-size: 16px;
    border: none;
    border-radius: 10px;
    background: #ff66b2;
    color: white;
    cursor: pointer;
    transition: 0.3s;
}
.audio-btn:hover { opacity:0.8; }
</style>
</head>
<body>

<!-- Nhạc nền -->
<audio id="bgAudio" autoplay loop>
  <source src="/audio/tuyen_ngon_bac_ho.mp3" type="audio/mpeg">
  Trình duyệt của bạn không hỗ trợ audio.
</audio>
<button class="audio-btn" onclick="toggleAudio()">🔊 Nhạc</button>

<!-- Tuyết rơi -->
<div id="snow"></div>

<div class="container">
<h1>📂 Bảng điều khiển Bot Python</h1>

<div class="upload-section">
<h3>⬆️ Upload File Mới</h3>
<form id="uploadForm" method="POST" enctype="multipart/form-data" action="/upload">
    <label class="custom-file-upload">
        📂 Chọn tệp
        <input type="file" name="file" id="fileInput" required>
    </label>
    <span id="fileName" style="margin-left:15px; font-size:18px; color:#333;"></span>
    <br><br>
    <button class="upload" type="submit">Upload</button>
</form>
</div>

<h3>🖥️ Danh sách file & trạng thái</h3>
{% for f in files %}
<div class="file-item">
<div>
<span class="file-name">{{f}}</span>
<span class="status {% if f in running %}running{% else %}stopped{% endif %}">
{% if f in running %}Đang chạy{% else %}Đã dừng{% endif %}
</span>
</div>
<div class="file-actions">
<form style="display:inline;" action="/run/{{f}}" method="post">
<button class="run">▶️ Chạy</button>
</form>
<form style="display:inline;" action="/stop/{{f}}" method="post">
<button class="stop">🔴 Dừng</button>
</form>
<form style="display:inline;" action="/delete/{{f}}" method="post">
<button class="delete">🗑️ Xóa</button>
</form>
<a href="/files/{{f}}">🌐 Tải xuống</a>
</div>
</div>
{% endfor %}
</div>

<script>
// Hiển thị tên file khi chọn
const fileInput = document.getElementById('fileInput');
const fileNameSpan = document.getElementById('fileName');
const uploadForm = document.getElementById('uploadForm');

fileInput.addEventListener('change', () => {
    if(fileInput.files.length > 0){
        fileNameSpan.textContent = fileInput.files[0].name;
    } else {
        fileNameSpan.textContent = '';
    }
});

// Xác nhận trước khi upload
uploadForm.addEventListener('submit', function(e){
    if(fileInput.files.length > 0){
        const confirmUpload = confirm('Bạn có chắc muốn upload file: ' + fileInput.files[0].name + ' không?');
        if(!confirmUpload){
            e.preventDefault();
        }
    }
});

// Tuyết rơi
const snowContainer = document.getElementById('snow');
const numFlakes = 50;

for(let i=0;i<numFlakes;i++){
    let flake = document.createElement('div');
    flake.className = 'snowflake';
    flake.textContent = '❄';
    flake.style.left = Math.random() * window.innerWidth + 'px';
    flake.style.fontSize = (12 + Math.random()*20) + 'px';
    flake.style.animationDuration = (5 + Math.random()*5) + 's';
    flake.style.animationDelay = (Math.random()*5) + 's';
    snowContainer.appendChild(flake);
}

// Bật/tắt nhạc
function toggleAudio(){
    var audio = document.getElementById('bgAudio');
    if(audio.paused) audio.play();
    else audio.pause();
}
</script>

</body>
</html>
"""

def run_script(path):
    process = subprocess.Popen(['python3', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bot_scripts[path] = {'process': process, 'status': 'running'}
    return process

def stop_script(path):
    info = bot_scripts.get(path)
    if info and info.get('status') == 'running':
        process = info['process']
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except:
            pass
        bot_scripts[path]['status'] = 'stopped'

@app.route('/')
def index():
    files = os.listdir(UPLOAD_DIR)
    running = [os.path.basename(p) for p, info in bot_scripts.items() if info.get('status') == 'running']
    return render_template_string(HTML_PAGE, files=files, running=running)

@app.route('/upload', methods=['POST'])
def upload_web():
    if 'file' not in request.files:
        return "❌ Không có file", 400
    file = request.files['file']
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(save_path)
    return redirect(url_for('index'))

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/run/<filename>', methods=['POST'])
def run_file(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        run_script(path)
    return redirect(url_for('index'))

@app.route('/stop/<filename>', methods=['POST'])
def stop_file(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    stop_script(path)
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    try:
        stop_script(path)
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print("Lỗi xóa file:", e)
    return redirect(url_for('index'))

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)