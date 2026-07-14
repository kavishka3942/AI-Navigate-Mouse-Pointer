"""
gui/chatbot_widget.py
Updated UI to match Figma designs using custom painted widgets.
"""
from __future__ import annotations
from enum import Enum
from PyQt6.QtCore import QPropertyAnimation, QPoint, QRect, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QVBoxLayout,
    QWidget,
)
from gui.pill_styles import GlossyInputWidget, ProcessingWidget, GuidanceWidget
from pynput.mouse import Listener as MouseListener # NEW: For global click detection
class _ChatState(Enum):
    PROCESSING = "processing"
    NOTIFICATION = "notification"
    IDLE = "idle"

class InputBox(QFrame):
    """Frame 1: Static, anchored input pill with glossy border."""
    submitted = pyqtSignal(str)

    def __init__(self, parent=None, cursor_overlay=None):
        super().__init__(parent)
        self._cursor_overlay = cursor_overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Use the new GlossyInputWidget
        self._glossy_input = GlossyInputWidget(self)
        self._glossy_input.return_pressed.connect(self._on_submit)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._glossy_input)
        self.hide()

    def show_at_cursor(self):
        pos = self._cursor_anchor_point()
        # Center the 320x40 pill on the cursor
        geom = QRect(pos.x() - 160, pos.y() - 20, 320, 40)
        
        screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            if geom.right() > avail.right(): geom.moveRight(avail.right() - 8)
            if geom.left() < avail.left(): geom.moveLeft(avail.left() + 8)
            
        self.setGeometry(geom)
        self.show()
        self.raise_()
        # Set focus to the line edit after a short delay
        QTimer.singleShot(10, self._glossy_input.set_focus)

    def _on_submit(self, text: str):
        if text:  # Only submit if there's actual text
            self.hide()
            self.submitted.emit(text)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.isVisible():
            self.hide()

    def _cursor_anchor_point(self) -> QPoint:
        if self._cursor_overlay and getattr(self._cursor_overlay, "current_pos", None):
            return QPoint(int(self._cursor_overlay.current_pos.x()), int(self._cursor_overlay.current_pos.y()))
        return QCursor.pos()

class ProcessingIndicator(QFrame):
    """Frame 2: Compact processing pill that follows the cursor."""
    def __init__(self, parent=None, cursor_overlay=None):
        super().__init__(parent)
        self._cursor_overlay = cursor_overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)

        self._processing_widget = ProcessingWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._processing_widget)
        
        # Timer to follow cursor
        self._follow_timer = QTimer(self)
        self._follow_timer.timeout.connect(self._follow_cursor)
        self.hide()

    def start(self):
        """Show the processing indicator and start following cursor."""
        self._follow_cursor()  # Position immediately
        self.show()
        self.raise_()
        self._follow_timer.start(16)  # Update position every 16ms (~60fps)

    def stop(self):
        """Hide the processing indicator and stop following."""
        self._follow_timer.stop()
        self.hide()

    def _follow_cursor(self):
        if not self.isVisible(): 
            return
        anchor = self._cursor_anchor_point()
        # Position to the right of the cursor
        x = anchor.x() + 14
        y = anchor.y() - 20
        self.move(x, y)

    def _cursor_anchor_point(self) -> QPoint:
        if self._cursor_overlay and getattr(self._cursor_overlay, "current_pos", None):
            return QPoint(int(self._cursor_overlay.current_pos.x()), int(self._cursor_overlay.current_pos.y()))
        return QCursor.pos()

class NotificationBubble(QFrame):
    """Frame 3: Guidance bubble that follows the cursor and dismisses on ANY click."""
    dismissed = pyqtSignal()

    def __init__(self, parent=None, cursor_overlay=None):
        super().__init__(parent)
        self._cursor_overlay = cursor_overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._guidance_widget = GuidanceWidget("Processing complete.", self)
        self._guidance_widget.dismissed.connect(self._on_dismiss)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._guidance_widget)
        
        self._follow_timer = QTimer(self)
        self._follow_timer.timeout.connect(self._follow_cursor)
        
        # NEW: Initialize the global mouse listener variable
        self._mouse_listener = None
        self.hide()

    def start_processing(self):
        self.hide()

    def show_notification(self, text: str):
        self._guidance_widget._text = text or "Processing complete."
        self._guidance_widget.update()
        self._follow_cursor()
        self.show()
        self.raise_()
        self._follow_timer.start(16)
        
        # NEW: Start listening for global mouse clicks to auto-dismiss
        self._start_global_click_listener()

    def _on_dismiss(self):
        """Safely hides the bubble and stops all timers/listeners."""
        if not self.isVisible():
            return
            
        self._follow_timer.stop()
        self._stop_global_click_listener()
        self.hide()
        self.dismissed.emit()

    # --- NEW: Global Click Detection Logic ---
    def _start_global_click_listener(self):
        """Starts a passive background thread to listen for any mouse click."""
        if self._mouse_listener is None:
            self._mouse_listener = MouseListener(on_click=self._on_global_click)
            self._mouse_listener.start()

    def _stop_global_click_listener(self):
        """Stops the background listener."""
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None

    def _on_global_click(self, x, y, button, pressed):
        """
        Callback for pynput. Runs in a background thread.
        If a mouse button is PRESSED anywhere on the screen, trigger dismiss.
        """
        if pressed:
            # Use QTimer to safely marshal the call back to the main GUI thread
            QTimer.singleShot(0, self._on_dismiss)
            return False  # Return False to stop the listener after the first click
        return True

    # --- End Global Click Detection Logic ---

    def _follow_cursor(self):
        if not self.isVisible(): 
            return
        anchor = self._cursor_anchor_point()
        x = anchor.x() + 14
        y = anchor.y() - 25
        self.move(x, y)

    def _cursor_anchor_point(self) -> QPoint:
        if self._cursor_overlay and getattr(self._cursor_overlay, "current_pos", None):
            return QPoint(int(self._cursor_overlay.current_pos.x()), int(self._cursor_overlay.current_pos.y()))
        return QCursor.pos()

# Backwards-compat alias
ChatInput = InputBox
Notification = NotificationBubble