# Direktori Model YOLOv8

Folder ini digunakan untuk menyimpan bobot model hasil pelatihan khusus (*custom training*):

- **Nama File Target**: `best.pt`
- **Arsitektur**: YOLOv8n (Nano)
- **Jumlah Kelas**: 6 Kelas
  0. `manusia`
  1. `mobil`
  2. `motor`
  3. `kucing`
  4. `lembu`
  5. `kambing`

### Status Berkas Model Saat Ini:
- `yolov8n.pt` (6.2 MB) : **SUDAH TERSEDIA (Pretrained)** di folder ini!
  Server Flask sudah siap dijalankan 100% offline dengan pemetaan 6 kelas target skripsi.
- `best.pt` : **Opsional (Custom)**. Jika Anda nanti melatih dataset sendiri menggunakan `train_yolov8.py`, salin file `best.pt` ke folder ini. Sistem akan otomatis memprioritaskan `best.pt`.

Setelah Anda menyelesaikan proses pelatihan dataset (menggunakan skrip `train_yolov8.py`), cukup salin file `best.pt` hasil latih ke folder ini, lalu restart server Flask.

