"""
main.py – Application Entry Point
"""
import sys
import signal

from PyQt6.QtWidgets import QApplication

from config.settings import TARGET_ELEMENT
from agents.vision_grounding import VisionWorker
from gui.chatbot_widget import ChatInput, Notification, ProcessingIndicator
from gui.overlay_cursor import AICursorOverlay


def main() -> None:
    print("=====================================================")
    print("AI Vision-to-Cursor Control Started")
    print("=====================================================")
    print(f"- Default target element: '{TARGET_ELEMENT}'")
    print("- Press 'Ctrl+Shift+A' to open or hide the chat pill.")
    print("- Type a target, press Enter, and the VLM will search for that element.")
    print("- Press 'Esc' or 'Ctrl+C' to exit cleanly.")
    print("=====================================================\n")

    # Allow Ctrl+C to cleanly kill the PyQt application from the terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    overlay = AICursorOverlay()
    overlay.show()

    input_box = ChatInput(cursor_overlay=overlay)
    notification = Notification(cursor_overlay=overlay)
    
    # NEW: Create a separate ProcessingIndicator instance
    processing_indicator = ProcessingIndicator(cursor_overlay=overlay)

    worker_state = {"worker": None}

    def toggle_input_box():
        if input_box.isVisible():
            input_box.hide()
            return
        input_box.show_at_cursor()

    def launch_vision_search(target_text: str):
        worker = worker_state["worker"]
        if worker is not None and worker.isRunning():
            print("[-] Vision task already running, please wait.")
            return

        primary_screen = QApplication.primaryScreen()
        if primary_screen is None:
            print("[-] No primary screen detected; cannot start vision worker.")
            return

        screen_rect = primary_screen.geometry()
        dpr = primary_screen.devicePixelRatio()
        phys_width = int(screen_rect.width() * dpr)
        phys_height = int(screen_rect.height() * dpr)
        user_input = target_text.strip()

        # NEW: Show processing indicator instead of notification
        notification.start_processing()  # Hides notification
        processing_indicator.start()     # Shows processing pill

        worker = VisionWorker(phys_width, phys_height, user_input)
        worker_state["worker"] = worker

        worker.target_found.connect(overlay.set_new_target)
        
        # When workflow completes, stop processing and show notification
        def on_workflow_complete(x, y, label):
            processing_indicator.stop()  # Stop processing indicator
            notification.show_notification(label or "No label returned")
        
        worker.result_ready.connect(on_workflow_complete)

        def clear_worker():
            worker_state["worker"] = None

        worker.finished.connect(clear_worker)
        worker.start()

    overlay.chat_hotkey_pressed.connect(toggle_input_box)
    input_box.submitted.connect(launch_vision_search)
    notification.dismissed.connect(lambda: print("[+] Notification dismissed"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()