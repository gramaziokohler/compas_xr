import threading


download_event = threading.Event()

def _callback_download():
    while True:
        print ("dummy")
        download_event.set()

download_thread = threading.Thread(target=_callback_download())
download_thread.start()

# Set a timeout using threading.Timer to stop the thread after a specified time (e.g., 5 seconds)
timeout_seconds = 0.5
timeout_timer = threading.Timer(timeout_seconds, download_thread.join)
timeout_timer.start()

download_event.wait(0.5)  # Wait for the download to complete