# ==============================================================================
# SKRIPSI INFORMATIKA - UNIVERSITAS ALMUSLIM
# Peneliti   : Ikhsan Wahyudi (235520110043)
# Skrip Pelatihan Model YOLOv8n (Transfer Learning / Fine-Tuning)
# Sesuai TRD Sub-bab 3.5: 6 Kelas (manusia, mobil, motor, kucing, lembu, kambing)
# ==============================================================================

import os
import shutil
from ultralytics import YOLO

def main():
    print("=================================================================")
    print("  PELATIHAN MODEL YOLOV8N - SISTEM KENDALI LAMPU PINTAR")
    print("  Peneliti: Ikhsan Wahyudi (235520110043)")
    print("=================================================================")

    # 1. Lokasi file data.yaml dari Roboflow / dataset lokal Anda
    # Pastikan file data.yaml memiliki daftar 6 kelas:
    # names: ['manusia', 'mobil', 'motor', 'kucing', 'lembu', 'kambing']
    data_yaml_path = input("Masukkan path ke file data.yaml (contoh: dataset/data.yaml): ").strip()
    
    if not data_yaml_path:
        data_yaml_path = "dataset/data.yaml"

    if not os.path.exists(data_yaml_path):
        print(f"\n[ERROR] File '{data_yaml_path}' tidak ditemukan!")
        print("Silakan siapkan dataset terlebih dahulu (misal unduh dari Roboflow format YOLOv8).")
        return

    # 2. Inisialisasi model pretrained yolov8n.pt
    base_weight = os.path.join("model", "yolov8n.pt")
    if not os.path.exists(base_weight):
        base_weight = "yolov8n.pt"
    print(f"\n[INFO] Memuat bobot dasar '{base_weight}'...")
    model = YOLO(base_weight)

    # 3. Parameter pelatihan sesuai TRD Sub-bab 3.5
    epochs = 75           # 50 - 100 epoch
    imgsz = 640           # Resolusi 640x640 piksel
    batch_size = 16       # Sesuaikan dengan RAM GPU / CPU
    project_name = "runs_lampu_pintar"
    experiment_name = "train_yolov8n_6class"

    print(f"\n[INFO] Memulai pelatihan:")
    print(f" - Epochs    : {epochs}")
    print(f" - Image Size: {imgsz}")
    print(f" - Batch Size: {batch_size}")
    print("-----------------------------------------------------------------")

    model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        project=project_name,
        name=experiment_name,
        save=True,
        plots=True,
        verbose=True
    )

    print("\n=================================================================")
    print("[SELESAI] Pelatihan model selesai!")
    
    # 4. Salin bobot terbaik (best.pt) ke folder model/
    best_weights = os.path.join(project_name, experiment_name, "weights", "best.pt")
    target_destination = os.path.join("model", "best.pt")

    if os.path.exists(best_weights):
        os.makedirs("model", exist_ok=True)
        shutil.copy(best_weights, target_destination)
        print(f"[OK] Bobot terbaik berhasil disalin ke: {target_destination}")
        print("Server Flask sekarang akan secara otomatis menggunakan model 'best.pt' ini!")
    else:
        print(f"[PERINGATAN] File {best_weights} tidak ditemukan. Periksa folder {project_name}.")

if __name__ == "__main__":
    main()

