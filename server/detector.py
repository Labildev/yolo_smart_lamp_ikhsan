# ==============================================================================
# MODUL INFERENSI & DETEKSI OBJEK YOLOV8
# Mendukung Model Khusus (best.pt) maupun Pretrained Fallback (yolov8n.pt)
# Sesuai Matriks Keputusan PRD Sub-bab 2.2
# ==============================================================================

import os
import sys
import time
from datetime import datetime

# Direktori proyek dasar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Konfigurasi direktori cache dan batas thread agar aman di hosting cPanel / CageFS
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['BLIS_NUM_THREADS'] = '1'
os.environ['TORCH_NUM_THREADS'] = '1'
os.environ.setdefault('YOLO_CONFIG_DIR', DATA_DIR)
os.environ.setdefault('MPLCONFIGDIR', '/tmp')

import cv2
import numpy as np
from ultralytics import YOLO

# Direktori proyek
PROJECT_ROOT = os.path.dirname(BASE_DIR)
MODEL_DIR = os.path.join(PROJECT_ROOT, 'model')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Path model khusus jika user sudah melatih dataset
CUSTOM_MODEL_PATH = os.path.join(MODEL_DIR, 'best.pt')
PRETRAINED_MODEL_PATH = os.path.join(MODEL_DIR, 'yolov8n.pt')

# Ambang batas sesuai TRD Sub-bab 3.5
CONF_THRESHOLD = 0.50
IOU_THRESHOLD = 0.45

# Pemetaan Kelas COCO Standar (Fallback jika best.pt belum dilatih)
COCO_CLASS_MAPPING = {
    'person': 'manusia',
    'car': 'mobil',
    'bus': 'mobil',
    'truck': 'mobil',
    'motorcycle': 'motor',
    'bicycle': 'motor',
    'cat': 'kucing',
    'cow': 'lembu',
    'sheep': 'kambing',
    'dog': 'kucing',     # Fallback kategori hewan jika terdeteksi anjing
    'horse': 'lembu'     # Fallback kategori hewan ternak
}

TARGET_ON_CLASSES = ['manusia', 'mobil', 'motor']
TARGET_OFF_CLASSES = ['kucing', 'lembu', 'kambing']

class YOLOv8Detector:
    def __init__(self):
        self.model = None
        self.is_custom_model = False
        self.load_model()

    def load_model(self):
        """Memuat best.pt jika tersedia di folder model, atau fallback ke model lokal yolov8n.pt."""
        try:
            # 1. Cek konfigurasi environment variable MODEL_PATH (Opsional untuk deployment cloud)
            env_model = os.environ.get('MODEL_PATH')
            if env_model and os.path.exists(env_model):
                print(f"[YOLO] Memuat model dari environment MODEL_PATH: {env_model}")
                self.model = YOLO(env_model)
                self.is_custom_model = 'best' in os.path.basename(env_model).lower()
                return

            # 2. Cek model khusus (best.pt) di lokasi-lokasi potensial
            candidate_custom = [
                CUSTOM_MODEL_PATH,
                os.path.join(BASE_DIR, 'best.pt'),
                os.path.join(BASE_DIR, 'model', 'best.pt')
            ]
            for p in candidate_custom:
                if os.path.exists(p):
                    print(f"[YOLO] Memuat model khusus (best.pt): {p}")
                    self.model = YOLO(p)
                    self.is_custom_model = True
                    return

            # 3. Cek model pretrained (yolov8n.pt) di lokasi-lokasi potensial
            candidate_pretrained = [
                PRETRAINED_MODEL_PATH,
                os.path.join(BASE_DIR, 'yolov8n.pt'),
                os.path.join(BASE_DIR, 'model', 'yolov8n.pt')
            ]
            for p in candidate_pretrained:
                if os.path.exists(p):
                    print(f"[YOLO] Memuat model pretrained lokal: {p}")
                    print("[YOLO] Mode Pemetaan Cerdas Aktif: COCO 80 Kelas -> 6 Kelas Target Skripsi...")
                    self.model = YOLO(p)
                    self.is_custom_model = False
                    return

            # 4. Fallback default YOLOv8n (diunduh otomatis oleh Ultralytics jika belum ada)
            print("[YOLO] Model lokal belum ditemukan di folder model/.")
            print("[YOLO] Mengunduh/menggunakan model standar 'yolov8n.pt' dengan pemetaan kelas cerdas...")
            self.model = YOLO('yolov8n.pt')
            self.is_custom_model = False
        except Exception as e:
            print(f"[ERROR YOLO load_model] Gagal inisialisasi awal model: {e}")
            self.load_error = str(e)
            self.model = None

    def detect(self, image_bytes):
        """
        Memproses raw bytes JPEG dari ESP32-S3:
        1. Decode citra
        2. Inferensi YOLOv8n
        3. Terapkan Matriks Keputusan Sistem
        4. Simpan citra ber-bounding box
        5. Kembalikan data respon JSON
        """
        if self.model is None:
            self.load_model()
            if self.model is None:
                raise RuntimeError(f"Model YOLOv8 belum siap: {getattr(self, 'load_error', 'Gagal memuat bobot model')}")

        start_time = time.time()

        # 1. Decode byte array ke format gambar OpenCV BGR
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Gagal mendecode raw bytes gambar JPEG.")

        # 2. Jalankan inferensi YOLO
        results = self.model.predict(
            source=img,
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False
        )

        inference_time_ms = (time.time() - start_time) * 1000

        detected_items = []
        max_confidence = 0.0

        # 3. Ekstraksi hasil bounding box dan nama kelas
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                orig_name = result.names[cls_id]
                conf = float(box.conf[0].item())

                # Pemetaan nama kelas jika memakai model COCO
                if self.is_custom_model:
                    class_name = str(orig_name).lower()
                else:
                    class_name = COCO_CLASS_MAPPING.get(orig_name.lower(), orig_name.lower())

                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                detected_items.append({
                    'class': class_name,
                    'orig_name': orig_name,
                    'confidence': conf,
                    'bbox': xyxy
                })
                if conf > max_confidence:
                    max_confidence = conf

        # 4. Aturan Bisnis & Matriks Keputusan Objek (PRD Sub-bab 2.2)
        # Prioritas tertinggi: Jika ada Manusia atau Kendaraan -> Lampu ON
        has_human = any(item['class'] == 'manusia' for item in detected_items)
        has_vehicle = any(item['class'] in ['mobil', 'motor'] for item in detected_items)
        has_animal = any(item['class'] in TARGET_OFF_CLASSES for item in detected_items)

        if has_human:
            category = 'manusia'
            lamp_action = 'ON'
        elif has_vehicle:
            category = 'kendaraan'
            lamp_action = 'ON'
        elif has_animal:
            category = 'hewan'
            lamp_action = 'OFF'
        else:
            category = 'objek_lain'
            lamp_action = 'OFF'

        detected_class_names = [item['class'] for item in detected_items]

        # 5. Visualisasi Bounding Box pada Citra untuk Web Dashboard
        annotated_img = img.copy()

        for item in detected_items:
            x1, y1, x2, y2 = item['bbox']
            cls_name = item['class']
            conf = item['confidence']

            # Warna kotak: Hijau untuk target ON, Merah untuk target OFF
            if cls_name in TARGET_ON_CLASSES:
                box_color = (0, 220, 0)      # Hijau
            elif cls_name in TARGET_OFF_CLASSES:
                box_color = (0, 70, 255)     # Merah oranye
            else:
                box_color = (255, 180, 0)    # Biru / abu-abu

            # Gambar Bounding Box
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), box_color, 2)

            # Label teks
            label_text = f"{cls_name} {conf:.2f}"
            (text_w, text_h), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_img, (x1, y1 - text_h - 4), (x1 + text_w + 4, y1), box_color, -1)
            cv2.putText(annotated_img, label_text, (x1 + 2, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Informasi status di pojok atas citra
        status_banner = f"Lampu: {lamp_action} | Kat: {category.upper()} | Inferensi: {inference_time_ms:.1f}ms"
        banner_bg = (0, 160, 0) if lamp_action == 'ON' else (70, 70, 70)
        cv2.rectangle(annotated_img, (0, 0), (annotated_img.shape[1], 28), banner_bg, -1)
        cv2.putText(annotated_img, status_banner, (10, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        # 6. Simpan citra hasil deteksi
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:19]
        file_name = f"detect_{now_str}.jpg"
        upload_path = os.path.join(UPLOADS_DIR, file_name)
        static_preview_path = os.path.join(STATIC_DIR, 'latest_detection.jpg')

        cv2.imwrite(upload_path, annotated_img)
        cv2.imwrite(static_preview_path, annotated_img)

        return {
            'status': 'success',
            'category': category,
            'detected_classes': detected_class_names,
            'confidence': round(max_confidence, 2),
            'inference_time_ms': round(inference_time_ms, 1),
            'lamp_action': lamp_action,
            'file_name': file_name,
            'is_custom_model': self.is_custom_model
        }

