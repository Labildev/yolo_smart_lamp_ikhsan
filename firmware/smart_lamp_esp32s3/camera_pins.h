// ==============================================================================
// DEFINISI PIN KAMERA ESP32-S3-CAM (OV2640) - VARIAN ESP32-S3 N16R8
// Khusus kompatibel dengan ESP32-S3 N16R8 (16MB Flash + 8MB Octal PSRAM)
// ==============================================================================
// CATATAN PENTING ARSITEKTUR MEMORI ESP32-S3 N16R8:
// Pada ESP32-S3 N16R8, pin GPIO berikut digunakan secara internal oleh modul:
// - GPIO 26 s/d 32: Terhubung ke 16MB Quad/Octal SPI Flash (N16)
// - GPIO 33 s/d 37: Terhubung ke 8MB Octal OPI PSRAM (R8)
//
// Konfigurasi pin kamera di bawah ini (GPIO 4..13, 15..18) dan pin periferal
// (PIR = GPIO 21, Relay = GPIO 14) 100% BEBAS DARI KONFLIK internal memori dan clock kamera!
// ==============================================================================

#ifndef CAMERA_PINS_H
#define CAMERA_PINS_H

// Model standar untuk ESP32-S3-CAM N16R8 (AI-Thinker / Freenove / Waveshare / Generic)
#define CAMERA_MODEL_ESP32S3_CAM_N16R8

#if defined(CAMERA_MODEL_ESP32S3_CAM_N16R8) || defined(CAMERA_MODEL_AI_THINKER_ESP32S3_CAM) || defined(CAMERA_MODEL_FREENOVE_ESP32S3_CAM)
  // Pinout Kamera Standar ESP32-S3-CAM N16R8
  #define PWDN_GPIO_NUM     -1
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM     15
  #define SIOD_GPIO_NUM      4
  #define SIOC_GPIO_NUM      5

  #define Y9_GPIO_NUM       16
  #define Y8_GPIO_NUM       17
  #define Y7_GPIO_NUM       18
  #define Y6_GPIO_NUM       12
  #define Y5_GPIO_NUM       10
  #define Y4_GPIO_NUM        8
  #define Y3_GPIO_NUM        9
  #define Y2_GPIO_NUM       11
  #define VSYNC_GPIO_NUM     6
  #define HREF_GPIO_NUM      7
  #define PCLK_GPIO_NUM     13

#elif defined(CAMERA_MODEL_FREENOVE_ESP32S3_CAM)
  // Pinout Alternatif: Freenove ESP32-S3-WROOM-CAM
  #define PWDN_GPIO_NUM     -1
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM     15
  #define SIOD_GPIO_NUM      4
  #define SIOC_GPIO_NUM      5

  #define Y9_GPIO_NUM       16
  #define Y8_GPIO_NUM       17
  #define Y7_GPIO_NUM       18
  #define Y6_GPIO_NUM       12
  #define Y5_GPIO_NUM       10
  #define Y4_GPIO_NUM        8
  #define Y3_GPIO_NUM        9
  #define Y2_GPIO_NUM       11
  #define VSYNC_GPIO_NUM     6
  #define HREF_GPIO_NUM      7
  #define PCLK_GPIO_NUM     13

#elif defined(CAMERA_MODEL_XIAO_ESP32S3_SENSE)
  // Pinout Alternatif: Seeed Studio XIAO ESP32S3 Sense
  #define PWDN_GPIO_NUM     -1
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM     10
  #define SIOD_GPIO_NUM     40
  #define SIOC_GPIO_NUM     39

  #define Y9_GPIO_NUM       48
  #define Y8_GPIO_NUM       11
  #define Y7_GPIO_NUM       12
  #define Y6_GPIO_NUM       14
  #define Y5_GPIO_NUM       16
  #define Y4_GPIO_NUM       18
  #define Y3_GPIO_NUM       17
  #define Y2_GPIO_NUM       15
  #define VSYNC_GPIO_NUM    38
  #define HREF_GPIO_NUM     47
  #define PCLK_GPIO_NUM     13

#else
  #error "Model Kamera belum didefinisikan! Pilih salah satu pada camera_pins.h"
#endif

#endif // CAMERA_PINS_H

