# ==============================================================================
# PASSENGER WSGI ENTRY POINT UNTUK CPANEL RUMAHWEB ("Setup Python App")
# Sistem Kendali Lampu Pintar Deep Learning - Ikhsan Wahyudi (235520110043)
# ==============================================================================

import os
import sys

# SANGAT KRUSIAL UNTUK CPANEL: Batasi OpenBLAS, MKL, dan OMP ke 1 thread!
# Mencegah crash 'OpenBLAS blas_thread_init: pthread_create failed' akibat limit NPROC CloudLinux
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["TORCH_NUM_THREADS"] = "1"

import traceback

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(CURRENT_DIR, 'server')

if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from app import app as application
except Exception as e:
    err_text = traceback.format_exc()
    log_file = os.path.join(CURRENT_DIR, 'cpanel_startup_error.log')
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(err_text)
    except Exception:
        pass

    def application(environ, start_response):
        status = '200 OK'
        output = (
            "===================================================================\n"
            "  DIAGNOSTIK STARTUP PYTHON CPANEL (IKHSAN SMART LAMP)\n"
            "===================================================================\n\n"
            "Terjadi kesalahan saat memuat aplikasi backend Python:\n\n"
            f"{err_text}\n"
            "===================================================================\n"
        ).encode('utf-8')
        response_headers = [
            ('Content-type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]

if __name__ == '__main__':
    application.run()
