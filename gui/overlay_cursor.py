"""
gui/overlay_cursor.py
~~~~~~~~~~~~~~~~~~~~~
AICursorOverlay – the transparent, always-on-top PyQt6 window that draws
the glowing secondary cursor and orchestrates the VisionWorker thread.

Extracted verbatim from main.py.  The only changes are:
  - Imports now come from config.settings and agents.vision_grounding.
  - OllamaWorker references renamed to VisionWorker.
  - Magic numbers replaced by named constants from settings.
  - Logic and paint code are 100% identical to the original.
"""
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QCursor
from PyQt6.QtWidgets import QApplication, QWidget
from pynput import keyboard

from config.settings import (
    HOTKEY_TRIGGER,
    HOTKEY_EXIT,
    FPS,
    LERP_FACTOR,
    AI_LOCK_DURATION_MS,
    CURSOR_SCALE,
)


class AICursorOverlay(QWidget):
    chat_hotkey_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Transparent, frameless, passthrough window covering all input
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Cover primary screen
        primary_screen   = QApplication.primaryScreen()
        self.screen_rect = primary_screen.geometry()
        self.setGeometry(self.screen_rect)
        # Store logical dimensions and device pixel ratio for accurate mapping
        self.screen_width  = self.screen_rect.width()
        self.screen_height = self.screen_rect.height()
        self.dpr           = primary_screen.devicePixelRatio()
        print(f"[DEBUG] Screen geometry: {self.screen_width}x{self.screen_height}, DPR={self.dpr}")

        # State tracking for smooth animation
        self.current_pos   = QPointF(QCursor.pos())
        self.target_pos    = QPointF(QCursor.pos())
        self.last_mouse_pos = QCursor.pos()
        self.following_ai  = False

        # Setup Global Hotkey for triggering the vision loop
        self.hotkey_listener = keyboard.GlobalHotKeys({
            HOTKEY_TRIGGER: self.on_hotkey_trigger,
            HOTKEY_EXIT:    self.on_esc,
        })
        self.hotkey_listener.start()

        # 60 FPS repainting and animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_cursor)
        self.timer.start(1000 // FPS)

    # ------------------------------------------------------------------
    def on_esc(self):
        print("\n[!] Esc pressed. Exiting...")
        QApplication.quit()

    def on_hotkey_trigger(self):
        self.chat_hotkey_pressed.emit()

    # ------------------------------------------------------------------
    def set_new_target(self, physical_x, physical_y):
        """Called automatically when the QThread emits the 'target_found' signal.

        The VLM returns coordinates in the *physical* pixel space (e.g. 1920x1080).
        PyQt6 operates in *logical* coordinates scaled by the Device Pixel Ratio.
        We must divide by DPR before passing the values to the Qt canvas.
        """
        # --- High-DPI Physical → Logical Coordinate Conversion ---
        dpr       = QApplication.primaryScreen().devicePixelRatio()
        logical_x = int(physical_x / dpr)
        logical_y = int(physical_y / dpr)
        print(
            f"[DPI FIX] VLM Physical ({physical_x}, {physical_y}) "
            f"-> PyQt6 Logical ({logical_x}, {logical_y}) "
            f"[DPR: {dpr:.2f}]"
        )
        # ----------------------------------------------------------

        self.target_pos   = QPointF(logical_x, logical_y)
        self.following_ai = True  # Enable AI tracking mode

        # Stay at the location for AI_LOCK_DURATION_MS, then revert to mouse
        QTimer.singleShot(AI_LOCK_DURATION_MS, self.revert_to_mouse)

    def revert_to_mouse(self):
        self.following_ai = False

    # ------------------------------------------------------------------
    def update_cursor(self):
        """Called ~60 times per second to interpolate the cursor's position."""
        current_mouse        = QCursor.pos()
        self.last_mouse_pos  = current_mouse  # Keep track for smooth revert

        # If we are not following AI coordinates, follow the physical mouse
        if not self.following_ai:
            self.target_pos = QPointF(current_mouse)

        # Calculate the distance remaining
        dx = self.target_pos.x() - self.current_pos.x()
        dy = self.target_pos.y() - self.current_pos.y()

        # Smooth interpolation – moves LERP_FACTOR of the remaining gap per frame
        self.current_pos.setX(self.current_pos.x() + dx * LERP_FACTOR)
        self.current_pos.setY(self.current_pos.y() + dy * LERP_FACTOR)

        self.update()  # Trigger paintEvent

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.current_pos.x()
        cy = self.current_pos.y()

        # Standard cursor arrow shape coordinates
        points = [
            QPointF(0,  0),
            QPointF(0,  20),
            QPointF(5,  16),
            QPointF(9,  25),
            QPointF(12, 24),
            QPointF(8,  15),
            QPointF(14, 15),
        ]

        scale   = CURSOR_SCALE
        polygon = QPolygonF()
        for p in points:
            polygon.append(QPointF(p.x() * scale + cx, p.y() * scale + cy))

        # Render blue glow with rounded edges
        glow_color = QColor(0, 100, 255)
        for width, alpha in [(12, 20), (8, 40), (6, 80), (3, 150)]:
            glow_color.setAlpha(alpha)
            glow_pen = QPen(glow_color)
            glow_pen.setWidth(width)
            glow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolygon(polygon)

        # Render solid white inner arrow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawPolygon(polygon)
