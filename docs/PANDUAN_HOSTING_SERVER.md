# PANDUAN DEPLOYMENT & HOSTING SERVER SISTEM LAMPU PINTAR
**Implementasi Sistem Kendali Lampu Pintar Menggunakan Deep Learning (YOLOv8)**  
*Peneliti*: **Ikhsan Wahyudi (235520110043)** - S1 Informatika, Universitas Almuslim  

---

Panduan deployment sistem kendali lampu pintar telah dipisahkan secara terstruktur berdasarkan lingkungan eksekusi:

### 1. [Panduan Menjalankan di Laptop Lokal (Windows)](PANDUAN_RUNNING_LOCAL.md)
* Berisi panduan 1-klik menjalankan server lokal menggunakan file `run_server.bat`.
* Akses Web Dashboard lokal di `http://localhost:5000`.
* Simulasi webcam laptop dan pengujian otomatis matriks Bab V Skripsi.
* Pengambilan data log pengujian format CSV.

### 2. [Panduan Lengkap Hosting cPanel Rumahweb](PANDUAN_HOSTING_CPANEL.md)
* Berisi panduan lengkap deployment ke cPanel Shared Hosting Rumahweb ("Setup Python App" berbasis Phusion Passenger).
* Domain target: **`https://ikhsan.mhsfikom.my.id`**.
* Panduan pemilihan dan pembuatan file ZIP yang aman (bebas file sampah & virtualenv Windows).
* Penanganan limit thread CloudLinux (`OPENBLAS_NUM_THREADS = 1`) agar server tidak error 500/503.
* Konfigurasi koneksi cloud HTTPS pada firmware ESP32-S3-CAM.

---
*Catatan: Sistem tidak lagi memerlukan Docker maupun platform cloud pihak ketiga karena seluruh arsitektur backend telah dioptimalkan secara langsung untuk cPanel Shared Hosting Rumahweb dan lingkungan lokal Windows.*
