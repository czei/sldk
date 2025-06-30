#!/usr/bin/env python3
"""SLDK Test Suite

Comprehensive test suite for the Scrolling LED Dev Kit (SLDK) library.

Test Structure:
- unit/: Unit tests for individual components
- integration/: Integration tests for component interaction  
- fixtures/: Test data and fixtures

Test Categories:
- Core: App, display, content queue functionality
- Web: Web framework, templates, forms
- Effects: Animation effects and particle systems
- Hardware: CircuitPython compatibility and hardware simulation

Usage:
    # Run all tests
    pytest
    
    # Run specific test category
    pytest -m unit
    pytest -m integration
    pytest -m web
    pytest -m effects
    
    # Run with coverage
    pytest --cov=sldk
    
    # Run specific test file
    pytest tests/unit/app/test_sldk_app.py
"""

__version__ = "1.0.0"