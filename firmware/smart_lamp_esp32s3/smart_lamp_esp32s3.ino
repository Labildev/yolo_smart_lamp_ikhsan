// ==============================================================================
// SKRIPSI INFORMATIKA - UNIVERSITAS ALMUSLIM
// Peneliti   : Ikhsan Wahyudi (235520110043)
// Judul      : Implementasi Sistem Kendali Lampu Pintar Menggunakan Deep Learning
//              Untuk Deteksi dan Pelacakan Objek Yang Melintas
// Deskripsi  : Firmware ESP32-S3-CAM (ESP32-S3 N16R8: 16MB Flash + 8MB OPI PSRAM)
// ==============================================================================

#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include "config.h"
#include "camera_pins.h"

// Prototipe Fungsi
void setRelay(bool state);
bool initCamera();
bool sendImageToServer(camera_fb_t *fb, String &responseBody);
bool parseLampAction(const String &jsonResponse);

void setup() {
  Serial.begin(115200);

  // Tunggu koneksi Serial Monitor (berguna jika menggunakan USB CDC native ESP32-S3)
  unsigned long startWait = millis();
  while (!Serial && (millis() - startWait < 2000));
  delay(300);

  Serial.println("\n=======================================================");
  Serial.println("  SISTEM KENDALI LAMPU PINTAR ESP32-S3 N16R8 (YOLOv8)");
  Serial.println("  Peneliti: Ikhsan Wahyudi (235520110043)");
  Serial.println("=======================================================");

  // Informasi Diagnostik Hardware ESP32-S3 N16R8
  Serial.printf("[INFO HW] Chip: %s (Rev %d)\n", ESP.getChipModel(), ESP.getChipRevision());
  Serial.printf("[INFO HW] Flash Size: %u MB (N16)\n", ESP.getFlashChipSize() / (1024 * 1024));
  Serial.printf("[INFO HW] Free Heap : %u KB\n", ESP.getFreeHeap() / 1024);
  if (psramFound()) {
    Serial.printf("[INFO HW] PSRAM Size: %u MB (Octal PSRAM R8 Aktif)\n", ESP.getPsramSize() / (1024 * 1024));
    Serial.printf("[INFO HW] Free PSRAM: %u KB\n", ESP.getFreePsram() / 1024);
  } else {
    Serial.println("[WARN HW] PSRAM belum aktif! Pastikan di Arduino IDE pilih Tools -> PSRAM: 'OPI PSRAM'.");
  }

  // 1. Inisialisasi Pin Relay & Sensor PIR
  pinMode(RELAY_PIN, OUTPUT);
  setRelay(false); // Pastikan relay selalu OFF saat booting (Fail-Safe)

  pinMode(PIR_PIN, INPUT_PULLDOWN);

  // 2. Inisialisasi Modul Kamera OV2640 dengan Buffer Octal PSRAM (R8)
  if (!initCamera()) {
    Serial.println("[ERROR] Gagal inisialisasi modul kamera OV2640!");
    Serial.println("[ERROR] Periksa kabel pita kamera atau pastikan PSRAM OPI sudah diaktifkan.");
    while (true) {
      delay(1000);
    }
  }
  Serial.println("[OK] Kamera OV2640 berhasil diinisialisasi (VGA 640x480).");

  // 3. Menghubungkan ke Jaringan Wi-Fi Lokal
  Serial.print("[WIFI] Menghubungkan ke: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int wifiAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifiAttempts < 30) {
    delay(500);
    Serial.print(".");
    wifiAttempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Berhasil terhubung!");
    Serial.print("[WIFI] IP ESP32-S3: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WIFI-WARN] Belum terhubung ke Wi-Fi. Sistem tetap siaga.");
  }

  Serial.println("[STATUS] Mode Siaga (Idle). Menunggu pemicu Sensor PIR...");
}

void loop() {
  // Pastikan koneksi Wi-Fi tetap aktif jika terputus
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
  }

  // Baca status sensor PIR HC-SR505
  int pirState = digitalRead(PIR_PIN);

  if (pirState == HIGH) {
    Serial.println("\n-------------------------------------------------------");
    Serial.println("[PIR] Gerakan terdeteksi! (PIR Sinyal HIGH)");

    // -------------------------------------------------------------------------
    // TAHAP 1 & 2: FLASH LAMPU KILAT & AMBIL CITRA (PRD Sub-bab 1.3)
    // -------------------------------------------------------------------------
    Serial.println("[FLASH] Mengaktifkan lampu kilat (500 ms)...");
    setRelay(true);             // Nyalakan lampu 12V sebagai flash
    delay(FLASH_WARMUP_MS);     // Jeda 500 ms agar eksposur kamera stabil

    Serial.println("[CAMERA] Menangkap 1 frame citra (JPEG)...");
    // Buang 1 buffer frame lama di DMA pool agar frame yang diambil 100% tersinari lampu flash
    camera_fb_t *old_fb = esp_camera_fb_get();
    if (old_fb) {
      esp_camera_fb_return(old_fb);
    }
    camera_fb_t *fb = esp_camera_fb_get();
    
    // Matikan lampu flash segera setelah pemotretan selesai
    setRelay(false);
    Serial.println("[FLASH] Lampu kilat dimatikan kembali.");

    if (!fb) {
      Serial.println("[ERROR] Gagal mengambil frame dari kamera!");
      delay(COOLDOWN_MS);
      return;
    }

    // -------------------------------------------------------------------------
    // TAHAP 3: TRANSMISI CITRA VIA HTTP POST KE SERVER LOKAL
    // -------------------------------------------------------------------------
    String responseBody = "";
    bool postSuccess = false;

    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("[HTTP] Mengirim citra (%u byte) ke Server Flask...\n", fb->len);
      postSuccess = sendImageToServer(fb, responseBody);
    } else {
      Serial.println("[FAIL-SAFE] Wi-Fi terputus! Mengabaikan pengiriman.");
    }

    // Kembalikan buffer frame kamera ke pool memori
    esp_camera_fb_return(fb);

    // -------------------------------------------------------------------------
    // TAHAP 4: KEPUTUSAN KENDALI LAMPU UTAMA & AUTO-EXTEND (PRD Sub-bab 1.5)
    // -------------------------------------------------------------------------
    bool shouldTurnOn = false;

    if (postSuccess && responseBody.length() > 0) {
      Serial.println("[SERVER-RESP] " + responseBody);
      shouldTurnOn = parseLampAction(responseBody);
    } else {
      // Fail-Safe: Gagal komunikasi atau timeout -> Lampu tetap OFF
      Serial.println("[FAIL-SAFE] Gagal komunikasi / Server tidak merespons. Lampu tetap OFF.");
      shouldTurnOn = false;
    }

    if (shouldTurnOn) {
      Serial.println("[ACTION] Target Positif (Manusia / Kendaraan) terverifikasi!");
      Serial.println("[RELAY] Menyalakan Lampu Utama (Durasi dasar 10 detik)...");
      setRelay(true);

      // Hitung durasi nyala dasar 10 detik dengan pengecekan Auto-Extend
      unsigned long startTime = millis();
      unsigned long duration = MAIN_LIGHT_HOLD_MS;

      while (millis() - startTime < duration) {
        delay(200);

        // Mekanisme Auto-Extend:
        // Jika sensor PIR masih mendeteksi gerakan menjelang durasi habis, perpanjang waktu!
        if (digitalRead(PIR_PIN) == HIGH) {
          startTime = millis(); // Reset penghitung waktu mundur
          Serial.println("[AUTO-EXTEND] PIR masih HIGH! Durasi nyala diperpanjang...");
        }
      }

      setRelay(false);
      Serial.println("[RELAY] Lampu Utama dimatikan (Area telah sepi).");
    } else {
      Serial.println("[ACTION] Objek Hewan / Objek Lain / Tidak Terdeteksi. Lampu Utama tetap PADAM.");
      setRelay(false);
    }

    // -------------------------------------------------------------------------
    // TAHAP 5: WAKTU TENANG (COOLDOWN)
    // -------------------------------------------------------------------------
    Serial.printf("[COOLDOWN] Waktu tenang %d ms untuk stabilisasi sensor...\n", COOLDOWN_MS);
    delay(COOLDOWN_MS);
    Serial.println("[STATUS] Kembali ke Mode Siaga (Idle).");
  }

  delay(50); // Polling interval siaga
}

// ==============================================================================
// FUNGSI PENDUKUNG
// ==============================================================================

// Mengatur status modul Relay dengan memperhitungkan Active LOW / Active HIGH
void setRelay(bool state) {
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, state ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  }
}

// Inisialisasi Hardware Kamera OV2640 dengan frame buffer Octal PSRAM
bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Parameter kompresi citra dan pemanfaatan 8MB Octal PSRAM (R8)
  if (psramFound()) {
    Serial.println("[PSRAM] Octal PSRAM 8MB (R8) terdeteksi dan diaktifkan.");
    config.frame_size   = FRAMESIZE_VGA;        // Resolusi VGA 640x480 (Standar PRD)
    config.jpeg_quality = 10;                   // Kualitas kompresi tinggi & tajam untuk YOLOv8 (0-63)
    config.fb_count     = 2;                    // Dual Frame Buffer untuk transmisi cepat
    #if defined(CAMERA_FB_IN_PSRAM)
    config.fb_location  = CAMERA_FB_IN_PSRAM;   // Pastikan alokasi buffer masuk ke 8MB Octal PSRAM
    #endif
  } else {
    Serial.println("[WARN] PSRAM tidak terdeteksi! Menggunakan alokasi darurat internal RAM.");
    Serial.println("[WARN] Pastikan di Arduino IDE: Tools -> PSRAM: 'OPI PSRAM'.");
    config.frame_size   = FRAMESIZE_QVGA;       // Turunkan ke 320x240 jika PSRAM tidak aktif
    config.jpeg_quality = 15;
    config.fb_count     = 1;
  }
  
  #if defined(CAMERA_GRAB_LATEST)
  config.grab_mode    = CAMERA_GRAB_LATEST;   // Frame terbaru saat flash menyala
  #endif

  esp_err_t err = esp_camera_init(&config);
  return (err == ESP_OK);
}

// Mengirim raw bytes JPEG via HTTP/HTTPS POST ke Server (Lokal maupun Cloud Hosting)
bool sendImageToServer(camera_fb_t *fb, String &responseBody) {
  HTTPClient http;
  String serverUrl = "";

  String cloudUrl = String(CLOUD_SERVER_URL);
  cloudUrl.trim();

  if (cloudUrl.length() > 0) {
    serverUrl = cloudUrl;
  } else {
    serverUrl = "http://" + String(SERVER_HOST) + ":" + String(SERVER_PORT) + String(SERVER_ENDPOINT);
  }

  Serial.println("[HTTP] Menghubungi endpoint: " + serverUrl);

  bool isHttps = serverUrl.startsWith("https://");
  WiFiClientSecure secureClient;
  WiFiClient regularClient;

  if (isHttps) {
    // Terima sertifikat SSL cloud otomatis (Render, Railway, Cloudflare, Let's Encrypt)
    secureClient.setInsecure();
    http.begin(secureClient, serverUrl);
  } else {
    http.begin(regularClient, serverUrl);
  }

  http.setTimeout(HTTP_TIMEOUT_MS);
  http.addHeader("Content-Type", "image/jpeg");

  int httpCode = http.POST(fb->buf, fb->len);

  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      responseBody = http.getString();
      http.end();
      return true;
    } else {
      Serial.printf("[HTTP] Server merespons dengan kode status: %d\n", httpCode);
    }
  } else {
    Serial.printf("[HTTP] Gagal kirim / Timeout: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  return false;
}

// Parser sederhana tanpa ketergantungan library tambahan
// Mengecek apakah respons JSON mengandung '"lamp_action":"ON"' atau '"lamp_action": "ON"'
bool parseLampAction(const String &jsonResponse) {
  if (jsonResponse.indexOf("\"lamp_action\":\"ON\"") != -1 ||
      jsonResponse.indexOf("\"lamp_action\": \"ON\"") != -1 ||
      jsonResponse.indexOf("\"lamp_action\": \"on\"") != -1 ||
      jsonResponse.indexOf("\"lamp_action\":\"on\"") != -1) {
    return true;
  }
  return false;
}

