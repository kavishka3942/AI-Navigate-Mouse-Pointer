import sys
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)

# Get the primary screen object
screen = QApplication.primaryScreen()

# Logical sizes (might be downscaled by OS settings)
logical_width = screen.size().width()
logical_height = screen.size().height()

# Device Pixel Ratio (e.g., 1.0 for 100%, 1.5 for 150%)
pixel_ratio = screen.devicePixelRatio()

# Calculate actual raw physical pixels
real_width = int(logical_width * pixel_ratio)
real_height = int(logical_height * pixel_ratio)

print(f"OS Scaled Size: {logical_width}x{logical_height}")
print(f"OS Scaling Factor: {pixel_ratio}x")
print(f"True Physical Size: {real_width}x{real_height} pixels")