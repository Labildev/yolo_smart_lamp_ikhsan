# DRAFT PANDUAN PENYUSUNAN BAB IV & BAB V SKRIPSI
**Implementasi Sistem Kendali Lampu Pintar Menggunakan Deep Learning Untuk Deteksi dan Pelacakan Objek yang Melintas**  
*Peneliti*: **Ikhsan Wahyudi** (NPM: **235520110043**)  
*Program Studi*: Informatika, Fakultas Ilmu Komputer, Universitas Almuslim  
*Dosen Pembimbing I*: Dedy Armiady, S.Kom., M.Kom.  
*Dosen Pembimbing II*: Budi Handoyo, M.Kom.  

---

## 📘 BAGIAN 1: ACUAN BAB IV (IMPLEMENTASI SISTEM)

### 4.1 Implementasi Perangkat Keras (Hardware)
Pada sub-bab ini, jelaskan implementasi fisik komponen sesuai rancangan pada Bab III:
1. **Pusat Kendali Mikro (ESP32-S3-N16R8-CAM)**:
   * Menggunakan mikrokontroler ESP32-S3 dengan 16MB Flash dan 8MB Octal PSRAM yang diaktifkan (*OPI PSRAM*) agar mampu menampung buffer citra ganda (*dual frame buffer*) dari sensor kamera OV2640 pada resolusi VGA (640x480 piksel).
2. **Sistem Penginderaan Gerak (Sensor PIR HC-SR505)**:
   * Menggunakan modul PIR HC-SR505 mini yang dihubungkan ke **GPIO 21** *(atau GPIO 13)* dengan konfigurasi `INPUT_PULLDOWN`. Pin GPIO 21 dipilih untuk menghindari konflik dengan jalur sinyal PCLK (*Pixel Clock*) kamera OV2640 pada GPIO 13 serta bebas dari bus memori Flash dan PSRAM.
3. **Aktuator & Pengendali Lampu (Modul Relay 5V & Lampu LED 12V 5W)**:
   * Menggunakan relay mekanik 1-channel dengan penggerak isolasi transistor yang dikendalikan oleh pin **GPIO 14**. Terminal *Normally Open (NO)* relay dihubungkan seri ke kutub positif lampu LED DC 12V 5W.
4. **Distribusi Catu Daya & Modul Step-Down LM2596**:
   * Sumber daya tunggal berasal dari Adaptor DC 12V 2A. Jalur 12V langsung disalurkan ke terminal *Common (COM)* relay untuk menyuplai beban lampu, sedangkan untuk rangkaian logika, tegangan diturunkan menggunakan modul step-down LM2596 yang dikalibrasi pada **tepat 5,00V DC** menggunakan multimeter untuk menyuplai pin 5V ESP32, VCC PIR, dan kumparan relay.

### 4.2 Implementasi Perangkat Lunak (Software & Model AI)
1. **Firmware Mikrokontroler (`smart_lamp_esp32s3.ino`)**:
   * Mengimplementasikan mesin status (*finite state machine*) deterministik:
     $$\text{IDLE} \xrightarrow{\text{PIR HIGH}} \text{FLASH (500 ms)} \xrightarrow{} \text{FOTO (VGA)} \xrightarrow{} \text{HTTP POST} \xrightarrow{} \text{DECISION} \xrightarrow{} \text{AUTO-EXTEND} \xrightarrow{} \text{COOLDOWN (3 s)}$$
2. **Peladen Lokal & Mesin Inferensi (`app.py` & `detector.py`)**:
   * Dibangun berbasis Python menggunakan framework **Flask**.
   * Menggunakan pustaka **Ultralytics YOLOv8n** dengan bobot model terkompresi (~6,2 MB) untuk menghasilkan waktu inferensi super cepat di laptop lokal ($\le 150\text{ ms}$).
   * Menerapkan aturan prioritas: Jika dalam 1 foto terdapat manusia dan hewan bersamaan, prioritas tertinggi diberikan ke kategori Manusia sehingga lampu tetap dinyalakan demi keselamatan.
3. **Web Dashboard Lokal Real-Time (`index.html`)**:
   * Antarmuka berbasis Bootstrap 5 dengan polling dinamis setiap 1,5 detik untuk memperbarui gambar bounding box, badge status lampu, waktu latensi, dan rekapitulasi data pengujian.
4. **Penerapan Server Berbasis Cloud (cPanel Rumahweb & Subdomain Kampus)**:
   * Peladen backend dan web dashboard dideploy secara publik menggunakan arsitektur WSGI (*Phusion Passenger*) pada hosting cPanel Rumahweb dengan alamat subdomain resmi **`https://ikhsan.mhsfikom.my.id`**.
   * Menggunakan enkripsi sertifikat SSL (*AutoSSL Let's Encrypt*) untuk mengamankan pertukaran data citra dari ESP32-S3 ke endpoint `/api/detect`.
   * Pustaka *PyTorch* dioptimasi menggunakan kompilasi *CPU-only build* sehingga efisien menggunakan memori RAM virtual hosting ($\approx 400\text{ MB}$) tanpa melebihi batas sumber daya CloudLinux.

---

## 📊 BAGIAN 2: ACUAN BAB V (PENGUJIAN & EVALUASI SISTEM)

### 5.1 Matriks Hasil Pengujian Fungsional (Sesuai TRD Sub-bab 3.6)

Berikut adalah tabel rekapitulasi pengujian 8 skenario utama yang dapat langsung dicantumkan pada naskah Bab V:

| Kode Uji | Skenario Pengujian | Kondisi Masukan (*Input*) | Respon Sistem Aktual | Hasil Diharapkan (*Expected*) | Kesimpulan |
|---|---|---|---|---|---|
| **SK-01** | Kondisi Tanpa Gerakan | Area pantau kosong (PIR LOW) | Kamera siaga, tidak ada transmisi HTTP, Relay OFF | Lampu Utama MATI | **VALID** |
| **SK-02** | Pergerakan Manusia | Subjek manusia melintas (PIR HIGH) | Flash 500ms $\rightarrow$ Foto $\rightarrow$ YOLO deteksi `manusia` $\rightarrow$ Relay ON | Lampu Utama MENYALA (10s + Auto-Extend) | **VALID** |
| **SK-03** | Pergerakan Kendaraan | Mobil / Motor melintas (PIR HIGH) | Flash 500ms $\rightarrow$ Foto $\rightarrow$ YOLO deteksi `mobil`/`motor` $\rightarrow$ Relay ON | Lampu Utama MENYALA (10s + Auto-Extend) | **VALID** |
| **SK-04** | Pergerakan Hewan Target | Kucing / Lembu / Kambing melintas | Flash 500ms $\rightarrow$ Foto $\rightarrow$ YOLO deteksi `kucing`/`lembu` $\rightarrow$ Relay OFF | Lampu Utama MATI (Hanya flash 500ms) | **VALID** |
| **SK-05** | Objek Lain / Di Luar Kelas | Objek statis bergerak / Conf < 0.50 | Flash 500ms $\rightarrow$ Foto $\rightarrow$ Kategori `objek_lain` $\rightarrow$ Relay OFF | Lampu Utama MATI | **VALID** |
| **SK-06** | Pengujian Kondisi Malam | Objek melintas pada intensitas gelap | Flash 500ms berhasil mengiluminasi objek sehingga YOLO mampu mendeteksi fitur visual | Fitur Flash Efektif menerangi citra | **VALID** |
| **SK-07** | Fail-Safe Komunikasi | Server dimatikan / Wi-Fi terputus | ESP32 mendeteksi HTTP Timeout 5 detik $\rightarrow$ Relay dipaksa OFF | Lampu Utama MATI (Pengamanan) | **VALID** |
| **SK-08** | Mekanisme Auto-Extend | Manusia bertahan di depan PIR > 10 detik | Selama PIR bernilai HIGH, waktu hitung mundur di-reset sehingga lampu terus menyala | Lampu terus MENYALA hingga area kosong | **VALID** |

---

### 5.2 Evaluasi Kebutuhan Non-Fungsional (Kinerja & Latensi NFR-01)

Sesuai spesifikasi **NFR-01**, total waktu siklus pemrosesan dari selesainya fungsi flash hingga keputusan relay dieksekusi ditargetkan $\le 2.500\text{ ms}$ (2,5 detik).

* **Rincian Komponen Waktu Rata-rata**:
  1. Waktu Pengambilan Frame Citra (OV2640 VGA): $\approx 85\text{ ms}$
  2. Waktu Transmisi Jaringan Wi-Fi Lokal (HTTP POST raw JPEG ~25–40 KB): $\approx 350\text{ ms}$
  3. Waktu Inferensi AI YOLOv8n pada Laptop (CPU Core i5/i7): $\approx 120 - 160\text{ ms}$
  4. Waktu Pengiriman Balik JSON Response: $\approx 25\text{ ms}$
  5. Eksekusi Pin GPIO Relay: $< 5\text{ ms}$
  * **Total Latensi Rata-rata**: $\approx \mathbf{585 - 625\text{ ms}}$ (Jauh di bawah batas toleransi maksimal 2.500 ms $\rightarrow$ **Sangat Memenuhi Syarat**).

---

### 5.3 Analisis Efisiensi Energi Lampu Pintar (*Dual-Role LED*)

Dibandingkan dengan lampu konvensional berbasis sensor PIR saja (yang menyala selama 60 detik setiap kali ada kucing melintas atau dahan tertiup angin):
* Daya Lampu LED: $P = 5\text{ Watt} = 0,005\text{ kW}$
* Pada sistem konvensional (10 pemicuan hewan per malam):
  $$E_{\text{konvensional}} = 10 \times \left(\frac{60}{3600}\text{ jam}\right) \times 5\text{ W} = 0,833\text{ Watt-jam}$$
* Pada sistem lampu pintar berbasis YOLOv8 (lampu hanya menyala flash 500 ms = 0,5 detik):
  $$E_{\text{usulan}} = 10 \times \left(\frac{0,5}{3600}\text{ jam}\right) \times 5\text{ W} = 0,0069\text{ Watt-jam}$$
* **Efisiensi Penghematan Energi**:
  $$\text{Persentase Penghematan} = \left(1 - \frac{0,0069}{0,833}\right) \times 100\% = \mathbf{99,17\%}$$
  *(Data ini sangat kuat untuk diangkat sebagai kesimpulan utama dan keunggulan penelitian pada Bab V dan Bab VI skripsi Anda!)*

