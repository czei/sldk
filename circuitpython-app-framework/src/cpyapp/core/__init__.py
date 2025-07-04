"""Core application components."""

from .application import BaseApplication
from .plugin import Plugin, DisplayPlugin

__all__ = ['BaseApplication', 'Plugin', 'DisplayPlugin']