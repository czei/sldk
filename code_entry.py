"""
ThemeParkAPI - Entry point
Copyright 2024 3DUPFitters LLC
"""
import sys

# Check if running on CircuitPython
is_circuitpython = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

# Add src/lib to Python path if running on CircuitPython
if is_circuitpython:
    # For MatrixPortal S3, libraries are in src/lib
    if '/src/lib' not in sys.path:
        sys.path.append('/src/lib')
    if '/lib' not in sys.path:
        sys.path.append('/lib')  # Fallback

# Now try to import asyncio
try:
    import asyncio
except ImportError as e:
    print(f"Error importing asyncio: {e}")
    print("Path: ", sys.path)
    print("Running on CircuitPython:", is_circuitpython)
    sys.exit(1)

# Import the main application - Only run if this is being executed as the main script
if __name__ == "__main__":
    try:
        from theme_park_main import main
        
        # Run the main function
        asyncio.run(main())
    except (KeyboardInterrupt, Exception) as e:
        # Error will be logged in the main module
        print(f"Error: {e}")