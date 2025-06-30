"""Over-The-Air (OTA) update system for SLDK.

Provides secure, reliable updates for CircuitPython devices.
"""

from .updater import OTAUpdater
from .client import OTAClient
from .server import OTAServer
from .manifest import UpdateManifest

__all__ = ['OTAUpdater', 'OTAClient', 'OTAServer', 'UpdateManifest']