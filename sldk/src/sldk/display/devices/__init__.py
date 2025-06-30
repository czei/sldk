"""SLDK Device Drivers

Hardware-specific display implementations for various LED matrix devices.
"""

# Import available devices
__all__ = []

# MatrixPortal S3 (ESP32-S3)
try:
    from .matrixportal_s3 import MatrixPortalS3Display
    __all__.append("MatrixPortalS3Display")
except ImportError:
    MatrixPortalS3Display = None

# Original MatrixPortal (ESP32)
try:
    from .matrixportal import MatrixPortalDisplay
    __all__.append("MatrixPortalDisplay")
except ImportError:
    MatrixPortalDisplay = None

# Generic displayio-based devices
try:
    from .generic_displayio import GenericDisplayIODevice
    __all__.append("GenericDisplayIODevice")
except ImportError:
    GenericDisplayIODevice = None


def detect_hardware(**kwargs):
    """Auto-detect available hardware.
    
    Args:
        **kwargs: Hardware configuration options
        
    Returns:
        DisplayInterface instance or None
    """
    # Try MatrixPortal S3 first (most common)
    if MatrixPortalS3Display:
        try:
            return MatrixPortalS3Display(**kwargs)
        except Exception:
            pass
    
    # Try original MatrixPortal
    if MatrixPortalDisplay:
        try:
            return MatrixPortalDisplay(**kwargs)
        except Exception:
            pass
    
    # Try generic displayio
    if GenericDisplayIODevice:
        try:
            return GenericDisplayIODevice(**kwargs)
        except Exception:
            pass
    
    return None