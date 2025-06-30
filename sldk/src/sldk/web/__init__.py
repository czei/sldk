"""SLDK Web Framework

A lightweight, async-first web framework for CircuitPython LED applications.
Designed for ESP32 and other memory-constrained devices.
"""

from .server import SLDKWebServer
from .handlers import WebHandler, StaticFileHandler
from .templates import TemplateEngine
from .forms import FormBuilder

__all__ = [
    "SLDKWebServer",
    "WebHandler",
    "StaticFileHandler", 
    "TemplateEngine",
    "FormBuilder",
]

# Optional imports that might not be available
try:
    from .adapters import CircuitPythonAdapter, DevelopmentAdapter
    __all__.extend(["CircuitPythonAdapter", "DevelopmentAdapter"])
except ImportError:
    pass