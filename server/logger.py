# ==============================================================================
# LOGGER MODUL PENGUJIAN OTOMATIS (SKRIPSI BAB V)
# Mencatat setiap siklus deteksi ke file CSV secara persisten
# ==============================================================================

import os
import csv
import threading
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
CSV_PATH = os.path.join(DATA_DIR, 'log_pengujian.csv')
_csv_lock = threading.Lock()

CSV_HEADERS = [
    'No',
    'Timestamp',
    'Nama_File',
    'Kelas_Terdeteksi',
    'Kategori',
    'Confidence',
    'Waktu_Inferensi_ms',
    'Status_Lampu_Keputusan',
    'Keterangan'
]

def init_logger():
    """Memastikan folder data dan header file CSV sudah terbuat."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def get_next_test_number():
    """Menghitung nomor pengujian berikutnya berdasarkan jumlah baris CSV."""
    init_logger()
    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            # Baris pertama adalah header, sehingga nomor berikutnya adalah len(rows)
            return len(rows)
    except Exception:
        return 1

def log_detection(file_name, detected_classes, category, confidence, inference_time_ms, lamp_action, notes=''):
    """Menambahkan 1 baris hasil pengujian ke log CSV dengan pengamanan thread lock."""
    with _csv_lock:
        init_logger()
        test_num = get_next_test_number()
        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        classes_str = ', '.join(detected_classes) if detected_classes else 'Tidak Ada'
        conf_str = f"{confidence:.2f}" if confidence > 0 else '0.00'
        inf_str = f"{inference_time_ms:.1f}"

        row = [
            test_num,
            timestamp_str,
            file_name,
            classes_str,
            category,
            conf_str,
            inf_str,
            lamp_action,
            notes
        ]

        with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        return test_num

def get_recent_logs(limit=50):
    """Mengambil riwayat log terbaru untuk ditampilkan pada tabel dan galeri Dashboard."""
    with _csv_lock:
        init_logger()
        records = []
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_name = row.get('Nama_File', '')
                    file_path = os.path.join(uploads_dir, file_name)
                    row['image_url'] = f"/uploads/{file_name}"
                    row['file_exists'] = os.path.exists(file_path)
                    records.append(row)
            # Urutkan dari yang terbaru
            records.reverse()
            return records[:limit]
        except Exception as e:
            print(f"[LOGGER-ERROR] Gagal membaca riwayat log: {e}")
            return []

def get_total_tests_count():
    """Mengembalikan total pengujian yang telah tercatat."""
    with _csv_lock:
        init_logger()
        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                return max(0, len(rows) - 1)
        except Exception:
            return 0

def delete_log_entry(file_name_or_no):
    """Menghapus 1 baris pengujian dari CSV dan menghapus berkas citranya di uploads/."""
    with _csv_lock:
        init_logger()
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        new_rows = []
        deleted = False
        target_str = str(file_name_or_no).strip()

        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header:
                    new_rows.append(header)
                for row in reader:
                    if len(row) > 2:
                        row_no = str(row[0]).strip()
                        row_file = str(row[2]).strip()
                        if row_file == target_str or row_no == target_str:
                            deleted = True
                            # Hapus file gambar terkait jika ada di folder uploads/
                            target_path = os.path.join(uploads_dir, row_file)
                            if os.path.exists(target_path):
                                try:
                                    os.remove(target_path)
                                except Exception:
                                    pass
                            continue
                    new_rows.append(row)

            if deleted:
                # Re-indeks nomor urut No (kolom ke-0)
                for idx in range(1, len(new_rows)):
                    new_rows[idx][0] = str(idx)

                with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(new_rows)

            return deleted
        except Exception as e:
            print(f"[LOGGER-ERROR] Gagal menghapus baris log: {e}")
            return False

def clear_logs():
    """Mereset data log untuk sesi pengujian baru dan membersihkan file foto hasil jepretan."""
    with _csv_lock:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

        # Bersihkan seluruh file foto di folder uploads/
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        if os.path.exists(uploads_dir):
            for fname in os.listdir(uploads_dir):
                if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        os.remove(os.path.join(uploads_dir, fname))
                    except Exception:
                        pass

