import os
import uuid
import subprocess
from flask import Flask, render_template, request, send_file, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'rahasia'  # untuk flash message
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")


@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    resolution = request.form.get('resolution')
    cookies_file = request.files.get('cookies')

    if not url or not cookies_file:
        flash('URL dan file cookies wajib diisi.')
        return redirect(url_for('index'))

    # Simpan cookies yang diupload
    cookies_path = os.path.join(DOWNLOAD_FOLDER, f'{uuid.uuid4()}.txt')
    cookies_file.save(cookies_path)

    # Nama file sementara
    filename = f"video_{uuid.uuid4()}"
    video_path = os.path.join(DOWNLOAD_FOLDER, f"{filename}.mp4")
    audio_path = os.path.join(DOWNLOAD_FOLDER, f"{filename}.m4a")
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{filename}_merged.mp4")

    # Unduh video dan audio secara terpisah
    ytdlp_cmd = [
        'yt-dlp.exe',
        url,
        '--cookies', cookies_path,
        '-f', f'bestvideo[height<={resolution}]+bestaudio',
        '-o', os.path.join(DOWNLOAD_FOLDER, f"{filename}.%(ext)s")
    ]

    try:
        flash("Download Selesai...")
        subprocess.run(ytdlp_cmd, check=True)

        # Gabungkan video dan audio menggunakan ffmpeg.exe
        ffmpeg_cmd = [
            'ffmpeg.exe', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            output_path
        ]
        subprocess.run(ffmpeg_cmd, check=True)

        # Hapus file terpisah jika berhasil
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(cookies_path)

        flash("Download selesai. File siap diunduh.")
        return send_file(output_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        flash(f"Terima Kasih")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
