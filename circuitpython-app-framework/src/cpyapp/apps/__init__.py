"""
CircuitPython App Framework - Simple Applications

This module provides simplified, beginner-friendly interfaces for creating
LED matrix applications while maintaining the full power of the framework.
"""

from .simple import SimpleScrollApp, scroll_text, scroll_url, scroll_function

__all__ = [
    'SimpleScrollApp',
    'scroll_text', 
    'scroll_url',
    'scroll_function'
]