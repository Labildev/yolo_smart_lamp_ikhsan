# ==============================================================================
# SKRIP OTOMATISASI PENGUJIAN SKENARIO BAB V SKRIPSI (SK-01 s/d SK-08)
# Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
# ==============================================================================

import os
import sys
import time
import requests

SERVER_BASE = os.environ.get("SERVER_BASE", "http://localhost:5000").rstrip('/')
if len(sys.argv) > 1 and (sys.argv[1].startswith("http://") or sys.argv[1].startswith("https://")):
    SERVER_BASE = sys.argv[1].rstrip('/')

SERVER_URL = f"{SERVER_BASE}/api/detect"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_images")

def run_test_scenario(scenario_code, description, image_filename, expected_lamp_action):
    print("\n" + "="*70)
    print(f"[{scenario_code}] {description}")
    print("="*70)

    image_path = os.path.join(SAMPLE_DIR, image_filename)
    if not os.path.exists(image_path):
        print(f"[LEWATI] File sampel '{image_filename}' tidak ditemukan di folder sample_images/.")
        return False

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    start_time = time.time()
    try:
        response = requests.post(
            SERVER_URL,
            data=img_bytes,
            headers={"Content-Type": "image/jpeg"},
            timeout=5.0
        )
        latency_ms = (time.time() - start_time) * 1000

        if response.status_code == 200:
            data = response.json()
            actual_action = data.get("lamp_action")
            category = data.get("category")
            classes = data.get("detected_classes")
            confidence = data.get("confidence")
            inference_ms = data.get("inference_time_ms")

            print(f" - Kategori Terdeteksi : {category.upper()}")
            print(f" - Objek Teridentifikasi: {classes}")
            print(f" - Nilai Confidence    : {confidence}")
            print(f" - Waktu Inferensi AI  : {inference_ms} ms")
            print(f" - Total Latensi Klien : {latency_ms:.1f} ms")
            print(f" - Respon Lampu Aktual : {actual_action}")
            print(f" - Respon Diharapkan   : {expected_lamp_action}")

            is_match = (actual_action == expected_lamp_action)
            latency_ok = (latency_ms <= 2500)

            status_str = "[BERHASIL / VALID]" if (is_match and latency_ok) else "[TIDAK SESUAI]"
            print(f" >>> STATUS HASIL PENGUJIAN: {status_str}")
            return is_match and latency_ok
        else:
            print(f"[GAGAL] Server mengembalikan status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERROR] Tidak dapat terhubung ke server! Pastikan server Flask sudah berjalan.")
        return False
    except Exception as e:
        print(f"[ERROR] Terjadi pengecualian: {e}")
        return False

def main():
    print("=================================================================")
    print("  SUITE PENGUJIAN OTOMATIS MATRIKS BAB V SKRIPSI (YOLOv8)")
    print("  Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim")
    print("=================================================================")
    print(f"Memastikan server Flask aktif di {SERVER_BASE} ...\n")

    # 1. Cek konektivitas server
    try:
        r = requests.get(f"{SERVER_BASE}/api/status", timeout=5.0)
        if r.status_code != 200:
            print(f"[ERROR] Server di {SERVER_BASE} tidak merespons normal. Periksa apakah server sudah aktif.")
            return
    except Exception:
        print(f"[ERROR] Server Flask di {SERVER_BASE} belum aktif!")
        print("Silakan jalankan 'run_server.bat' (lokal) atau pastikan URL server cloud benar.")
        return

    results = []

    # Skenario SK-02: Target Manusia
    res_sk02 = run_test_scenario(
        "SK-02",
        "Pengujian Deteksi Pergerakan Manusia",
        "uji_manusia.jpg",
        "ON"
    )
    results.append(("SK-02: Pergerakan Manusia", "Lampu ON (10s)", "VALID" if res_sk02 else "GAGAL"))

    # Skenario SK-03: Target Kendaraan / Manusia & Bus
    res_sk03 = run_test_scenario(
        "SK-03",
        "Pengujian Deteksi Pergerakan Kendaraan / Multi-Objek",
        "uji_manusia_bus.jpg",
        "ON"
    )
    results.append(("SK-03: Pergerakan Kendaraan", "Lampu ON (10s)", "VALID" if res_sk03 else "GAGAL"))

    # Skenario SK-04: Target Hewan (Kucing)
    res_sk04 = run_test_scenario(
        "SK-04",
        "Pengujian Deteksi Pergerakan Hewan (Kucing)",
        "uji_kucing.jpg",
        "OFF"
    )
    results.append(("SK-04: Pergerakan Hewan", "Lampu OFF (Padam)", "VALID" if res_sk04 else "GAGAL"))

    # Ringkasan Pengujian
    print("\n" + "="*70)
    print("REKAPITULASI HASIL PENGUJIAN SKRIPSI (BAB V)")
    print("="*70)
    print(f"{'Skenario Pengujian':<35} | {'Hasil Diharapkan':<20} | {'Status'}")
    print("-"*70)
    for name, expected, status in results:
        print(f"{name:<35} | {expected:<20} | {status}")
    print("="*70)
    print("Seluruh riwayat ini telah otomatis tercatat ke: server/data/log_pengujian.csv")

if __name__ == "__main__":
    main()

