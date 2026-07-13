import time
import mss
import threading
from PIL import Image
from pynput import mouse

# ==========================================
# CONFIGURATION SETTINGS
# ==========================================
# Initial delay (in seconds) before taking the first screenshot after a click.
INITIAL_DELAY_SEC = 1.0       

# Option to take multiple screenshots after the initial click.
# If False, it will only take exactly ONE screenshot per click (after INITIAL_DELAY_SEC).
TAKE_MULTIPLE = False          

# The total duration (in seconds) to keep taking screenshots if TAKE_MULTIPLE is True.
TOTAL_DURATION_SEC = 5.0      

# The time interval (in seconds) between each subsequent screenshot during the multiple-screenshot phase.
INTERVAL_SEC = 1.0            

# Global flag to prevent starting a new screenshot loop if the user clicks repeatedly while one is already running.
is_taking_screenshots = False


def take_screenshot(filename="screenshot.jpg"):
    """Captures the primary monitor and saves it to a file, using logic from screenshot.py."""
    with mss.mss() as sct:
        # Grab the primary monitor screen
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image and save
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.save(filename)
        print(f"[+] Saved {filename}")


def screenshot_sequence():
    """Handles the timing and looping logic for taking the screenshots."""
    global is_taking_screenshots
    is_taking_screenshots = True
    
    # ---------------------------------------------------------
    # STEP 1: Wait for the initial delay before the first shot
    # ---------------------------------------------------------
    print(f"Click detected! Waiting {INITIAL_DELAY_SEC} seconds before taking the first screenshot...")
    time.sleep(INITIAL_DELAY_SEC)
    
    # Take the first screenshot
    timestamp = int(time.time() * 1000) # Use milliseconds for unique filenames
    take_screenshot(f"screenshot_{timestamp}.jpg")
    
    # ---------------------------------------------------------
    # STEP 2: Handle multiple screenshots if enabled
    # ---------------------------------------------------------
    if TAKE_MULTIPLE:
        print(f"Multiple screenshots enabled. Capturing for the next {TOTAL_DURATION_SEC} seconds...")
        start_time = time.time()
        
        # Keep looping as long as the elapsed time is less than TOTAL_DURATION_SEC
        while (time.time() - start_time) < TOTAL_DURATION_SEC:
            
            # Wait for the specified interval before taking the next one
            time.sleep(INTERVAL_SEC)
            
            # Re-check the time in case the sleep pushed us past the duration limit
            if (time.time() - start_time) >= TOTAL_DURATION_SEC:
                break
                
            # Take the subsequent screenshot
            timestamp = int(time.time() * 1000)
            take_screenshot(f"screenshot_{timestamp}.jpg")
            
    print("Screenshot sequence completed. Ready for the next click.\n")
    
    # Sequence finished, allow new clicks to trigger it again
    is_taking_screenshots = False


def on_click(x, y, button, pressed):
    """Callback function triggered by pynput whenever a mouse click happens."""
    
    # 'pressed' is True when mouse button goes down, False when it comes up.
    # We only want to trigger our logic once per click (when it goes down).
    if pressed:
        # If we are already currently in a screenshot sequence, ignore this new click.
        # This prevents spam-clicking from spawning hundreds of screenshot threads.
        if not is_taking_screenshots:
            # We run the sequence in a background Thread. 
            # Why? Because if we put time.sleep() directly inside this on_click function,
            # it will freeze the mouse listener and potentially lag the system's mouse input!
            threading.Thread(target=screenshot_sequence, daemon=True).start()


def main():
    print("=====================================================")
    print("Screenshot Click Listener Started")
    print("=====================================================")
    print(f"Initial Delay: {INITIAL_DELAY_SEC}s")
    print(f"Take Multiple: {TAKE_MULTIPLE}")
    if TAKE_MULTIPLE:
        print(f"Duration:      {TOTAL_DURATION_SEC}s")
        print(f"Interval:      {INTERVAL_SEC}s")
    print("=====================================================")
    print("Listening for mouse clicks...")
    print("Press 'Esc' anywhere or 'Ctrl+C' in this terminal to STOP.")
    print("=====================================================\n")
    
    # We will use an Event to keep the main thread alive and let it catch signals cleanly
    import threading
    exit_event = threading.Event()

    def on_press(key):
        from pynput.keyboard import Key
        if key == Key.esc:
            print("\n[!] Esc pressed. Exiting...")
            exit_event.set()
            return False # Stops the keyboard listener

    # Start keyboard listener for the Esc key
    from pynput import keyboard
    kb_listener = keyboard.Listener(on_press=on_press)
    kb_listener.start()
    
    # Start the mouse listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    try:
        # Wait until the exit_event is set (e.g. by pressing Esc)
        # Using a timeout loop allows Python to catch KeyboardInterrupt (Ctrl+C)
        while not exit_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C pressed. Exiting...")
    finally:
        mouse_listener.stop()
        kb_listener.stop()


if __name__ == "__main__":
    main()
