"""Display system for LED matrix displays."""

from .interface import DisplayInterface
from .factory import create_display
from .unified import UnifiedDisplay

__all__ = ['DisplayInterface', 'create_display', 'UnifiedDisplay']