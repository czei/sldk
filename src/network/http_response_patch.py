"""
Patch for Adafruit HTTP Response to handle connection errors more gracefully.
Copyright 2024 3DUPFitters LLC
"""

def apply_http_response_patch():
    """
    Apply patches to the adafruit_httpserver Response class to make it more
    robust against client disconnection errors.
    
    This should be called at the start of the app before using the web server.
    """
    try:
        from adafruit_httpserver.response import Response
        
        # Save original method
        original_send_bytes = Response._send_bytes
        
        # Create enhanced version with better error handling
        def enhanced_send_bytes(self, data):
            """Enhanced _send_bytes method with better error handling for disconnections"""
            try:
                return original_send_bytes(self, data)
            except (BrokenPipeError, OSError) as e:
                # These errors are common when client disconnects prematurely
                # Just log and return quietly instead of crashing
                from src.utils.error_handler import ErrorHandler
                logger = ErrorHandler("error_log")
                if isinstance(e, BrokenPipeError) or (hasattr(e, 'args') and e.args and e.args[0] in (32, 104)):
                    logger.debug(f"Client disconnected during response: {type(e).__name__}")
                else:
                    logger.error(e, f"Error sending response: {type(e).__name__}")
                return 0  # Indicate no bytes sent
        
        # Replace the method
        Response._send_bytes = enhanced_send_bytes
        
        return True
    except Exception as e:
        # If patching fails, log error but continue
        from src.utils.error_handler import ErrorHandler
        logger = ErrorHandler("error_log")
        logger.error(e, "Failed to apply HTTP response patch")
        return False