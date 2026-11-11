# ==============================================================================
# SKRIPSI INFORMATIKA - UNIVERSITAS ALMUSLIM
# Peneliti   : Ikhsan Wahyudi (235520110043)
# Judul      : Implementasi Sistem Kendali Lampu Pintar Menggunakan Deep Learning
#              Untuk Deteksi dan Pelacakan Objek Yang Melintas
# Deskripsi  : Backend Server Flask & Web Dashboard Real-Time
# ==============================================================================

import os
import sys

# Batasi thread library komputasi ilmiah agar aman di hosting cPanel CloudLinux (hindari OpenBLAS pthread error)
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TORCH_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"

import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, Response
from detector import YOLOv8Detector
from logger import log_detection, get_recent_logs, get_total_tests_count, clear_logs, CSV_PATH
from webcam import OpenCVWebcam

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)

# Inisialisasi Detektor YOLOv8 & Pengelola Webcam Laptop
detector = YOLOv8Detector()
webcam = OpenCVWebcam()

@app.errorhandler(500)
def handle_500(e):
    import traceback
    return f"""
    <div style="font-family: monospace; padding: 25px; background: #fff1f2; border: 2px solid #e11d48; color: #9f1239; border-radius: 8px;">
        <h2 style="margin-top:0;">Detail Kesalahan Backend (Error 500):</h2>
        <p>Terjadi pengecualian saat memproses permintaan:</p>
        <pre style="background: #ffffff; padding: 15px; border-radius: 6px; overflow-x: auto; border: 1px solid #fda4af;">{traceback.format_exc()}</pre>
    </div>
    """, 500

# State Terakhir Sistem (Untuk Pemantauan Real-Time pada Web Dashboard)
latest_state = {
    'status': 'idle',
    'category': '-',
    'detected_classes': [],
    'confidence': 0.0,
    'inference_time_ms': 0.0,
    'lamp_action': 'OFF',
    'file_name': '',
    'timestamp': '-',
    'is_custom_model': detector.is_custom_model
}

@app.after_request
def add_cors_headers(response):
    """Menambahkan header CORS agar API dapat diakses dari dashboard eksternal atau hosting cloud."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/health')
@app.route('/api/health')
def api_health():
    """Health check endpoint untuk load balancer & platform cloud (Render, Railway, AWS, GCP)."""
    return jsonify({
        'status': 'healthy',
        'service': 'smart-lamp-yolov8',
        'is_custom_model': detector.is_custom_model,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/')
def index():
    """Halaman Utama Landing Page Penelitian & Sistem."""
    return render_template('landing.html')

@app.route('/dashboard')
@app.route('/index.html')
def dashboard():
    """Halaman Utama Web Dashboard Pemantauan & Analisis Real-Time."""
    return render_template('dashboard.html')

@app.route('/api/detect', methods=['POST'])
def api_detect():
    """
    Endpoint Utama Inferensi YOLOv8:
    Menerima citra JPEG dari ESP32-S3 (Raw Bytes) atau Unggahan Web (Multipart Form).
    Mengembalikan format JSON sesuai TRD Sub-bab 3.4.
    """
    global latest_state
    try:
        image_bytes = None

        # 1. Cek apakah request berupa multipart/form-data (dari browser/Postman)
        if 'image' in request.files:
            image_bytes = request.files['image'].read()
        elif 'file' in request.files:
            image_bytes = request.files['file'].read()
        # 2. Cek apakah request berupa raw binary data (dari ESP32-S3 HTTPClient)
        elif request.data:
            image_bytes = request.data

        if not image_bytes or len(image_bytes) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Citra tidak ditemukan dalam request (Payload kosong).'
            }), 400

        # 3. Jalankan Inferensi YOLOv8n & Matriks Keputusan
        result = detector.detect(image_bytes)

        # 4. Catat Pengujian ke CSV secara Persisten (Acuan Bab V Skripsi)
        notes = 'Model Custom' if result['is_custom_model'] else 'Model Pretrained (Fallback)'
        test_num = log_detection(
            file_name=result['file_name'],
            detected_classes=result['detected_classes'],
            category=result['category'],
            confidence=result['confidence'],
            inference_time_ms=result['inference_time_ms'],
            lamp_action=result['lamp_action'],
            notes=notes
        )

        # 5. Perbarui State Terakhir untuk Web Dashboard
        now_str = datetime.now().strftime('%H:%M:%S')
        latest_state.update({
            'status': 'success',
            'category': result['category'],
            'detected_classes': result['detected_classes'],
            'confidence': result['confidence'],
            'inference_time_ms': result['inference_time_ms'],
            'lamp_action': result['lamp_action'],
            'file_name': result['file_name'],
            'timestamp': now_str,
            'is_custom_model': result['is_custom_model']
        })

        print(f"[DETECT #{test_num}] {now_str} | Kat: {result['category'].upper()} | "
              f"Objek: {result['detected_classes']} | Conf: {result['confidence']:.2f} | "
              f"Waktu: {result['inference_time_ms']:.1f}ms | Lampu: {result['lamp_action']}")

        # 6. Kirim Respons JSON ke ESP32-S3-CAM
        return jsonify({
            'status': 'success',
            'category': result['category'],
            'detected_classes': result['detected_classes'],
            'confidence': result['confidence'],
            'inference_time_ms': result['inference_time_ms'],
            'lamp_action': result['lamp_action']
        }), 200

    except Exception as e:
        print(f"[ERROR /api/detect] {e}")
        return jsonify({
            'status': 'error',
            'category': 'objek_lain',
            'detected_classes': [],
            'confidence': 0.0,
            'inference_time_ms': 0.0,
            'lamp_action': 'OFF',
            'error_message': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Mengembalikan data status terakhir dan total pengujian untuk pembaruan dashboard."""
    state = dict(latest_state)
    state['total_tests'] = get_total_tests_count()
    return jsonify(state)

@app.route('/api/logs', methods=['GET'])
def api_logs():
    """Mengembalikan riwayat pengujian terbaru dalam format JSON."""
    return jsonify(get_recent_logs(limit=30))

@app.route('/api/export-csv', methods=['GET'])
def api_export_csv():
    """Mengunduh file rekapitulasi pengujian CSV untuk Bab V Skripsi."""
    if os.path.exists(CSV_PATH):
        return send_file(
            CSV_PATH,
            mimetype='text/csv',
            as_attachment=True,
            download_name='rekap_pengujian_lampu_pintar_yolov8.csv'
        )
    return jsonify({'status': 'error', 'message': 'File log belum tersedia.'}), 404

@app.route('/api/clear-logs', methods=['POST'])
def api_clear_logs():
    """Mereset data log pengujian."""
    global latest_state
    clear_logs()
    latest_state.update({
        'status': 'idle',
        'category': '-',
        'detected_classes': [],
        'confidence': 0.0,
        'inference_time_ms': 0.0,
        'lamp_action': 'OFF',
        'file_name': '',
        'timestamp': '-'
    })
    return jsonify({'status': 'success', 'message': 'Log pengujian berhasil direset.'})

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """Menyajikan arsip foto hasil tangkapan di folder uploads."""
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/api/test-sample', methods=['POST'])
def api_test_sample():
    """Menjalankan deteksi instan menggunakan sampel foto untuk kemudahan presentasi skripsi."""
    global latest_state
    try:
        sample_name = request.json.get('sample_name') if request.is_json else request.form.get('sample_name')
        if not sample_name:
            return jsonify({'status': 'error', 'message': 'Parameter sample_name tidak diberikan'}), 400

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sample_path = os.path.join(project_root, 'sample_images', sample_name)

        if not os.path.exists(sample_path):
            return jsonify({'status': 'error', 'message': f'File sampel {sample_name} tidak ditemukan'}), 404

        with open(sample_path, 'rb') as f:
            image_bytes = f.read()

        result = detector.detect(image_bytes)
        notes = f"Simulasi Instan ({sample_name})"
        test_num = log_detection(
            file_name=result['file_name'],
            detected_classes=result['detected_classes'],
            category=result['category'],
            confidence=result['confidence'],
            inference_time_ms=result['inference_time_ms'],
            lamp_action=result['lamp_action'],
            notes=notes
        )

        now_str = datetime.now().strftime('%H:%M:%S')
        latest_state.update({
            'status': 'success',
            'category': result['category'],
            'detected_classes': result['detected_classes'],
            'confidence': result['confidence'],
            'inference_time_ms': result['inference_time_ms'],
            'lamp_action': result['lamp_action'],
            'file_name': result['file_name'],
            'timestamp': now_str,
            'is_custom_model': result['is_custom_model']
        })

        return jsonify({
            'status': 'success',
            'category': result['category'],
            'detected_classes': result['detected_classes'],
            'confidence': result['confidence'],
            'inference_time_ms': result['inference_time_ms'],
            'lamp_action': result['lamp_action'],
            'file_name': result['file_name']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/webcam_feed')
def api_webcam_feed():
    """Streaming MJPEG langsung dari kamera laptop melalui OpenCV (Bekerja 100% di semua peramban tanpa HTTPS/WebRTC)."""
    def generate():
        started = webcam.start()
        if not started:
            return
        while webcam.is_running:
            frame_bytes = webcam.get_frame_bytes()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.04)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/webcam_capture', methods=['POST'])
def api_webcam_capture():
    """Mengambil frame dari webcam laptop, menjalankan inferensi YOLOv8, dan memperbarui dashboard."""
    global latest_state
    try:
        frame_bytes = webcam.get_frame_bytes()
        if not frame_bytes:
            webcam.start()
            time.sleep(0.4)
            frame_bytes = webcam.get_frame_bytes()

        if not frame_bytes:
            return jsonify({'status': 'error', 'message': 'Gagal membaca frame kamera laptop.'}), 500

        result = detector.detect(frame_bytes)
        notes = "Webcam Laptop OpenCV"
        test_num = log_detection(
            file_name=result['file_name'],
            detected_classes=result['detected_classes'],
            category=result['category'],
            confidence=result['confidence'],
            inference_time_ms=result['inference_time_ms'],
            lamp_action=result['lamp_action'],
            notes=notes
        )

        now_str = datetime.now().strftime('%H:%M:%S')
        latest_state.update({
            'status': 'success',
            'category': result['category'],
            'detected_classes': result['detected_classes'],
            'confidence': result['confidence'],
            'inference_time_ms': result['inference_time_ms'],
            'lamp_action': result['lamp_action'],
            'file_name': result['file_name'],
            'timestamp': now_str,
            'is_custom_model': result['is_custom_model']
        })

        return jsonify({
            'status': 'success',
            'category': result['category'],
            'detected_classes': result['detected_classes'],
            'confidence': result['confidence'],
            'inference_time_ms': result['inference_time_ms'],
            'lamp_action': result['lamp_action'],
            'file_name': result['file_name']
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/webcam_stop', methods=['POST'])
def api_webcam_stop():
    """Mematikan stream kamera laptop."""
    webcam.stop()
    return jsonify({'status': 'success', 'message': 'Kamera laptop dinonaktifkan.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print("=================================================================")
    print("  PELADEN SISTEM KENDALI LAMPU PINTAR (FLASK + YOLOV8)")
    print("  Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim")
    print("=================================================================")
    print(f"Web Dashboard dapat diakses pada: http://localhost:{port}")
    print(f"Endpoint Deteksi ESP32-S3        : http://{host}:{port}/api/detect\n")
    # Jalankan pada 0.0.0.0 agar dapat diakses oleh ESP32 maupun router / platform cloud
    app.run(host=host, port=port, debug=False)

