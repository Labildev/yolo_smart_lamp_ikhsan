// ==============================================================================
// KONFIGURASI SISTEM KENDALI LAMPU PINTAR ESP32-S3 N16R8 (16MB FLASH + 8MB OPI PSRAM)
// Berdasarkan Dokumen PRD & TRD v1.0 Final - Ikhsan Wahyudi (235520110043)
// ==============================================================================

#ifndef CONFIG_H
#define CONFIG_H

// --- 1. Konfigurasi Jaringan Wi-Fi ---
// Sesuaikan dengan nama hotspot / Wi-Fi lokal Anda (Frekuensi wajib 2.4 GHz)
#define WIFI_SSID       "NAMA_WIFI_ANDA"
#define WIFI_PASSWORD   "PASSWORD_WIFI_ANDA"

// --- 2. Konfigurasi Server (Server Lokal maupun Cloud Hosting) ---
// OPSI A (Cloud Hosting): Jika server di-hosting di internet (cPanel Rumahweb, Render, VPS, ngrok):
// Masukkan URL endpoint lengkap (contoh: "https://ikhsan.mhsfikom.my.id/api/detect")
// Catatan: Jika baris ini diisi, firmware OTOMATIS menggunakan URL Cloud ini!
#define CLOUD_SERVER_URL  ""  // Isi dengan "https://ikhsan.mhsfikom.my.id/api/detect" jika sudah online

// OPSI B (Lokal Laptop): Digunakan jika CLOUD_SERVER_URL di atas kosong ("")
// Masukkan IP Address Laptop/PC Anda di jaringan lokal (cek via 'ipconfig' di CMD)
#define SERVER_HOST     "192.168.1.100"
#define SERVER_PORT     5000
#define SERVER_ENDPOINT "/api/detect"

// --- 3. Konfigurasi Pin GPIO (Relay Pin 14 & PIR Pin 21) ---
#define RELAY_PIN       14    // Output Kendali Modul Relay 5V (Beban Lampu LED 12V 5W)

// CATATAN TEKNIS KRUSIAL:
// Pada ESP32-S3-CAM, GPIO 13 secara internal digunakan oleh jalur PCLK (Pixel Clock) Kamera OV2640.
// Oleh karena itu, pin PIR diatur ke GPIO 21 agar 100% bebas bentrok dengan clock kamera maupun PSRAM.
// (Jika di rangkaian fisik Anda menggunakan Pin 13, Anda dapat mengubah nilainya ke 13).
#define PIR_PIN         21    // Input Sensor PIR HC-SR505 (Bebas bentrok PCLK Kamera)

// --- 4. Karakteristik Modul Relay 5V ---
// Umumnya modul relay 5V di pasaran bertipe Active LOW:
// set true  = Relay ON saat pin bernilai LOW (0V), OFF saat HIGH (3.3V)
// set false = Relay ON saat pin bernilai HIGH (3.3V), OFF saat LOW (0V)
#define RELAY_ACTIVE_LOW  true

// --- 5. Parameter Waktu / Pewaktuan Sistem (Sesuai TRD Sub-bab 3.3) ---
#define FLASH_WARMUP_MS     500     // Jeda nyala lampu flash sebelum jepret kamera
#define HTTP_TIMEOUT_MS     5000    // Batas waktu tunggu koneksi HTTP POST (Fail-Safe)
#define MAIN_LIGHT_HOLD_MS  10000   // Durasi dasar nyala lampu utama (10 detik)
#define COOLDOWN_MS         3000    // Waktu tenang setelah siklus selesai (hindari false re-trigger)

#endif // CONFIG_H

