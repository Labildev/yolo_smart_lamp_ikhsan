# PANDUAN LENGKAP HOSTING CPANEL RUMAHWEB ("SETUP PYTHON APP")
**Sistem Kendali Lampu Pintar Menggunakan Deep Learning (YOLOv8)**  
*Peneliti*: **Ikhsan Wahyudi (235520110043)** - S1 Informatika, Universitas Almuslim  
*Target Domain*: **`https://ikhsan.mhsfikom.my.id`**  

---

## 📋 DAFTAR ISI
1. [Gambaran Arsitektur Hosting cPanel](#1-gambaran-arsitektur-hosting-cpanel)
2. [Langkah 1: Konfigurasi Subdomain di cPanel](#langkah-1-konfigurasi-subdomain-di-cpanel)
3. [Langkah 2: Menyiapkan Proyek di Menu "Setup Python App"](#langkah-2-menyiapkan-proyek-di-menu-setup-python-app)
4. [Langkah 3: Menyiapkan File ZIP di Laptop Windows](#langkah-3-menyiapkan-file-zip-di-laptop-windows)
5. [Langkah 4: Upload & Ekstrak di cPanel File Manager](#langkah-4-upload--ekstrak-di-cpanel-file-manager)
6. [Langkah 5: Instalasi Dependensi Python di cPanel (PyTorch CPU Hemat Kuota)](#langkah-5-instalasi-dependensi-python-di-cpanel-pytorch-cpu-hemat-kuota)
7. [Langkah 6: Konfigurasi Pembatasan Thread CloudLinux (Fix OpenBLAS Crash)](#langkah-6-konfigurasi-pembatasan-thread-cloudlinux-fix-openblas-crash)
8. [Langkah 7: Restart Aplikasi & Akses Web Dashboard](#langkah-7-restart-aplikasi--akses-web-dashboard)
9. [Langkah 8: Pengujian Endpoint API dari Laptop](#langkah-8-pengujian-endpoint-api-dari-laptop)
10. [Langkah 9: Konfigurasi Firmware ESP32-S3-CAM (Koneksi Cloud HTTPS)](#langkah-9-konfigurasi-firmware-esp32-s3-cam-koneksi-cloud-https)
11. [Troubleshooting & Pemecahan Masalah cPanel](#troubleshooting--pemecahan-masalah-cpanel)

---

## 1. Gambaran Arsitektur Hosting cPanel

Di hosting bersama (Shared Hosting) Rumahweb, backend Python berjalan menggunakan modul **CloudLinux Phusion Passenger**:
* **Entry Point WSGI**: `passenger_wsgi.py` bertindak sebagai penghubung antara web server Apache/LiteSpeed dengan aplikasi Flask `server/app.py`.
* **Virtual Environment**: Terletak otomatis di `/home/mhsr9595/virtualenv/smart_lamp/3.11/`.
* **Keamanan HTTPS**: Subdomain `ikhsan.mhsfikom.my.id` otomatis dilindungi SSL gratis (Let's Encrypt / AutoSSL cPanel).
* **Endpoint Utama**:
  * Web Dashboard: `https://ikhsan.mhsfikom.my.id`
  * API Deteksi ESP32-S3: `https://ikhsan.mhsfikom.my.id/api/detect`
  * API Status & Health: `https://ikhsan.mhsfikom.my.id/api/health`

---

## Langkah 1: Konfigurasi Subdomain di cPanel

1. Masuk ke panel hosting cPanel Rumahweb Anda.
2. Cari menu **Domains** atau **Subdomains**.
3. Buat subdomain baru:
   * **Subdomain**: `ikhsan`
   * **Domain**: `mhsfikom.my.id`
   * **Document Root**: Biarkan default (misalnya `public_html/ikhsan` atau `ikhsan.mhsfikom.my.id`).
4. Klik **Create**. Pastikan SSL/HTTPS sudah aktif (terdapat gembok hijau di browser).

---

## Langkah 2: Menyiapkan Proyek di Menu "Setup Python App"

1. Di halaman utama cPanel, cari bagian **Software** $\rightarrow$ klik **Setup Python App**.
2. Klik tombol biru **Create Application**.
3. Isi parameter konfigurasi berikut dengan teliti:
   * **Python version**: Pilih **`3.11`** (wajib versi 3.11).
   * **Application root**: Ketik **`smart_lamp`** *(tanpa tanda petik, tanpa spasi di awal/akhir)*. Folder ini akan berada di `/home/mhsr9595/smart_lamp`.
   * **Application URL**: Pilih subdomain **`ikhsan.mhsfikom.my.id`**.
   * **Kotak subpath di sebelah kanan URL**: **BIARKAN KOSONG** *(jangan ketik tanda miring `/` atau spasi, agar website langsung terbuka di root domain)*.
   * **Application startup file**: Biarkan kosong *(default otomatis: `passenger_wsgi.py`)*.
   * **Application Entry point**: Biarkan kosong *(default otomatis: `application`)*.
4. Klik tombol **Create** di kanan atas.
5. Setelah berhasil terbuat, cPanel akan menampilkan baris perintah aktivasi virtualenv, contoh:
   ```bash
   source /home/mhsr9595/virtualenv/smart_lamp/3.11/bin/activate && cd /home/mhsr9595/smart_lamp
   ```

---

## Langkah 3: Menyiapkan File ZIP di Laptop Windows

Di laptop lokal Anda (`D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP`):

1. Buka folder proyek di **Windows Explorer**.
2. Tahan tombol **Ctrl** di keyboard Anda, lalu pilih (klik) **5 item** utama ini:
   * 📁 Folder **`model`** (berisi `yolov8n.pt`)
   * 📁 Folder **`sample_images`** (berisi foto uji)
   * 📁 Folder **`server`** (berisi `app.py`, `detector.py`, `logger.py`, `webcam.py`, `templates`, `static`)
   * 📄 File **`passenger_wsgi.py`**
   * 📄 File **`requirements.txt`**

> **⚠️ PENTING:**  
> **JANGAN** sertakan folder `venv`, `firmware`, `docs`, atau file `.docx`. Folder `venv` di laptop adalah binary Windows sebesar 1.1 GB yang tidak bisa berjalan di Linux cPanel. Dengan memilih 5 item di atas saja, ukuran zip hanya **~6.5 MB**.

3. **Klik Kanan** pada item yang ditandai $\rightarrow$ pilih **Compress to ZIP file** (Windows 11) atau **Send to $\rightarrow$ Compressed (zipped) folder** (Windows 10).
4. Beri nama file: `smart_lamp.zip`.

---

## Langkah 4: Upload & Ekstrak di cPanel File Manager

1. Di cPanel, buka menu **File Manager**.
2. Masuk ke direktori:
   ```text
   /home/mhsr9595/smart_lamp/
   ```
3. Klik tombol **Upload** di bilah atas $\rightarrow$ pilih file `smart_lamp.zip` dari laptop Anda.
4. Tunggu hingga progress upload selesai (bar berwarna hijau 100%).
5. Kembali ke File Manager, klik kanan pada `smart_lamp.zip` $\rightarrow$ pilih **Extract**.
   * Pada kolom direktori tujuan, pastikan tertulis: `/home/mhsr9595/smart_lamp`
   * Klik **Extract Files**.
6. **Verifikasi Posisi Berkas:**
   Pastikan berkas `passenger_wsgi.py` berada **langsung** di dalam folder `/home/mhsr9595/smart_lamp/` (bukan tersembunyi di dalam subfolder ekstraksi).
7. Hapus file `smart_lamp.zip` dari File Manager agar menghemat kuota penyimpanan hosting Anda.

---

## Langkah 5: Instalasi Dependensi Python di cPanel (PyTorch CPU Hemat Kuota)

1. Di cPanel, buka menu **Terminal**.
2. Aktifkan virtual environment cPanel dan masuk ke folder proyek dengan menjalankan perintah yang diberikan cPanel:
   ```bash
   source ~/virtualenv/smart_lamp/*/bin/activate && cd ~/smart_lamp
   ```
   *(Tanda prompt terminal akan berubah menjadi `((smart/lamp:3.11)) [mhsr9595@... smart_lamp]$`)*

3. Perbarui `pip`:
   ```bash
   pip install --upgrade pip
   ```

4. **Instal PyTorch Khusus CPU (Hemat Kuota):**
   > **Catatan Sangat Penting:** Jangan menginstal `torch` biasa karena akan mengunduh library CUDA GPU sebesar 3 GB yang dapat melebihi kuota inode/RAM hosting. Gunakan versi CPU-only:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
   ```

5. **Instal Seluruh Dependensi Lainnya:**
   ```bash
   pip install -r requirements.txt --no-cache-dir
   ```

---

## Langkah 6: Konfigurasi Pembatasan Thread CloudLinux (Fix OpenBLAS Crash)

Server fisik hosting Rumahweb memiliki **48 CPU threads**. Ketika `numpy` atau `opencv` dimuat, library OpenBLAS secara default mencoba membuat 48 thread sekaligus. Namun, CloudLinux membatasi jumlah thread per user (`RLIMIT_NPROC`), sehingga memicu error:
`OpenBLAS blas_thread_init: pthread_create failed for thread 38 of 48: Resource temporarily unavailable`

### Solusi Permanen:
1. File `passenger_wsgi.py`, `server/app.py`, dan `server/detector.py` yang Anda upload sudah kami lengkapi dengan pembatasan thread di baris paling atas:
   ```python
   os.environ["OPENBLAS_NUM_THREADS"] = "1"
   os.environ["MKL_NUM_THREADS"] = "1"
   os.environ["OMP_NUM_THREADS"] = "1"
   os.environ["BLIS_NUM_THREADS"] = "1"
   os.environ["TORCH_NUM_THREADS"] = "1"
   ```
2. Di Terminal cPanel, simpan juga pembatasan ini ke file profil terminal Anda:
   ```bash
   echo "export OPENBLAS_NUM_THREADS=1" >> ~/.bashrc
   echo "export OMP_NUM_THREADS=1" >> ~/.bashrc
   echo "export MKL_NUM_THREADS=1" >> ~/.bashrc
   ```

3. **Uji Coba Eksekusi di Terminal cPanel:**
   ```bash
   python -c "import passenger_wsgi; print('BERHASIL!')"
   ```
   Jika muncul output `[YOLO] Memuat model pretrained lokal...` dan `BERHASIL!`, artinya konfigurasi server Anda sudah 100% sempurna!

---

## Langkah 7: Restart Aplikasi & Akses Web Dashboard

1. Kembali ke cPanel $\rightarrow$ menu **Setup Python App**.
2. Pada baris aplikasi `smart_lamp`, klik tombol **RESTART**.
3. Buka peramban di laptop atau smartphone Anda, lalu akses:
   👉 **`https://ikhsan.mhsfikom.my.id`**
4. Web Dashboard pemantauan lampu pintar Anda akan langsung terbuka secara langsung via internet dengan koneksi aman HTTPS!

---

## Langkah 8: Pengujian Endpoint API dari Laptop

Anda dapat menguji apakah server cloud Anda sudah siap menerima pengiriman citra dari ESP32-S3:

1. Buka Command Prompt di laptop lokal Anda:
   ```cmd
   cd /d D:\LABIL\BIMBEL\IKHSAN\SMART_LAMP
   ```
2. **Uji Health Check Endpoint:**
   ```cmd
   curl https://ikhsan.mhsfikom.my.id/api/health
   ```
   *(Harus mengembalikan status: `{"status":"healthy","model_loaded":true}`)*

3. **Uji Pengiriman Citra Simulasi ESP32 ke Cloud:**
   ```cmd
   .\venv\Scripts\python.exe tools\simulate_esp32.py sample_images\uji_manusia.jpg https://ikhsan.mhsfikom.my.id/api/detect
   ```
   *(Server cloud akan memproses citra, mengembalikan `lamp_action: "ON"`, dan foto manusia langsung tampil di dashboard cloud)*.

4. **Uji Matriks Bab V Skripsi Langsung ke Cloud:**
   ```cmd
   .\venv\Scripts\python.exe tools\test_bab5_matrix.py https://ikhsan.mhsfikom.my.id
   ```

---

## Langkah 9: Konfigurasi Firmware ESP32-S3-CAM (Koneksi Cloud HTTPS)

Agar perangkat keras fisik ESP32-S3 mengirimkan data langsung ke server cloud cPanel Anda:

1. Buka software **Arduino IDE** di laptop Anda.
2. Buka berkas proyek:
   ```text
   firmware/smart_lamp_esp32s3/smart_lamp_esp32s3.ino
   ```
3. Buka tab berkas **`config.h`**.
4. Pada bagian **Konfigurasi Server**, masukkan URL endpoint cloud Anda:
   ```cpp
   // --- Konfigurasi Cloud Hosting cPanel Rumahweb ---
   #define CLOUD_SERVER_URL  "https://ikhsan.mhsfikom.my.id/api/detect"
   ```
5. Pastikan SSID dan Password Wi-Fi sudah diisi dengan benar:
   ```cpp
   #define WIFI_SSID       "NAMA_WIFI_ANDA"
   #define WIFI_PASSWORD   "PASSWORD_WIFI_ANDA"
   ```
6. Hubungkan modul ESP32-S3-CAM ke laptop via kabel USB Data Type-C.
7. Pilih Board: **ESP32S3 Dev Module**, PSRAM: **OPI PSRAM**, Flash Size: **16MB (128Mb)**.
8. Klik tombol **Upload** (panah kanan).
9. Selesai! Sekarang setiap kali sensor PIR mendeteksi gerakan, ESP32-S3 akan memotret dan mengirim foto secara langsung melalui internet ke server cPanel Anda di mana pun Anda berada.

---

## Troubleshooting & Pemecahan Masalah cPanel

| Kode / Pesan Error | Kemungkinan Penyebab | Cara Mengatasi |
|---|---|---|
| **503 Service Unavailable** | Web server Passenger belum start atau `passenger_wsgi.py` tidak ditemukan di Application Root. | Pastikan file `passenger_wsgi.py` ada langsung di `/home/mhsr9595/smart_lamp/`. Buka Setup Python App lalu klik **RESTART**. |
| **500 Internal Server Error** | Kesalahan saat import library Python atau kehabisan thread OpenBLAS. | Periksa isi file `/home/mhsr9595/smart_lamp/cpanel_startup_error.log` via File Manager untuk membaca log kesalahan detail. Pastikan baris pembatas thread OpenBLAS sudah aktif. |
| **`No module named 'ultralytics'`** | Library belum terinstal di virtualenv cPanel. | Buka Terminal cPanel, aktifkan venv (`source ~/virtualenv/...`), lalu jalankan `pip install -r requirements.txt`. |
| **PIR Trigger tapi Server tidak menerima** | URL di `config.h` salah atau ada kendala koneksi Wi-Fi pada ESP32. | Buka Serial Monitor Arduino IDE pada baudrate 115200 untuk memantau status koneksi HTTP dan respons server. |
