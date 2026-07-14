"""
gui/pill_styles.py
Custom painted widgets to replicate the Figma designs (Comet border, Equalizer, etc.)
"""
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QConicalGradient, QPainterPath
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit

# --- Color Tokens from Figma ---
COLOR_OBSIDIAN = QColor(18, 18, 20, 204)  # #121214 with 80% opacity
COLOR_BORDER = QColor(45, 45, 48)         # #2D2D30
COLOR_SILVER = QColor(160, 160, 165)      # Muted silver for placeholder
COLOR_WHITE = QColor(245, 246, 248)       # High contrast white
COLOR_GRAY_TEXT = QColor(140, 140, 145)   # Small gray text
COLOR_GREEN_DOT = QColor(52, 199, 89)     # Live green status dot
COLOR_INDIGO = QColor(99, 102, 241)       # Indigo for accents

class GlossyInputWidget(QWidget):
    """Frame 1: Input state with rotating comet border effect and actual text input."""
    return_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 40)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Animation timer for the comet border
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_angle)
        self._timer.start(16) # ~60 FPS

        # Create the actual QLineEdit overlay
        self._line_edit = QLineEdit(self)
        self._line_edit.setGeometry(10, 8, 300, 24)  # Leave room for border
        self._line_edit.setPlaceholderText("Where should I guide you?")
        self._line_edit.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {COLOR_SILVER.name()};
                font-family: 'Inter', 'SF Pro', sans-serif;
                font-size: 13px;
                padding: 0 4px;
            }}
            QLineEdit:focus {{
                outline: none;
            }}
        """)
        self._line_edit.returnPressed.connect(self._on_return)
        self._line_edit.show()

    def _update_angle(self):
        self._angle = (self._angle + 2) % 360
        self.update()

    def _on_return(self):
        text = self._line_edit.text().strip()
        self._line_edit.clear()
        self.return_pressed.emit(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        radius = 20.0

        # 1. Draw Obsidian Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COLOR_OBSIDIAN))
        painter.drawRoundedRect(rect, radius, radius)

        # 2. Draw Base Gray Border
        painter.setPen(QPen(COLOR_BORDER, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)

        # 3. Draw Rotating Comet Arc (Indigo -> Violet -> Pink -> Cyan -> Blue -> Transparent)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)

        # Create a conical gradient centered on the widget
        center = QPointF(self.width() / 2, self.height() / 2)
        gradient = QConicalGradient(center, self._angle)
        gradient.setColorAt(0.0, QColor(99, 102, 241))   # Indigo
        gradient.setColorAt(0.2, QColor(139, 92, 246))   # Violet
        gradient.setColorAt(0.4, QColor(236, 72, 153))   # Pink
        gradient.setColorAt(0.6, QColor(34, 211, 238))   # Cyan
        gradient.setColorAt(0.8, QColor(59, 130, 246))   # Blue
        gradient.setColorAt(0.85, QColor(18, 18, 20, 0)) # Fade to transparent
        gradient.setColorAt(1.0, QColor(18, 18, 20, 0))

        painter.setPen(QPen(QBrush(gradient), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, radius, radius)

    def get_text(self):
        return self._line_edit.text()

    def clear_text(self):
        self._line_edit.clear()

    def set_focus(self):
        self._line_edit.setFocus()

class ProcessingWidget(QWidget):
    """Frame 2: Processing state with equalizer bars and animated text."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 40)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(100)

    def _animate(self):
        self._phase = (self._phase + 1) % 20
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COLOR_OBSIDIAN))
        painter.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), 20, 20)

        # Equalizer Bars (5 bars)
        bar_width = 3
        bar_spacing = 5
        start_x = 20
        max_height = 16
        for i in range(5):
            # Sine wave animation for height
            height = max(4, int(max_height * abs(__import__('math').sin((self._phase + i * 3) * 0.5))))
            x = start_x + i * (bar_width + bar_spacing)
            y = (self.height() - height) // 2
            painter.setBrush(QBrush(COLOR_INDIGO))
            painter.drawRoundedRect(QRectF(x, y, bar_width, height), 1.5, 1.5)

        # Animated Text "Analyzing query..."
        painter.setPen(QPen(COLOR_WHITE))
        font = QFont('Inter', 13)
        painter.setFont(font)
        dots = "." * ((self._phase // 5) % 4)
        painter.drawText(QRectF(60, 0, 140, 40), Qt.AlignmentFlag.AlignVCenter, f"Analyzing query{dots}")

class GuidanceWidget(QWidget):
    """Frame 3: Notification/Guidance state."""
    dismissed = pyqtSignal()

    def __init__(self, text: str = "Click to expand menu", parent=None):
        super().__init__(parent)
        self._text = text
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(220, 50) # Adjust size as needed

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(18, 18, 20, 230)))
        painter.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), 14, 14)

        # Green Status Dot
        painter.setBrush(QBrush(COLOR_GREEN_DOT))
        painter.drawEllipse(QPointF(16, 16), 3, 3)

        # "AI ASSISTANT" Text
        painter.setPen(QPen(COLOR_GRAY_TEXT))
        font_small = QFont('Inter', 9)
        font_small.setCapitalization(QFont.Capitalization.AllUppercase)
        painter.setFont(font_small)
        painter.drawText(QRectF(24, 6, 100, 14), Qt.AlignmentFlag.AlignLeft, "AI ASSISTANT")

        # Instruction Text
        painter.setPen(QPen(COLOR_WHITE))
        font_bold = QFont('Inter', 13)
        font_bold.setBold(True)
        painter.setFont(font_bold)
        painter.drawText(QRectF(16, 24, 180, 20), Qt.AlignmentFlag.AlignLeft, f"👉 {self._text}")

        # Chevron
        painter.setPen(QPen(COLOR_GRAY_TEXT, 1.5))
        painter.drawLine(QPointF(self.width() - 20, 20), QPointF(self.width() - 14, 25))
        painter.drawLine(QPointF(self.width() - 20, 30), QPointF(self.width() - 14, 25))

    def mousePressEvent(self, event):
        self.dismissed.emit()