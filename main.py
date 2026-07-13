"""
main.py – Application Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Initialises the QApplication, creates the overlay window, and starts the
Qt event loop.  All logic lives in the sub-packages below:

    config/   – constants & environment settings
    core/     – OS utilities (screen capture)
    agents/   – VLM vision worker (and future LangGraph pipeline)
    gui/      – Qt widgets (overlay cursor, chatbot stub)

Run:
    python main.py
"""
import sys
import signal

from PyQt6.QtWidgets import QApplication

from config.settings import TARGET_ELEMENT
from agents.vision_grounding import VisionWorker
from gui.chatbot_widget import ChatInput, Notification
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

    worker_state = {"worker": None}

    def toggle_input_box():
        # Shortcut shows the static input anchored to the cursor. If already
        # visible, hide it.
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
        # CHANGED: We pass the raw user_message (target_text) to the worker
        user_input = target_text.strip()

        # Activate the floating notification bubble and show processing
        notification.start_processing()

        worker = VisionWorker(phys_width, phys_height, user_input)
        worker_state["worker"] = worker

        worker.target_found.connect(overlay.set_new_target)
        # When the vision worker returns its label, show it in the bubble
        worker.result_ready.connect(lambda _x, _y, label: notification.show_notification(label or "No label returned"))

        def clear_worker():
            worker_state["worker"] = None

        worker.finished.connect(clear_worker)
        worker.start()

    overlay.chat_hotkey_pressed.connect(toggle_input_box)
    input_box.submitted.connect(launch_vision_search)
    # Allow user to dismiss the floating notification
    notification.dismissed.connect(lambda: print("[+] Notification dismissed"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()