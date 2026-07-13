import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QCursor, QFont


class CoordinateDisplay(QWidget):
    def __init__(self, screen_info):
        super().__init__()
        self.screen_info = screen_info

        self.setWindowTitle("PyQt6 Coordinate Tester")
        self.setFixedSize(420, 160)
        self.setStyleSheet("background-color: #1e1e2e; border-radius: 8px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        mono = QFont("Consolas", 11)

        # Screen info header
        self.header = QLabel()
        self.header.setFont(QFont("Consolas", 9))
        self.header.setStyleSheet("color: #6c6f85;")
        self.header.setText(
            f"Logical: {screen_info['logical_w']}x{screen_info['logical_h']}  |  "
            f"Physical: {screen_info['phys_w']}x{screen_info['phys_h']}  |  "
            f"DPR: {screen_info['dpr']}"
        )
        layout.addWidget(self.header)

        # Live coordinate label
        self.coord_label = QLabel("Move your mouse anywhere...")
        self.coord_label.setFont(QFont("Consolas", 14))
        self.coord_label.setStyleSheet("color: #cdd6f4; font-weight: bold;")
        layout.addWidget(self.coord_label)

        # Normalised 0-1000 grid label (used by the AI cursor system)
        self.norm_label = QLabel("")
        self.norm_label.setFont(QFont("Consolas", 11))
        self.norm_label.setStyleSheet("color: #a6e3a1;")
        layout.addWidget(self.norm_label)

        # Physical pixel label
        self.phys_label = QLabel("")
        self.phys_label.setFont(QFont("Consolas", 11))
        self.phys_label.setStyleSheet("color: #fab387;")
        layout.addWidget(self.phys_label)

        self.setLayout(layout)

        # Poll the cursor position every ~16 ms (≈60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(16)

        self.last_pos = QPoint(-1, -1)

    def refresh(self):
        pos = QCursor.pos()

        # Only redraw when the mouse actually moved
        if pos == self.last_pos:
            return
        self.last_pos = pos

        lx, ly = pos.x(), pos.y()
        lw = self.screen_info["logical_w"]
        lh = self.screen_info["logical_h"]
        dpr = self.screen_info["dpr"]

        # Normalised 0-1000 grid (matches the AI cursor prompt's coordinate system)
        nx = round((lx / lw) * 1000, 1)
        ny = round((ly / lh) * 1000, 1)

        # Physical pixel (what mss captures)
        px = int(lx * dpr)
        py = int(ly * dpr)

        self.coord_label.setText(f"PyQt6 Logical:   X = {lx:>5},  Y = {ly:>5}")
        self.norm_label.setText(f"AI 0-1000 Grid:  X = {nx:>7},  Y = {ny:>7}")
        self.phys_label.setText(f"Physical Pixels: X = {px:>5},  Y = {py:>5}")

        # Also print to terminal
        print(f"\r[Logical] ({lx:>5}, {ly:>5})  "
              f"[AI grid] ({nx:>7}, {ny:>7})  "
              f"[Physical] ({px:>5}, {py:>5})", end="", flush=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    logical_w = screen.size().width()
    logical_h = screen.size().height()
    dpr = screen.devicePixelRatio()
    phys_w = int(logical_w * dpr)
    phys_h = int(logical_h * dpr)

    print("=== PyQt6 Display Info ===")
    print(f"  Logical (Qt) size : {logical_w} x {logical_h}")
    print(f"  Device Pixel Ratio: {dpr}")
    print(f"  Physical pixels   : {phys_w} x {phys_h}")
    print("==========================")
    print("Move your mouse — live coordinates will update below:\n")

    screen_info = {
        "logical_w": logical_w,
        "logical_h": logical_h,
        "phys_w": phys_w,
        "phys_h": phys_h,
        "dpr": dpr,
    }

    window = CoordinateDisplay(screen_info)
    window.show()

    sys.exit(app.exec())
