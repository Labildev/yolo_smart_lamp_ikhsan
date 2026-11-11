# ==============================================================================
# SIMULATOR PENGIRIMAN CITRA ESP32-S3-CAM KE SERVER FLASK
# Menguji endpoint /api/detect dan respons JSON tanpa perangkat keras fisik
# Peneliti: Ikhsan Wahyudi (235520110043)
# ==============================================================================

import os
import sys
import time
import requests

SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:5000/api/detect")

def simulate_esp32_post(image_path, server_url=None):
    """
    Mengirim file gambar seolah-olah ditangkap oleh ESP32-S3:
    1. Mengirim raw byte JPEG dengan header Content-Type: image/jpeg
    2. Menghitung total latensi jaringan + inferensi
    3. Memeriksa format JSON dan keputusan relay (lamp_action)
    """
    url = server_url or SERVER_URL
    if not os.path.exists(image_path):
        print(f"[ERROR] Berkas citra tidak ditemukan: {image_path}")
        return False

    print("\n-------------------------------------------------------")
    print(f"[SIMULASI ESP32-S3] Membaca citra: {os.path.basename(image_path)}")
    
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    print(f"[SIMULASI ESP32-S3] Ukuran citra: {len(img_bytes)} bytes")
    print(f"[SIMULASI ESP32-S3] Mengirim HTTP POST ke: {url} (Timeout 5000ms)...")

    start_time = time.time()
    try:
        response = requests.post(
            url,
            data=img_bytes,
            headers={"Content-Type": "image/jpeg"},
            timeout=5.0
        )
        total_time_ms = (time.time() - start_time) * 1000

        print(f"[HTTP STATUS] {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\n[RESPONS JSON SERVER]")
            print(f" - Kategori            : {data.get('category')}")
            print(f" - Kelas Terdeteksi    : {data.get('detected_classes')}")
            print(f" - Nilai Confidence    : {data.get('confidence')}")
            print(f" - Waktu Inferensi AI  : {data.get('inference_time_ms')} ms")
            print(f" - Total Latensi Klien : {total_time_ms:.1f} ms")
            print(f" - Keputusan Lampu     : {data.get('lamp_action')}")

            # Simulasi perilaku relay pada ESP32-S3
            if data.get('lamp_action') == 'ON':
                print("\n>>> [RESPON HARDWARE ESP32] TARGET POSITIF!")
                print(">>> Pin GPIO 14 -> Trigger Relay ON.")
                print(">>> Lampu LED 12V MENYALA selama 10 detik (+ Auto-Extend aktif).")
            else:
                print("\n>>> [RESPON HARDWARE ESP32] TARGET BUKAN MANUSIA/KENDARAAN.")
                print(">>> Pin GPIO 14 -> Trigger Relay OFF.")
                print(">>> Lampu LED 12V TETAP PADAM.")

            # Validasi NFR-01: Total Latensi <= 2500 ms
            if total_time_ms <= 2500:
                print("\n[UJI NFR-01] MEMENUHI SYARAT (Latensi <= 2.500 ms)")
            else:
                print("\n[UJI NFR-01] PERINGATAN: Melebihi target 2.500 ms")

            return True
        else:
            print(f"[ERROR] Server merespons dengan kode: {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.Timeout:
        print("[FAIL-SAFE AKTIF] Timeout melebihi 5.000 ms!")
        print(">>> ESP32-S3 otomatis mematikan Relay (Lampu TETAP OFF).")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR KONEKSI] Gagal terhubung ke server Flask!")
        print("Pastikan server sudah berjalan dengan mengklik 'run_server.bat'.")
        return False
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        return False

if __name__ == "__main__":
    target_url = None
    test_file = None

    for arg in sys.argv[1:]:
        if arg.startswith("http://") or arg.startswith("https://"):
            target_url = arg
        else:
            test_file = arg

    if target_url:
        SERVER_URL = target_url

    if not test_file:
        # Cari file uji di folder sample_images jika ada
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(tools_dir)
        sample_dir = os.path.join(project_root, "sample_images")
        if not os.path.exists(sample_dir):
            sample_dir = os.path.join(tools_dir, "sample_images")
        if os.path.exists(sample_dir):
            files = [os.path.join(sample_dir, f) for f in os.listdir(sample_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if files:
                test_file = files[0]

    if not test_file:
        print("Penggunaan:")
        print("  python simulate_esp32.py [opsional_path_gambar.jpg] [opsional_url_server]")
        print("Contoh:")
        print("  python simulate_esp32.py sample_images/uji_manusia.jpg")
        print("  python simulate_esp32.py https://smart-lamp.onrender.com/api/detect")
        sys.exit(1)

    simulate_esp32_post(test_file, SERVER_URL)

