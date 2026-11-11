# SISTEM KENDALI LAMPU PINTAR MENGGUNAKAN DEEP LEARNING (YOLOv8)
### Deteksi dan Pelacakan Objek yang Melintas Berbasis ESP32-S3-CAM & Flask Dashboard

* **Peneliti**: **Ikhsan Wahyudi** (NPM: **235520110043**)
* **Program Studi**: S1 - Informatika, Fakultas Ilmu Komputer, Universitas Almuslim
* **Dosen Pembimbing I**: Dedy Armiady, S.Kom., M.Kom.
* **Dosen Pembimbing II**: Budi Handoyo, M.Kom.
* **Status Sistem**: Final v1.0 (Fixed Workflow & Pretrained Ready)

---

## 📑 DAFTAR ISI
1. [Gambaran Umum Sistem & Cara Kerja](#1-gambaran-umum-sistem--cara-kerja)
2. [Struktur Direktori Proyek](#2-struktur-direktori-proyek)
3. [Langkah 1: Instalasi Python di Laptop](#3-langkah-1-instalasi-python-di-laptop)
4. [Langkah 2: Menyiapkan Virtual Environment & Library](#4-langkah-2-menyiapkan-virtual-environment--library)
5. [Langkah 3: Menjalankan Server Flask & Web Dashboard](#5-langkah-3-menjalankan-server-flask--web-dashboard)
6. [Langkah 4: Pengujian Tanpa Hardware Fisik (Simulasi)](#6-langkah-4-pengujian-tanpa-hardware-fisik-simulasi)
7. [Langkah 5: Perakitan Hardware & Kalibrasi LM2596](#7-langkah-5-perakitan-hardware--kalibrasi-lm2596)
8. [Langkah 6: Konfigurasi & Upload Firmware ESP32-S3-CAM](#8-langkah-6-konfigurasi--upload-firmware-esp32-s3-cam)
9. [Langkah 7: Pengambilan Data Pengujian Bab V (Ekspor CSV)](#9-langkah-7-pengambilan-data-pengujian-bab-v-ekspor-csv)
10. [Langkah 8 (Opsional): Pelatihan Model Khusus (best.pt)](#10-langkah-8-opsional-pelatihan-model-khusus-bestpt)
11. [Langkah 9: Hosting Server ke cPanel Rumahweb (ikhsan.mhsfikom.my.id)](#11-langkah-9-hosting-server-ke-cpanel-rumahweb-ikhsanmhsfikommyid)
12. [Troubleshooting & Pemecahan Masalah Umum](#12-troubleshooting--pemecahan-masalah-umum)

---

## 1. Gambaran Umum Sistem & Cara Kerja

Sistem ini memecahkan masalah lampu otomatis konvensional yang menyala liar setiap kali ada gerakan tanpa membedakan objek. Dengan kombinasi sensor PIR dan model visual **YOLOv8n**:
1. **Mode Siaga**: ESP32-S3 terhubung ke Wi-Fi lokal, Relay pada posisi **OFF** (Lampu LED 12V 5W padam).
2. **Pemicu Gerakan (PIR HIGH)**: Sensor PIR mendeteksi radiasi inframerah pergerakan objek $\rightarrow$ mengirim sinyal HIGH (3,3V) ke **GPIO 21** *(atau GPIO 13)*.
3. **Lampu Kilat (Flash 500 ms)**: ESP32-S3 menyalakan lampu 12V via Relay (**GPIO 14**) selama 500 ms untuk pencahayaan, menangkap 1 frame foto VGA (640x480), lalu langsung mematikan lampu kembali.
4. **Transmisi HTTP POST**: Foto dikirim ke Server Flask (`http://<IP_LAPTOP>:5000/api/detect`) via Wi-Fi lokal.
5. **Inferensi YOLOv8**: Peladen lokal mendeteksi objek dengan ambang confidence $\ge 0.50$ dan menerapkan matriks keputusan:
   * **Manusia / Kendaraan (Mobil/Motor)** $\rightarrow$ **Relay ON** (Lampu utama MENYALA 10 detik + fitur *Auto-Extend* jika PIR masih mendeteksi gerakan).
   * **Hewan (Kucing/Lembu/Kambing) / Objek Lain** $\rightarrow$ **Relay OFF** (Lampu tetap PADAM).
   * **Fail-Safe** (Server mati / Timeout > 5 detik) $\rightarrow$ **Relay OFF** (Lampu dipaksa tetap PADAM demi keamanan).
6. **Waktu Tenang (Cooldown)**: Jeda 3 detik setelah lampu padam guna mencegah *false re-triggering*.

---

## 2. Struktur Direktori Proyek

```text
SMART_LAMP/
│
├── passenger_wsgi.py                # WSGI Entry Point cPanel Phusion Passenger
├── requirements.txt                 # Daftar pustaka dependensi Python
├── run_server.bat                   # [1-Klik] Menjalankan Server Flask & Dashboard
├── run_test_matrix.bat              # [1-Klik] Menjalankan Pengujian Matriks Bab V
├── run_webcam_simulator.bat         # [1-Klik] Simulator Webcam Laptop Real-Time
│
├── firmware/
│   └── smart_lamp_esp32s3/
│       ├── smart_lamp_esp32s3.ino   # Firmware Arduino ESP32-S3-CAM
│       ├── camera_pins.h            # Konfigurasi pinout kamera OV2640
│       └── config.h                 # Konfigurasi Wi-Fi, URL Cloud / IP Lokal, & Pin GPIO
│
├── server/
│   ├── app.py                       # Aplikasi Backend Flask & Endpoint /api/detect
│   ├── detector.py                  # Mesin Inferensi YOLOv8n (Offline Ready + Class Mapping)
│   ├── logger.py                    # Pencatat pengujian otomatis ke CSV secara persisten
│   ├── webcam.py                    # Modul stream & capture OpenCV Webcam laptop
│   ├── data/
│   │   └── log_pengujian.csv        # Berkas CSV rekapitulasi data uji Bab V Skripsi
│   ├── static/
│   ├── templates/
│   │   └── index.html               # Web Dashboard lokal (Bootstrap 5 & Auto-refresh)
│   └── uploads/                     # Arsip foto deteksi kamera
│
├── venv/                            # Virtual Environment Python Laptop Windows
│
├── docs/
│   ├── PANDUAN_RUNNING_LOCAL.md     # Panduan 1-klik running di laptop Windows
│   ├── PANDUAN_HOSTING_CPANEL.md    # Panduan lengkap hosting cPanel Rumahweb
│   ├── PANDUAN_HOSTING_SERVER.md    # Indeks panduan deployment
│   └── PANDUAN_PENGKABELAN_DAN_KALIBRASI.md
│
├── model/
│   ├── yolov8n.pt                   # Model Pretrained Lokal (6.2 MB, SUDAH TERSEDIA)
│   ├── best.pt                      # (Opsional) Letakkan bobot hasil custom training di sini
│   └── README.md                    # Dokumentasi penggunaan model
│
├── sample_images/                   # Aset foto uji coba mandiri
│   ├── uji_manusia.jpg              # Foto uji SK-02 (Manusia -> Lampu ON)
│   ├── uji_manusia_bus.jpg          # Foto uji SK-03 (Kendaraan -> Lampu ON)
│   └── uji_kucing.jpg               # Foto uji SK-04 (Hewan -> Lampu OFF)
│
├── tools/
│   ├── simulate_esp32.py            # Simulator pengiriman citra ESP32-S3 via terminal
│   ├── test_bab5_matrix.py          # Skrip pengujian otomatis matriks Bab V (SK-01 s/d SK-08)
│   └── webcam_simulator.py          # Simulator webcam laptop interaktif
│
├── docs/
│   ├── DRAFT_BAB_IV_DAN_BAB_V_SKRIPSI.md   # Format naskah pengujian skripsi
│   └── PANDUAN_PENGKABELAN_DAN_KALIBRASI.md # Diagram skematik & panduan multimeter LM2596
│
├── train_yolov8.py                  # Skrip otomatisasi pelatihan dataset 6 kelas
└── README.md                        # Panduan lengkap dokumentasi operasional
```

---

## 3. Langkah 1: Instalasi Python di Laptop

Jika di laptop Anda belum terpasang Python, ikuti petunjuk berikut:

1. Buka browser dan unduh installer resmi: **[Python 3.10.11](https://www.python.org/downloads/release/python-31011/)** atau **[Python 3.11.x](https://www.python.org/downloads/)** (Pilih varian *Windows installer 64-bit*).
2. Jalankan file `.exe` yang telah diunduh.
3. ⚠️ **LANGKAH PALING KRUSIAL**:
   * Di bagian bawah jendela awal instalasi, **WAJIB CENTANG**:
     > `[X] Add python.exe to PATH`
4. Klik **Install Now**. Tunggu sampai selesai (status *Setup was successful*).
5. Verifikasi instalasi:
   * Buka **Command Prompt (CMD)** baru.
   * Ketik:
     ```cmd
     python --version
     ```
   * Jika muncul `Python 3.10.x` atau `Python 3.11.x`, berarti Python sudah siap digunakan!

---

## 4. Langkah 2: Menyiapkan Virtual Environment & Library

Kami telah menyediakan skrip otomatisasi 1-klik agar Anda tidak perlu menginstall pustaka satu per satu secara manual.

### Cara A: Menggunakan Skrip 1-Klik (Sangat Disarankan)
1. Buka File Explorer, masuk ke folder: `d:\LABIL\BIMBEL\IKHSAN\SMART_LAMP\server`.
2. Klik ganda pada file: **`setup_env.bat`**.
3. Jendela terminal akan muncul dan secara otomatis:
   * Membuat lingkungan virtual (`venv`).
   * Memperbarui `pip`.
   * Menginstall seluruh pustaka: `Flask`, `ultralytics` (YOLOv8), `opencv-python-headless`, `pillow`, `requests`, dan `numpy`.
4. Tunggu hingga muncul tulisan `[SELESAI] Penyiapan virtual environment berhasil!`. Tekan tombol apa saja untuk menutup jendela.

### Cara B: Menggunakan Terminal Manual
Jika Anda lebih suka menggunakan Command Prompt (CMD):
```cmd
cd /d d:\LABIL\BIMBEL\IKHSAN\SMART_LAMP\server
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Langkah 3: Menjalankan Server Flask & Web Dashboard

### Cara Menjalankan:
1. Klik ganda file: **`run_server.bat`** langsung di folder utama proyek (atau di dalam folder `server`).
   *(Atau jalankan via CMD: `call server\venv\Scripts\activate && python server\app.py`)*.
3. Jendela terminal akan menampilkan informasi berikut:
   ```text
   =================================================================
     PELADEN LOKAL SISTEM KENDALI LAMPU PINTAR (FLASK + YOLOV8)
     Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
   =================================================================
   [YOLO] Memuat model pretrained lokal: ...\model\yolov8n.pt
   [YOLO] Mode Pemetaan Cerdas Aktif: COCO 80 Kelas -> 6 Kelas Target Skripsi...
   Web Dashboard dapat diakses pada: http://localhost:5000
   Endpoint Deteksi ESP32-S3        : http://<IP_LAPTOP_ANDA>:5000/api/detect
   ```
4. Buka browser (Google Chrome / Edge) di laptop Anda dan buka alamat:
   👉 **`http://localhost:5000`**

### Tampilan Web Dashboard:
* **Kartu Status Lampu**: Indikator hijau menyala pulsasi saat `MENYALA (ON)` dan abu-abu saat `PADAM (OFF)`.
* **Kategori Objek**: Label dinamis (Manusia, Kendaraan, Hewan, Objek Lain).
* **Confidence & Latensi**: Menampilkan nilai kepastian deteksi (%) dan waktu proses inferensi AI (ms).
* **Live Snapshot**: Menampilkan citra terbaru lengkap dengan kotak hijau/merah (*bounding box*) dan teks deteksi.
* **Tabel Rekapitulasi Data**: Riwayat seluruh pengujian real-time.
* **Tombol Unduh Rekap CSV**: Satu klik untuk mengunduh berkas Excel/CSV untuk Bab V skripsi Anda.

---

## 6. Langkah 4: Pengujian Tanpa Hardware Fisik (Simulasi)

Anda dapat langsung memverifikasi keakuratan deteksi AI dan logika relay bahkan sebelum menyambungkan ESP32-S3 fisik.

### Metode 1: Melalui Formulir Web Dashboard
1. Buka dashboard di `http://localhost:5000`.
2. Pada panel sebelah kanan (*Uji Coba Deteksi Manual*), klik **Choose File / Pilih File**.
3. Masuk ke folder `sample_images` dan pilih salah satu foto:
   * Pilih `uji_manusia.jpg` $\rightarrow$ Klik **Deteksi** $\rightarrow$ Status Lampu berubah menjadi **MENYALA (ON)**.
   * Pilih `uji_kucing.jpg` $\rightarrow$ Klik **Deteksi** $\rightarrow$ Status Lampu tetap **PADAM (OFF)**.
   * Pilih `uji_manusia_bus.jpg` $\rightarrow$ Klik **Deteksi** $\rightarrow$ Status Lampu berubah menjadi **MENYALA (ON)**.

### Metode 2: Menggunakan Skrip Simulator ESP32 (`simulate_esp32.py`)
Skrip ini mengirimkan byte biner JPEG mentah dengan header `Content-Type: image/jpeg` persis seperti yang dilakukan oleh ESP32-S3:
```cmd
cd /d d:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
call server\venv\Scripts\activate.bat
python tools\simulate_esp32.py sample_images\uji_manusia.jpg
```
Output terminal akan menampilkan detail respon JSON, latensi jaringan, serta aksi pin hardware.

### Metode 3: Uji Otomatis Seluruh Matriks Bab V (`test_bab5_matrix.py`)
Untuk menguji seluruh skenario secara berurutan dan mendapatkan tabel rekap validasi:
```cmd
cd /d d:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
call server\venv\Scripts\activate.bat
python tools\test_bab5_matrix.py
```

---

## 7. Langkah 5: Perakitan Hardware & Kalibrasi LM2596

> [!CAUTION]
> **BAHAYA KERUSAKAN**: Adaptor Anda bertegangan **12V DC**. Pin ESP32-S3 hanya mentoleransi maksimal **5,0V DC**. **JANGAN** menyambungkan kabel output LM2596 ke ESP32 sebelum tegangan diukur dengan multimeter!

### Panduan Kalibrasi Tegangan (Wajib Dilakukan Pertama Kali):
1. Sambungkan kabel positif (+) adaptor 12V ke terminal **IN+** modul LM2596.
2. Sambungkan kabel negatif (-) adaptor 12V ke terminal **IN-** modul LM2596.
3. Nyalakan adaptor ke stopkontak PLN.
4. Siapkan **Multimeter Digital** pada skala pengukuran **DC Voltage (20V)**.
5. Tempelkan probe merah ke terminal **OUT+** dan probe hitam ke terminal **OUT-** LM2596.
6. Gunakan obeng minus kecil untuk memutar trimpot biru pada modul LM2596 (putar berlawanan arah jarum jam) hingga multimeter membaca **tepat 5,00 Volt**.
7. Cabut adaptor dari stopkontak. Modul step-down kini aman digunakan.

### Tabel Pengkabelan Lengkap:
| Komponen | Terminal Pin | Terhubung Ke |
|---|---|---|
| **LM2596 (Output 5V)** | `OUT+` (+5.0V) | Pin `5V` ESP32, Pin `VCC` PIR HC-SR505, Pin `VCC` Relay 5V |
| **LM2596 (Output GND)**| `OUT-` (GND) | Pin `GND` ESP32, Pin `GND` PIR HC-SR505, Pin `GND` Relay 5V |
| **Sensor PIR HC-SR505**| Pin `OUT` (Sinyal)| Pin **GPIO 21** ESP32-S3 *(Atau GPIO 13 jika rangkaian sudah terpasang)* |
| **Modul Relay 5V** | Pin `IN` (Trigger) | Pin **GPIO 14** ESP32-S3 |
| **Adaptor 12V** | Positif (+12V) | Terminal `COM` Relay & Terminal `IN+` LM2596 |
| **Modul Relay 5V** | Terminal `NO` | Kabel Positif (+) Lampu LED 12V 5W |
| **Adaptor 12V** | Negatif (GND) | Kabel Negatif (-) Lampu LED 12V 5W & Terminal `IN-` LM2596 |

*(Panduan gambar skematik lengkap dapat dilihat di [docs/PANDUAN_PENGKABELAN_DAN_KALIBRASI.md](file:///d:/LABIL/BIMBEL/IKHSAN/SMART_LAMP/docs/PANDUAN_PENGKABELAN_DAN_KALIBRASI.md))*

---

## 8. Langkah 6: Konfigurasi & Upload Firmware ESP32-S3-CAM

### 1. Dapatkan IP Address Laptop Anda
1. Buka CMD di laptop, ketik: `ipconfig` lalu tekan Enter.
2. Cari adaptor **Wireless LAN adapter Wi-Fi** dan catat **IPv4 Address** (contoh: `192.168.1.18`).
3. Pastikan laptop dan ESP32-S3 terhubung ke **satu jaringan Wi-Fi/Hotspot yang sama (Frekuensi 2,4 GHz)**.

### 2. Atur Berkas `config.h`
Buka berkas [`firmware/smart_lamp_esp32s3/config.h`](file:///d:/LABIL/BIMBEL/IKHSAN/SMART_LAMP/firmware/smart_lamp_esp32s3/config.h) menggunakan Arduino IDE atau editor teks:
```cpp
// 1. Masukkan Nama & Password Wi-Fi Anda
#define WIFI_SSID       "Hotspot_Saya"
#define WIFI_PASSWORD   "password1234"

// 2. Masukkan IPv4 Laptop Anda yang didapat dari perintah 'ipconfig'
#define SERVER_HOST     "192.168.1.18"
#define SERVER_PORT     5000
#define SERVER_ENDPOINT "/api/detect"

// 3. Konfigurasi Relay (Default: Active LOW untuk kebanyakan modul relay 5V)
#define RELAY_ACTIVE_LOW  true
```

### 3. Pengaturan Board pada Arduino IDE (Khusus ESP32-S3 N16R8)
1. Buka file [`firmware/smart_lamp_esp32s3/smart_lamp_esp32s3.ino`](file:///d:/LABIL/BIMBEL/IKHSAN/SMART_LAMP/firmware/smart_lamp_esp32s3/smart_lamp_esp32s3.ino) di Arduino IDE.
2. Di menu **Tools**, atur konfigurasi berikut dengan teliti (Wajib sesuai spesifikasi N16R8):
   * **Board**: `"ESP32S3 Dev Module"`
   * **USB CDC On Boot**: `"Enabled"` *(Penting jika colok kabel ke port USB Type-C native ESP32-S3)*
   * **CPU Frequency**: `"240MHz (WiFi)"`
   * **Flash Mode**: `"QIO 80MHz"`
   * **Flash Size**: `"16MB (128Mb)"` ⚠️ *(Wajib 16MB karena varian modul N16)*
   * **Partition Scheme**: `"16M Flash (3MB APP/9.9MB FATFS)"` atau `"Huge App (3MB No OTA/1MB SPIFFS)"`
   * **PSRAM**: `"OPI PSRAM"` ⚠️ *(SANGAT KRUSIAL: Varian R8 memiliki 8MB Octal PSRAM. Jangan pilih Disabled atau QSPI!)*
   * **Upload Mode**: `"UART0 / Hardware CDC"`
   * **Upload Speed**: `"921600"` (atau `"460800"`)
   * **Port**: Pilih Port COM board ESP32-S3 Anda (misal `COM3`, `COM4`, dsb).
3. Tekan tombol **Upload** (ikon panah ke kanan).
4. Setelah proses upload tuntas, buka **Serial Monitor** pada baud rate **115200**. Firmware akan menampilkan informasi diagnostik:
   ```text
   [INFO HW] Chip: ESP32-S3 (Rev 1/2)
   [INFO HW] Flash Size: 16 MB (N16)
   [INFO HW] PSRAM Size: 8 MB (Octal PSRAM R8 Aktif)
   [OK] Kamera OV2640 berhasil diinisialisasi (VGA 640x480).
   ```

---

## 9. Langkah 7: Pengambilan Data Pengujian Bab V (Ekspor CSV)

Setiap kali sistem melakukan siklus deteksi (baik dari simulasi maupun dari ESP32 fisik), sistem secara otomatis mencatat pengujian ke:
📁 **`server/data/log_pengujian.csv`**

Format kolom data CSV yang tersimpan:
| No | Timestamp | Nama_File | Kelas_Terdeteksi | Kategori | Confidence | Waktu_Inferensi_ms | Status_Lampu_Keputusan | Keterangan |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-08 01:35:10 | detect_20261108_013510.jpg | manusia | manusia | 0.92 | 134.5 | ON | Model Pretrained (Fallback) |
| 2 | 2026-11-08 01:36:22 | detect_20261108_013622.jpg | kucing | hewan | 0.88 | 129.2 | OFF | Model Pretrained (Fallback) |

**Cara Mengunduh Data**:
* Klik tombol **Unduh Rekap CSV** di bagian pojok kanan atas Web Dashboard (`http://localhost:5000`).
* File CSV ini dapat langsung Anda buka menggunakan Microsoft Excel untuk pembuatan grafik, tabel, dan analisis data Bab V Skripsi Anda!

---

## 10. Langkah 8 (Opsional): Pelatihan Model Khusus (best.pt)

Jika dosen pembimbing atau penguji Anda meminta model yang dilatih khusus (*custom fine-tuning*) menggunakan dataset foto lingkungan sekitar:

1. Buat akun di **[Roboflow](https://roboflow.com/)**, unggah foto-foto objek Anda, beri anotasi *bounding box* dengan 6 nama kelas:
   `manusia`, `mobil`, `motor`, `kucing`, `lembu`, `kambing`.
2. Ekspor dataset dengan format **YOLOv8** (akan menghasilkan file `data.yaml`).
3. Ekstrak folder dataset tersebut ke direktori proyek (misal di folder `dataset/`).
4. Jalankan skrip pelatihan otomatis:
   ```cmd
   cd /d d:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
   call server\venv\Scripts\activate.bat
   python train_yolov8.py
   ```
5. Masukkan letak path `data.yaml`. Skrip akan otomatis melatih model selama 75 epoch dan menyalin bobot terbaik (**`best.pt`**) ke folder `model/`.
6. Restart server Flask (`run_server.bat`). Server akan otomatis beralih menggunakan `best.pt` khusus Anda!

---

## 11. Langkah 9: Hosting Server ke cPanel Rumahweb (ikhsan.mhsfikom.my.id)

Proyek ini telah dikonfigurasi secara optimal untuk **cPanel Shared Hosting Rumahweb** ("Setup Python App" berbasis Phusion Passenger) dengan domain:
👉 **`https://ikhsan.mhsfikom.my.id`**

### Panduan Lengkap:
* **Panduan Hosting cPanel**: Baca selengkapnya di [docs/PANDUAN_HOSTING_CPANEL.md](docs/PANDUAN_HOSTING_CPANEL.md) untuk panduan pembuatan zip, ekstraksi di cPanel, instalasi PyTorch CPU, konfigurasi thread CloudLinux, hingga pengujian remote.
* **Panduan Menjalankan di Laptop Lokal**: Baca selengkapnya di [docs/PANDUAN_RUNNING_LOCAL.md](docs/PANDUAN_RUNNING_LOCAL.md) untuk 1-klik running di laptop via `.bat`, webcam simulator, dan uji matriks Bab V.

### Ringkasan Konfigurasi ESP32-S3 ke Cloud:
Pada file `firmware/smart_lamp_esp32s3/config.h`, cukup isi URL endpoint cloud Anda:
```cpp
#define CLOUD_SERVER_URL "https://ikhsan.mhsfikom.my.id/api/detect"
```
Firmware ESP32-S3 otomatis menggunakan protokol HTTPS aman (`WiFiClientSecure`) untuk mentransmisikan foto langsung melalui internet.

---

## 12. Troubleshooting & Pemecahan Masalah Umum

### 1. `python` tidak dikenali di Command Prompt
* **Penyebab**: Opsi *Add python.exe to PATH* tidak dicentang saat instalasi Python.
* **Solusi**: Buka kembali file installer Python `.exe`, pilih *Modify*, lalu pastikan opsi *Add Python to environment variables* dicentang.

### 2. ESP32-S3 Serial Monitor menampilkan `[ERROR] Gagal inisialisasi kamera OV2640!`
* **Penyebab**: Pengaturan PSRAM di Arduino IDE belum diaktifkan atau board kekurangan daya.
* **Solusi**: Di menu *Tools* Arduino IDE, pastikan **PSRAM** diatur ke **OPI PSRAM**. Pastikan tegangan suplai LM2596 stabil di 5,0V.

### 3. Lampu LED menyala terbalik (Mati saat terdeteksi manusia, menyala saat tidak ada objek)
* **Penyebab**: Karakteristik modul relay Anda adalah *Active HIGH*, sedangkan konfigurasi default di kode adalah *Active LOW*.
* **Solusi**: Buka `config.h`, ubah baris:
  ```cpp
  #define RELAY_ACTIVE_LOW  false  // Ubah dari true menjadi false
  ```
  Lalu upload ulang ke ESP32.

### 4. ESP32 menampilkan error `[HTTP] Gagal kirim / Timeout`
* **Penyebab**: IP Laptop di `config.h` salah, atau laptop dan ESP32 tidak berada dalam satu jaringan Wi-Fi, atau Firewall Windows memblokir port 5000.
* **Solusi**:
  * Pastikan laptop dan ESP32 tersambung ke hotspot Wi-Fi yang sama.
  * Cek kembali IP laptop via perintah `ipconfig`.
  * Izinkan aplikasi Python melewati Windows Defender Firewall untuk jaringan privat.
