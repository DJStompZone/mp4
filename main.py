from flask import Flask, request, abort, send_file, render_template
from multiprocessing import Process
import uuid
import subprocess
import tempfile
import re

app = Flask(__name__)

downloads = {}

VERSION = "1.1.2 Beta"

def extract_youtube_id(text):
    url_patterns = [
        r"(?<=watch\?v=)[^&]+",
        r"(?<=youtu.be/)[^?&]+",
        r"(?<=youtube.com/embed/)[^?&]+",
        r"(?<=youtube.com/shorts/)[^?&]+",
        r"(?<=music.youtube.com/watch\?v=)[^&]+",
        r"^[A-Za-z0-9_-]{11}$"
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None

def download_video(video_id, filepath):
    command = ["yt-dlp", "-ci", "--force-overwrites", "-f", "mp4", "-o", filepath, f"https://www.youtube.com/watch?v={video_id}"]
    subprocess.run(command)

@app.route('/mp4')
def mp4():
    video_id = extract_youtube_id(request.args.get('id'))
    if video_id == None:
        abort(404)  # Return HTTP 404 Not Found error

    temp_file = tempfile.NamedTemporaryFile(dir="./tmp/", suffix=".mp4", delete=False)

    download_id = str(uuid.uuid4())
    downloads[download_id] = {
        'process': Process(target=download_video, args=(video_id, temp_file.name)),
        'filepath': temp_file.name
    }
    downloads[download_id]['process'].start()

    return {"download_id": download_id}, 202  # Return the unique download ID and a HTTP 202 Accepted status

@app.route('/download/<download_id>')
def download(download_id):
    if download_id not in downloads:
        abort(404)  # Return HTTP 404 Not Found error

    if downloads[download_id]['process'].is_alive():
        return {"status": "processing"}, 202  # If the download is still ongoing, return a HTTP 202 Accepted status

    filepath = downloads[download_id]['filepath']
    del downloads[download_id]  # Clean up the entry in the dictionary

    return send_file(filepath, mimetype="video/mp4", as_attachment=True, download_name=f"{download_id}.mp4")

@app.route('/')
def index():
    return render_template("index.html", version=VERSION)

app.run(debug=True, host="0.0.0.0", port=0)
