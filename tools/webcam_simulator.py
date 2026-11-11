# ==============================================================================
# SIMULATOR WEBCAM LAPTOP (UJI COBA REAL-TIME SEBELUM RAKIT ESP32-S3)
# Menggunakan Kamera Laptop untuk Mensimulasikan Sensor PIR & Kamera OV2640
# Peneliti: Ikhsan Wahyudi (235520110043) - Universitas Almuslim
# ==============================================================================

import sys
import time
import cv2
import requests

SERVER_URL = os.environ.get("SERVER_URL", "http://localhost:5000/api/detect")
if len(sys.argv) > 1 and (sys.argv[1].startswith("http://") or sys.argv[1].startswith("https://")):
    SERVER_URL = sys.argv[1]

def main():
    print("=================================================================")
    print("  SIMULATOR WEBCAM REAL-TIME (PENGUJIAN TANPA ESP32-S3)")
    print("  Sistem Kendali Lampu Pintar Deep Learning - Ikhsan Wahyudi")
    print("=================================================================")
    print("Petunjuk Penggunaan:")
    print(" - Tekan tombol [SPASI] : Mensimulasikan gerakan PIR (Kirim frame ke Server)")
    print(" - Tekan tombol [Q] / [ESC]: Keluar dari simulator")
    print("-----------------------------------------------------------------\n")

    # Buka webcam default laptop (index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Kamera webcam laptop tidak dapat diakses!")
        return

    # Atur resolusi VGA (640x480) persis seperti konfigurasi ESP32-S3
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    status_text = "Siaga (Tekan SPASI untuk jepret & kirim ke Server)"
    status_color = (0, 255, 255)
    last_action = "-"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Gagal membaca frame dari webcam.")
            break

        # Tampilkan overlay instruksi di layar webcam
        display_frame = frame.copy()
        cv2.rectangle(display_frame, (0, 0), (640, 40), (20, 20, 20), -1)
        cv2.putText(display_frame, status_text, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2)
        
        if last_action != "-":
            action_bg = (0, 180, 0) if last_action == "ON" else (0, 0, 180)
            cv2.rectangle(display_frame, (0, 440), (640, 480), action_bg, -1)
            cv2.putText(display_frame, f"HASIL KEPUTUSAN RELAY: LAMPU {last_action}", (15, 468), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        cv2.imshow("Simulator ESP32-S3-CAM (Tekan SPASI untuk Uji Coba)", display_frame)

        key = cv2.waitKey(1) & 0xFF

        # Tombol SPASI: Picu simulasi pengiriman
        if key == 32:
            status_text = "Mengirim frame VGA (640x480) ke Server Flask..."
            status_color = (0, 165, 255)
            
            # Encode frame ke byte JPEG
            success, encoded_img = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not success:
                print("[ERROR] Gagal mengencode frame ke JPEG.")
                continue

            jpeg_bytes = encoded_img.tobytes()
            print(f"\n[TRIGGER] Gerakan disimulasikan! Mengirim {len(jpeg_bytes)} bytes ke {SERVER_URL}...")

            start_t = time.time()
            try:
                res = requests.post(
                    SERVER_URL,
                    data=jpeg_bytes,
                    headers={"Content-Type": "image/jpeg"},
                    timeout=5.0
                )
                latency = (time.time() - start_t) * 1000

                if res.status_code == 200:
                    data = res.json()
                    last_action = data.get("lamp_action", "OFF")
                    kategori = data.get("category", "-").upper()
                    conf = data.get("confidence", 0.0)
                    inf_ms = data.get("inference_time_ms", 0.0)

                    status_text = f"Sukses! Kat: {kategori} | Conf: {conf:.2f} | Latensi: {latency:.1f}ms"
                    status_color = (0, 255, 0) if last_action == "ON" else (0, 100, 255)

                    print(f"[RESPONS] Kategori: {kategori} | Objek: {data.get('detected_classes')} | "
                          f"Lampu: {last_action} | AI: {inf_ms}ms | Total: {latency:.1f}ms")
                else:
                    status_text = f"Error Server: Kode {res.status_code}"
                    status_color = (0, 0, 255)
            except requests.exceptions.ConnectionError:
                status_text = "Gagal terhubung! Pastikan run_server.bat sudah berjalan."
                status_color = (0, 0, 255)
                print("[ERROR] Gagal terhubung ke server Flask di localhost:5000!")
            except Exception as e:
                status_text = f"Pengecualian: {e}"
                status_color = (0, 0, 255)

        # Tombol Q atau ESC: Keluar
        elif key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[SELESAI] Simulator webcam ditutup.")

if __name__ == "__main__":
    main()

