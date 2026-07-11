"""
core/os_utils.py
~~~~~~~~~~~~~~~~
Low-level OS helpers: screen capture via mss.
Extracted verbatim from OllamaWorker.run() in the original main.py.
"""
import os
import time

import mss
from PIL import Image


def capture_screen(screenshot_dir: str) -> str:
    """Capture the primary monitor and save it as a JPEG.

    Identical to the inline mss block that was in OllamaWorker.run().

    Args:
        screenshot_dir: Directory where the screenshot will be saved.
                        Created automatically if it does not exist.

    Returns:
        Absolute path to the saved JPEG file.
    """
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    timestamp = int(time.time() * 1000)
    filename  = os.path.join(screenshot_dir, f"vision_capture_{timestamp}.jpg")

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.save(filename)
        print(f"[+] Saved {filename}")

    return filename
