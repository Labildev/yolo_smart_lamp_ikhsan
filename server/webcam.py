# ==============================================================================
# MODUL PENGELOLA WEBCAM LAPTOP (OPENCV BACKEND STREAMER)
# Solusi Kompatibilitas Menyeluruh: Bekerja pada Semua Browser Tanpa Kendala WebRTC / HTTPS
# Peneliti: Ikhsan Wahyudi (235520110043)
# ==============================================================================

import time
import threading
import cv2

class OpenCVWebcam:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.lock = threading.Lock()
        self.current_frame = None

    def start(self):
        """Mengaktifkan kamera laptop di latar belakang."""
        with self.lock:
            if not self.is_running:
                # Coba backend DirectShow untuk Windows, fallback ke default jika gagal
                self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                if not self.cap or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.camera_index)

                if self.cap and self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.is_running = True
                    threading.Thread(target=self._capture_loop, daemon=True).start()
                    return True
                return False
            return True

    def _capture_loop(self):
        """Loop pengambilan frame dari webcam laptop secara kontinu."""
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame
            time.sleep(0.03)

    def get_frame_bytes(self):
        """Mengambil frame terakhir dalam format JPEG byte array."""
        with self.lock:
            if self.current_frame is not None:
                ret, jpeg = cv2.imencode('.jpg', self.current_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    return jpeg.tobytes()
        return None

    def stop(self):
        """Mematikan dan melepaskan akses hardware kamera laptop."""
        with self.lock:
            self.is_running = False
            if self.cap:
                self.cap.release()
                self.cap = None
            self.current_frame = None

