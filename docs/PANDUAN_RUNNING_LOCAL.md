# PANDUAN MENJALANKAN SISTEM DI LAPTOP LOKAL (WINDOWS)
**Implementasi Sistem Kendali Lampu Pintar Menggunakan Deep Learning (YOLOv8)**  
*Peneliti*: **Ikhsan Wahyudi (235520110043)** - S1 Informatika, Universitas Almuslim  

---

## 📋 DAFTAR ISI
1. [Prasyarat Sistem Laptop](#1-prasyarat-sistem-laptop)
2. [Cara Menjalankan Server Flask (1-Klik via File .BAT)](#2-cara-menjalankan-server-flask-1-klik-via-file-bat)
3. [Mengakses Web Dashboard Lokal](#3-mengakses-web-dashboard-lokal)
4. [Mencari Alamat IP Laptop untuk ESP32-S3 (Satu Jaringan Wi-Fi)](#4-mencari-alamat-ip-laptop-untuk-esp32-s3-satu-jaringan-wi-fi)
5. [Pengujian Mandiri Tanpa Hardware Fisik (Simulasi)](#5-pengujian-mandiri-tanpa-hardware-fisik-simulasi)
   * [Simulasi 1: Pengiriman Foto Uji via Skrip Python](#simulasi-1-pengiriman-foto-uji-via-skrip-python)
   * [Simulasi 2: Simulator Webcam Laptop Real-Time (1-Klik)](#simulasi-2-simulator-webcam-laptop-real-time-1-klik)
   * [Simulasi 3: Suite Pengujian Otomatis Matriks Bab V Skripsi (1-Klik)](#simulasi-3-suite-pengujian-otomatis-matriks-bab-v-skripsi-1-klik)
6. [Melihat dan Mengekspor Data Log Pengujian (CSV)](#6-melihat-dan-mengekspor-data-log-pengujian-csv)
7. [Troubleshooting & Solusi Error Lokal](#7-troubleshooting--solusi-error-lokal)

---

## 1. Prasyarat Sistem Laptop

* **Sistem Operasi**: Windows 10 atau Windows 11 (64-bit).
* **Python**: Python 3.11.x telah terpasang.
* **Virtual Environment (`venv`)**: Sudah tersedia di direktori utama `D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP\venv` lengkap dengan seluruh pustaka (Flask, Ultralytics YOLOv8, OpenCV, Pillow, PyTorch CPU).
* **Model AI**: Berkas model `model/yolov8n.pt` (6.2 MB) sudah tersedia di folder `model/`.

---

## 2. Cara Menjalankan Server Flask (1-Klik via File .BAT)

Cara paling mudah dan cepat untuk menjalankan server di laptop adalah menggunakan peluncur otomatis yang sudah disiapkan:

1. Buka folder proyek di Windows Explorer:
   ```text
   D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
   ```
2. Temukan file bernama **`run_server.bat`**.
3. **Klik 2x (Double-Click)** pada file **`run_server.bat`**.
4. Jendela terminal CMD akan terbuka dan otomatis mendeteksi environment `venv`.
5. Tunggu 2–4 detik hingga muncul pesan:
   ```text
   ==============================================================================
     PELADEN LOKAL SISTEM KENDALI LAMPU PINTAR (FLASK + YOLOV8)
     Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
   ==============================================================================

   [OK] Menggunakan Virtual Environment: venv
   [YOLO] Memuat model pretrained lokal: D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP\model\yolov8n.pt
   [YOLO] Mode Pemetaan Cerdas Aktif: COCO 80 Kelas -> 6 Kelas Target Skripsi...
    * Serving Flask app 'app'
    * Running on http://127.0.0.1:5000
    * Running on http://0.0.0.0:5000
   ```
6. **PENTING**: Biarkan jendela terminal ini tetap terbuka selama sistem sedang digunakan.

> **Tips Jika Menggunakan Command Prompt Manual:**  
> Anda juga dapat menjalankan via CMD biasa:
> ```cmd
> cd /d D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
> .\venv\Scripts\python.exe server\app.py
> ```

---

## 3. Mengakses Web Dashboard Lokal

Setelah server Flask aktif:
1. Buka peramban (browser) pilihan Anda (Google Chrome, Microsoft Edge, atau Mozilla Firefox).
2. Ketikkan alamat berikut pada bilah URL:
   👉 **`http://localhost:5000`** atau **`http://127.0.0.1:5000`**
3. **Fitur Web Dashboard**:
   * **Status Sistem Real-Time**: Menampilkan kategori objek yang melintas, bounding box deteksi, persentase kepercayaan (*confidence score*), waktu komputasi inferensi (*inference time ms*), dan aksi relay lampu (**RELAY ON / RELAY OFF**).
   * **Live Preview**: Menampilkan citra terakhir yang ditangkap dan diproses beserta kotak deteksinya.
   * **Tabel Riwayat Deteksi**: Menampilkan 15 data pengujian terakhir secara otomatis (*auto-refresh* tiap 2 detik).
   * **Tombol Ekspor CSV**: Mengunduh seluruh riwayat pengujian ke format spreadsheet Excel/CSV untuk keperluan data penelitian Bab V Skripsi.

---

## 4. Mencari Alamat IP Laptop untuk ESP32-S3 (Satu Jaringan Wi-Fi)

Jika Anda ingin menguji menggunakan perangkat keras fisik ESP32-S3-CAM di jaringan Wi-Fi lokal:
1. Pastikan laptop Anda dan ESP32-S3 terhubung ke jaringan Wi-Fi / Hotspot yang sama (frekuensi 2.4 GHz).
2. Di laptop Anda, tekan tombol **Windows + R**, ketik `cmd`, lalu tekan **Enter**.
3. Di jendela Command Prompt, ketik:
   ```cmd
   ipconfig
   ```
4. Cari bagian **Wireless LAN adapter Wi-Fi** dan temukan baris **IPv4 Address**, misalnya:
   ```text
   IPv4 Address. . . . . . . . . . . : 192.168.1.5
   ```
5. Buka file firmware Arduino `firmware/smart_lamp_esp32s3/config.h`:
   * Masukkan IP tersebut ke baris:
     ```cpp
     #define SERVER_HOST "192.168.1.5"
     #define SERVER_PORT 5000
     ```

---

## 5. Pengujian Mandiri Tanpa Hardware Fisik (Simulasi)

Anda dapat menguji seluruh fungsi deteksi AI, keputusan relay, pencatatan log CSV, dan visualisasi dashboard tanpa harus merakit perangkat keras fisik.

### Simulasi 1: Pengiriman Foto Uji via Skrip Python
Pastikan `run_server.bat` sedang berjalan di jendela lain, lalu buka CMD baru:
```cmd
cd /d D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
.\venv\Scripts\python.exe tools\simulate_esp32.py sample_images\uji_manusia.jpg
```
* **Hasil di Terminal**: Akan muncul respons JSON server (`category: "manusia"`, `lamp_action: "ON"`).
* **Hasil di Browser**: Web Dashboard langsung ter-update menampilkan foto manusia dan status lampu hijau **RELAY ON**.

---

### Simulasi 2: Simulator Webcam Laptop Real-Time (1-Klik)
Simulator ini menggunakan webcam laptop Anda seolah-olah menjadi kamera ESP32-S3:
1. Pastikan `run_server.bat` sedang aktif.
2. Di folder `D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP`, **klik 2x** file:
   👉 **`run_webcam_simulator.bat`**
3. Jendela kamera laptop Anda akan terbuka secara langsung.
4. **Cara Penggunaan**:
   * Arahkan kamera ke diri Anda atau objek lain.
   * Tekan tombol **SPASI** pada keyboard untuk mensimulasikan sensor PIR mendeteksi gerakan.
   * Frame kamera akan dijepret dan dikirim ke server.
   * Tekan tombol **Q** atau **ESC** untuk menutup simulator webcam.

---

### Simulasi 3: Suite Pengujian Otomatis Matriks Bab V Skripsi (1-Klik)
Untuk mengambil data hasil pengujian Bab V secara cepat:
1. Pastikan `run_server.bat` sedang aktif.
2. **Klik 2x** file:
   👉 **`run_test_matrix.bat`**
3. Skrip akan secara otomatis mengeksekusi 8 skenario pengujian standar skripsi:
   * **SK-01**: Latar Belakang Kosong $\rightarrow$ Lampu OFF
   * **SK-02**: Manusia Jarak Dekat (1,5 m) $\rightarrow$ Lampu ON
   * **SK-03**: Manusia Jarak Sedang (3 m) $\rightarrow$ Lampu ON
   * **SK-04**: Manusia Jarak Jauh (5 m) $\rightarrow$ Lampu ON
   * **SK-05**: Hewan Kucing $\rightarrow$ Lampu OFF
   * **SK-06**: Hewan Lembu/Kambing $\rightarrow$ Lampu OFF
   * **SK-07**: Kendaraan Bermotor $\rightarrow$ Lampu ON
   * **SK-08**: Multi-Objek (Manusia + Kendaraan) $\rightarrow$ Lampu ON
4. Seluruh hasil langsung tercatat di tabel dashboard dan masuk ke file CSV.

---

## 6. Melihat dan Mengekspor Data Log Pengujian (CSV)

Setiap deteksi yang diproses oleh server secara otomatis dicatat ke dalam berkas:
```text
D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP\server\data\log_pengujian.csv
```
* Kolom data yang dicatat mencakup:
  `timestamp`, `file_name`, `category`, `detected_classes`, `confidence`, `inference_time_ms`, `lamp_action`, `relay_status`.
* Anda dapat membuka file ini langsung menggunakan **Microsoft Excel** atau mengeklik tombol hijau **"Unduh Laporan CSV"** pada tampilan Web Dashboard.

---

## 7. Troubleshooting & Solusi Error Lokal

| Kendala | Penyebab | Solusi |
|---|---|---|
| **`No module named 'flask'`** | Menjalankan dengan Python global yang belum di-install package | Gunakan peluncur `run_server.bat` atau panggil `.\venv\Scripts\python.exe`. |
| **`Address already in use (Port 5000)`** | Masih ada proses Flask sebelumnya yang berjalan di latar belakang | Buka Task Manager $\rightarrow$ matikan proses `Python`, lalu jalankan kembali `run_server.bat`. |
| **ESP32 Gagal Konek ke Laptop** | Firewall Windows memblokir port 5000 atau beda jaringan Wi-Fi | Pastikan Wi-Fi sama dan izinkan Python melalui Windows Defender Firewall (Private Network). |
| **Kamera Webcam Tidak Terbuka** | Webcam sedang digunakan aplikasi lain (Zoom/Teams/Kamera) | Tutup aplikasi lain yang mengakses webcam sebelum menjalankan `run_webcam_simulator.bat`. |
