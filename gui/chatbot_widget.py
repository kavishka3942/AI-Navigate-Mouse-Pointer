"""
gui/chatbot_widget.py
~~~~~~~~~~~~~~~~~~~~~
Split UI into two windows:

- `InputBox`: static, anchored input that appears at the mouse and
    immediately grabs focus. It hides on Enter or when losing focus and
    emits `submitted` with the entered text.

- `NotificationBubble`: a persistent floating bubble that follows the
    custom AI pointer. It shows a loading indicator while the vision AI
    runs and then displays a dismissable notification message.

This file contains both classes and re-uses the `_LoadingIndicator`.
"""
from __future__ import annotations

from enum import Enum

from PyQt6.QtCore import QAbstractAnimation, QEasingCurve, QPoint, QRect, QPropertyAnimation, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QPainter, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
)


class _ChatState(Enum):
    PROCESSING = "processing"
    NOTIFICATION = "notification"


class _LoadingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0
        self.setFixedSize(44, 14)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(140)

    def _advance(self):
        self._phase = (self._phase + 1) % 3
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        dot_color = QColor(245, 246, 248)
        centers = [11, 22, 33]
        for index, center_x in enumerate(centers):
            alpha = [80, 140, 220][(index - self._phase) % 3]
            dot_color.setAlpha(alpha)
            painter.setBrush(dot_color)
            painter.drawEllipse(QPoint(center_x, self.height() // 2), 3, 3)


class InputBox(QFrame):
    """A static, anchored input box that appears at the mouse location and
    immediately grabs focus. It hides on Enter or when it loses focus and
    emits `submitted(str)` with the entered text.
    """

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
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._width = 420
        self._height = 40

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Where should I guide you?")
        self.input.returnPressed.connect(self._on_return)
        self.input.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.addWidget(self.input)

        self.hide()

    def show_at_cursor(self):
        """Position at the current cursor logical position and show.
        The widget is frozen at that screen spot until it hides.
        """
        pos = self._cursor_anchor_point()
        geom = QRect(pos.x(), pos.y() - self._height // 2, self._width, self._height)
        # Ensure on-screen
        screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            if geom.right() > avail.right():
                geom.moveRight(avail.right() - 8)
            if geom.left() < avail.left():
                geom.moveLeft(avail.left() + 8)
            if geom.top() < avail.top():
                geom.moveTop(avail.top() + 8)

        self.setGeometry(geom)
        self.show()
        self.raise_()
        QTimer.singleShot(0, self.input.setFocus)

    def _on_return(self):
        text = self.input.text().strip()
        self.input.clear()
        self.hide()
        self.submitted.emit(text)

    def focusOutEvent(self, event):
        # Hide immediately when user clicks away
        super().focusOutEvent(event)
        if self.isVisible():
            self.hide()

    def _cursor_anchor_point(self) -> QPoint:
        if self._cursor_overlay is not None:
            current_pos = getattr(self._cursor_overlay, "current_pos", None)
            if current_pos is not None:
                try:
                    return QPoint(int(current_pos.x()), int(current_pos.y()))
                except Exception:
                    pass
        return QCursor.pos()


class ProcessingIndicator(QFrame):
    """A compact, click-through floating loader that follows the AI pointer.
    Used while the VisionWorker is processing.
    """

    def __init__(self, parent=None, cursor_overlay=None):
        super().__init__(parent)
        self._cursor_overlay = cursor_overlay
        self._anchor_gap = 8
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # Click-through by default
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)

        self._loading = _LoadingIndicator(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self._loading)

        self._follow_timer = QTimer(self)
        self._follow_timer.setInterval(16)
        self._follow_timer.timeout.connect(self._follow_cursor)

        self.hide()

    def start(self):
        self._loading.show()
        self.adjustSize()
        self._follow_timer.start()
        self.show()
        self.raise_()

    def stop(self):
        self._follow_timer.stop()
        self.hide()

    def _follow_cursor(self):
        if not self.isVisible():
            return
        anchor = self._cursor_anchor_point()
        x = anchor.x() + self._anchor_gap
        y = anchor.y() - self.height() // 2
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            if x + self.width() > avail.right() - 8:
                x = anchor.x() - self.width() - self._anchor_gap
            if y < avail.top() + 8:
                y = avail.top() + 8
            if y + self.height() > avail.bottom() - 8:
                y = avail.bottom() - self.height() - 8

        self.move(x, y)

    def _cursor_anchor_point(self) -> QPoint:
        if self._cursor_overlay is not None:
            current_pos = getattr(self._cursor_overlay, "current_pos", None)
            if current_pos is not None:
                try:
                    return QPoint(int(current_pos.x()), int(current_pos.y()))
                except Exception:
                    pass
        return QCursor.pos()


class NotificationBubble(QFrame):
    """Floating bubble that follows the AI pointer. Shows a loading
    indicator during processing and then displays a dismissable message.
    """

    dismissed = pyqtSignal()

    def __init__(self, parent=None, cursor_overlay=None):
        super().__init__(parent)
        self._cursor_overlay = cursor_overlay
        self._state = _ChatState.PROCESSING
        self._anchor_gap = 14
        self._follow_interval_ms = 16

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._follow_timer = QTimer(self)
        self._follow_timer.setInterval(self._follow_interval_ms)
        self._follow_timer.timeout.connect(self._follow_cursor)

        # Small, separate processing indicator that remains minimal and
        # follows the pointer while the AI is thinking.
        self._processing_indicator = ProcessingIndicator(cursor_overlay=self._cursor_overlay)

        self._content = QWidget(self)
        self._content.setStyleSheet(
            """
            QWidget { background-color: rgba(18,18,20,0.9); border-radius: 14px; }
            QLabel { color: #F5F6F8; font-weight: 600; }
            """
        )

        layout = QHBoxLayout(self._content)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        self._loading = _LoadingIndicator(self._content)
        self._label = QLabel(self._content)
        self._label.hide()
        self._dismiss_btn = QPushButton("Dismiss", self._content)
        self._dismiss_btn.setFixedHeight(20)
        self._dismiss_btn.clicked.connect(self._on_dismiss)
        self._dismiss_btn.hide()

        layout.addWidget(self._loading)
        layout.addWidget(self._label)
        layout.addWidget(self._dismiss_btn)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._content)

        self.hide()

    def start_processing(self):
        self._label.hide()
        self._dismiss_btn.hide()
        # Hide the full bubble while showing the compact processing indicator
        self.hide()
        self._processing_indicator.start()

    def show_notification(self, text: str):
        # Stop and hide the minimal processing indicator if active
        try:
            self._processing_indicator.stop()
        except Exception:
            pass

        self._loading.hide()
        self._label.setText(text or "")
        self._label.show()
        self._dismiss_btn.show()
        # Show and become interactive so the user can dismiss
        self._set_click_through(False)
        # Ensure layout and sizing are recalculated before positioning
        self.adjustSize()
        # Position immediately next to the pointer then start following
        self._follow_cursor()
        self.show()
        self.raise_()
        self._follow_timer.start()

    def _on_dismiss(self):
        self._follow_timer.stop()
        self.hide()
        self.dismissed.emit()

    def _set_click_through(self, enabled: bool):
        # When enabled=True we want clicks to pass through: set TransparentForMouseEvents
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)
        # Also set WindowTransparentForInput flag
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enabled)
        if self.isVisible():
            # Re-show to ensure flags take effect
            self.hide()
            self.show()

    def _follow_cursor(self):
        if not self.isVisible():
            return
        anchor = self._cursor_anchor_point()
        # place bubble to the right of cursor
        x = anchor.x() + self._anchor_gap
        y = anchor.y() - self.height() // 2
        screen = QApplication.screenAt(anchor) or QApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            if x + self.width() > avail.right() - 8:
                x = anchor.x() - self.width() - self._anchor_gap
            if y < avail.top() + 8:
                y = avail.top() + 8
            if y + self.height() > avail.bottom() - 8:
                y = avail.bottom() - self.height() - 8

        self.move(x, y)

    def _cursor_anchor_point(self) -> QPoint:
        if self._cursor_overlay is not None:
            current_pos = getattr(self._cursor_overlay, "current_pos", None)
            if current_pos is not None:
                try:
                    return QPoint(int(current_pos.x()), int(current_pos.y()))
                except Exception:
                    pass
        return QCursor.pos()


# Backwards-compat alias for importing
ChatInput = InputBox
Notification = NotificationBubble
