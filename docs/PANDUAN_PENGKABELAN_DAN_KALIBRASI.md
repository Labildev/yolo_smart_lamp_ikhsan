# PANDUAN PENGKABELAN ELEKTRIS & KALIBRASI PERANGKAT KERAS
**Sistem Kendali Lampu Pintar Deep Learning (ESP32-S3-CAM + YOLOv8)**  
*Peneliti*: **Ikhsan Wahyudi (235520110043)** - Informatika Universitas Almuslim  

---

## ⚠️ PERINGATAN KESELAMATAN PERANGKAT KERAS (PENTING!)

ESP32-S3-CAM beroperasi pada logika **3,3V DC** dan memiliki batas toleransi input daya sebesar **5,0V DC**. Tegangan adaptor Anda adalah **12V DC**.

> [!CAUTION]
> **JANGAN LANGSUNG MENGHUBUNGKAN ADAPTOR 12V KE PIN ESP32!**
> Sebelum kabel output dari modul Step-Down LM2596 dihubungkan ke ESP32, sensor PIR, atau modul Relay:
> 1. Hubungkan Adaptor 12V ke terminal `IN+` dan `IN-` LM2596.
> 2. Siapkan **Multimeter Digital** pada mode pengukuran Tegangan DC (VDC).
> 3. Tempelkan probe multimeter pada terminal `OUT+` dan `OUT-` LM2596.
> 4. Putar potensiometer (trimpot kecil berwarna biru) menggunakan obeng minus kecil berlawanan arah jarum jam secara perlahan hingga layar multimeter menunjukkan **tepat 5,0 Volt DC**.
> 5. Setelah tegangan terukur stabil di 5,0V, barulah cabut adaptor dan lanjutkan pengkabelan ke komponen logika.

---

## 🔌 DIAGRAM DISTRIBUSI CATU DAYA & PENGKABELAN PIN

```text
 [ Adaptor 12V 2A DC ]
       │          │
 (+12V)│          │(GND)
       ├────────────────────────┐
       │                        │
       ▼                        ▼
 [ LM2596 IN+ ]           [ LM2596 IN- ]
       │                        │
  (Step-Down)              (Step-Down)
       │                        │
       ▼ (+5.0V Terkalibrasi)   ▼ (Common GND)
  ┌────┴────────────────────────┼────────────────────────┐
  │                             │                        │
  ▼                             ▼                        ▼
[ESP32-S3 CAM]            [Modul Relay 5V]         [Sensor PIR HC-SR505]
  - Pin 5V                  - Pin VCC                - Pin VCC
  - Pin GND ────────────────┼────────────────────────┼ Pin GND
                            │
                            │
[KONTROL LOGIKA (PIN RESMI)]   │
  - GPIO 21 (Input PIR) <──────┼────────────────────────┼ Pin OUT Sinyal PIR (atau GPIO 13)
  - GPIO 14 (Output Relay) ───> Pin IN Trigger Relay
                            │
[BEBAN LAMPU 12V 5W]        │
  - Kutub Positif (+12V) dari Adaptor ──> Terminal COM Relay
  - Terminal NO (Normally Open) Relay ──> Kutub Positif (+) Lampu LED 12V
  - Kutub Negatif (-) Lampu LED 12V  ──> Common Ground (Adaptor 12V GND)
```

---

## 📋 TABEL LENGKAP SAMBUNGAN PIN (PINOUT MAPPING TERKINI)

| Modul Asal | Pin / Terminal | Terhubung Ke | Deskripsi & Fungsi |
|---|---|---|---|
| **Adaptor 12V DC** | Kutub Positif (+) | `IN+` LM2596 & `COM` Relay 5V | Jalur utama 12V untuk lampu & konverter daya |
| **Adaptor 12V DC** | Kutub Negatif (-) | `IN-` LM2596 & Kabel Negatif Lampu | Jalur Ground bersama (*Common Ground*) |
| **LM2596 (Output)**| `OUT+` (+5.0V) | Pin `5V` ESP32, `VCC` Relay, `VCC` PIR | Suplai daya logika 5.0 Volt stabil |
| **LM2596 (Output)**| `OUT-` (GND) | Pin `GND` ESP32, `GND` Relay, `GND` PIR | Referensi tegangan bersama |
| **Sensor PIR** | Pin `OUT` | Pin **GPIO 21** ESP32-S3 *(Atau GPIO 13)* | Output sinyal digital PIR (Bebas konflik PCLK kamera) |
| **Modul Relay** | Pin `IN` | Pin **GPIO 14** ESP32-S3 | Input kendali kumparan relay dari ESP32 |
| **Modul Relay** | Terminal `NO` | Kabel Positif (+) Lampu LED 12V 5W | Menyalurkan 12V ke lampu hanya saat relay ON |

---

## 🔬 CATATAN KESELAMATAN PIN KHUSUS ESP32-S3 N16R8

1. **Pin Relay (GPIO 14)**:
   * **100% AMAN & BEBAS KONFLIK**. GPIO 14 tidak digunakan oleh kamera maupun memori Flash/PSRAM.
2. **Pin PIR (GPIO 13 & Rekomendasi GPIO 21)**:
   * Pada board ESP32-S3-CAM terintegrasi, pin **GPIO 13** secara internal terhubung ke jalur **PCLK (Pixel Clock)** kamera OV2640.
   * **Tips Laboratorium**: Jika saat pengujian kamera menampilkan pesan *`[ERROR] Gagal mengambil frame dari kamera!`*, hal tersebut terjadi karena sinyal pulsa PIR bertabrakan dengan clock kamera. Solusinya sangat mudah: **cukup pindahkan kabel PIR dari pin 13 ke pin sebelahnya yaitu GPIO 21 (atau GPIO 2)** dan ubah `#define PIR_PIN 21` di `config.h`.
3. **Pin Terlarang (Dilarang Digunakan)**:
   * **GPIO 26 s/d 32**: Digunakan bus Flash 16MB (N16).
   * **GPIO 33 s/d 37**: Digunakan bus Octal OPI PSRAM 8MB (R8).

---

## 🛠️ PENGATURAN ARDUINO IDE UNTUK ESP32-S3 N16R8

Saat melakukan upload firmware, pastikan menu **Tools** di Arduino IDE diatur sebagai berikut:
1. **Board**: `ESP32S3 Dev Module`
2. **Flash Size**: `16MB (128Mb)` *(Wajib 16MB karena N16)*
3. **Partition Scheme**: `16M Flash (3MB APP/9.9MB FATFS)` atau `Huge App (3MB No OTA/1MB SPIFFS)`
4. **PSRAM**: `OPI PSRAM` *(Sangat krusial! Mengaktifkan 8MB Octal PSRAM untuk alokasi frame buffer kamera VGA)*
5. **USB CDC On Boot**: `Enabled` *(Jika menggunakan port USB Type-C native ESP32-S3)*
6. **Flash Mode**: `QIO 80MHz`
7. **CPU Frequency**: `240MHz (WiFi)`
8. **Upload Mode**: `UART0 / Hardware CDC`
9. **Port**: Pilih Port COM board Anda (misal COM3/COM4)

---

---

## 💡 PERILAKU RELAY PADA SISTEM DUAL-ROLE LED

1. **Saat Siaga (Idle)**:
   * Relay berada pada posisi **Normally Open (NO)** terbuka $\rightarrow$ Lampu 12V padam.
2. **Saat PIR Mendeteksi Gerakan (PIR HIGH)**:
   * ESP32 mengaktifkan relay selama **500 ms** (fungsi lampu kilat/flash).
   * Kamera OV2640 mengambil 1 frame citra VGA (640x480).
   * ESP32 langsung mematikan relay $\rightarrow$ Lampu padam kembali.
3. **Hasil Inferensi YOLOv8 dari Laptop**:
   * Jika **MANUSIA** atau **KENDARAAN**: ESP32 menyalakan kembali relay selama **10 detik** (sebagai lampu penerangan utama). Menjelang detik ke-10, jika PIR masih HIGH, waktu diperpanjang otomatis (*Auto-Extend*).
   * Jika **HEWAN** atau **OBJEK LAIN**: Relay tetap dipertahankan OFF (lampu tidak menyala).
4. **Waktu Tenang (Cooldown)**:
   * Jeda **3 detik** diterapkan setelah lampu utama padam sebelum sensor PIR diaktifkan kembali guna mencegah pemicuan berulang akibat radiasi suhu lampu.

