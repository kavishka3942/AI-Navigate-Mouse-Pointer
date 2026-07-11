"""
core/signals.py
~~~~~~~~~~~~~~~
Centralised PyQt6 cross-thread signal definitions.

The primary cross-thread signal (target_found) currently lives on
VisionWorker in agents/vision_grounding.py because it is tightly coupled
to that class's QThread lifecycle.

This module is reserved for any future application-wide signals that need
to be shared across multiple unrelated components (e.g. a global status bus).
"""
