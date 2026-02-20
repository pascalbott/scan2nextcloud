import os
import time
import logging
import requests
import shutil
import datetime
from requests.auth import HTTPBasicAuth
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

# ========================
# CONFIG
# ========================

NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
NEXTCLOUD_USER = os.getenv("NEXTCLOUD_USER")
NEXTCLOUD_PASS = os.getenv("NEXTCLOUD_PASS")
NEXTCLOUD_FOLDER = os.getenv("NEXTCLOUD_FOLDER", "Scans")

SCAN_DIR = "/scan"
UPLOADED_DIR = "/uploaded"

RETRY_COUNT = 5
RETRY_DELAY = 5

# ========================
# LOGGING
# ========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("scan2nextcloud")

# ========================
# HELPER
# ========================

def wait_until_complete(path, timeout=120):
    logger.info(f"Warte auf stabile Datei: {path}")
    start = time.time()
    last_size = -1

    while time.time() - start < timeout:
        if not os.path.exists(path):
            return False

        size = os.path.getsize(path)
        if size == last_size and size > 0:
            logger.info("Datei ist stabil.")
            return True

        last_size = size
        time.sleep(2)

    logger.warning("Datei wurde nicht stabil innerhalb Timeout.")
    return False


def generate_timestamped_name(original_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{original_name}"


def upload_file(filepath):
    original_filename = os.path.basename(filepath)
    filename = generate_timestamped_name(original_filename)

    upload_url = (
        f"{NEXTCLOUD_URL}/remote.php/dav/files/"
        f"{NEXTCLOUD_USER}/{NEXTCLOUD_FOLDER}/{filename}"
    )

    logger.info(f"Upload gestartet: {filename}")
    logger.info(f"Ziel URL: {upload_url}")

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            with open(filepath, "rb") as f:
                response = requests.put(
                    upload_url,
                    data=f,
                    auth=HTTPBasicAuth(NEXTCLOUD_USER, NEXTCLOUD_PASS),
                    timeout=180,
                )

            if response.status_code in (201, 204):
                logger.info(f"Upload erfolgreich: {filename}")
                return True, filename
            else:
                logger.error(
                    f"Upload fehlgeschlagen (Versuch {attempt}): "
                    f"HTTP {response.status_code} - {response.text}"
                )

        except Exception as e:
            logger.error(f"Fehler beim Upload (Versuch {attempt}): {e}")

        time.sleep(RETRY_DELAY)

    return False, None


# ========================
# HANDLER
# ========================

class ScanHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        if not event.src_path.lower().endswith(".pdf"):
            logger.info("Nicht-PDF Datei ignoriert.")
            return

        logger.info(f"Neue Datei erkannt: {event.src_path}")

        if not wait_until_complete(event.src_path):
            logger.error("Datei nicht stabil, wird übersprungen.")
            return

        success, uploaded_name = upload_file(event.src_path)

        if success:
            try:
                os.makedirs(UPLOADED_DIR, exist_ok=True)

                archive_name = generate_timestamped_name(
                    os.path.basename(event.src_path)
                )

                destination = os.path.join(UPLOADED_DIR, archive_name)

                shutil.move(event.src_path, destination)

                logger.info(f"Datei archiviert nach: {destination}")

            except Exception as e:
                logger.error(f"Fehler beim Verschieben: {e}")
        else:
            logger.error("Upload endgültig fehlgeschlagen.")


# ========================
# START
# ========================

if __name__ == "__main__":
    logger.info("Scan2Nextcloud gestartet")
    logger.info(f"Scan Ordner: {SCAN_DIR}")
    logger.info(f"Nextcloud Benutzer: {NEXTCLOUD_USER}")
    logger.info(f"Nextcloud Ordner: {NEXTCLOUD_FOLDER}")

    os.makedirs(UPLOADED_DIR, exist_ok=True)

    observer = Observer()
    observer.schedule(ScanHandler(), SCAN_DIR, recursive=False)
    observer.start()

    logger.info("Warte auf neue Scans...")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()