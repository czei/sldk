"""
Tests for the display implementation module.
"""
import time
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.ui.display_impl import AsyncScrollingDisplay, SimpleScrollingDisplay
from src.utils.color_utils import ColorUtils

@pytest.mark.skip("Needs more complex mocking of displayio")
class TestAsyncScrollingDisplay:
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    def test_initialization(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test initializing the AsyncScrollingDisplay"""
        # This test needs more complex mocking setup for CircuitPython display modules
        # Skipping for now
        pass
    
    def test_set_colors(self):
        """Test setting colors from settings"""
        # Skip - requires complex display mocking
        pass

    def test_off(self):
        """Test turning off all display elements"""
        # Skip - requires complex display mocking
        pass

    @pytest.mark.asyncio
    async def test_show_splash(self):
        """Test showing the splash screen"""
        # Skip - requires complex display mocking
        pass

    @pytest.mark.asyncio
    async def test_show_ride_closed(self):
        """Test showing that a ride is closed"""
        # Skip - requires complex display mocking
        pass

    @pytest.mark.asyncio
    async def test_show_ride_wait_time(self):
        """Test showing a ride's wait time"""
        # Skip - requires complex display mocking
        pass

    @pytest.mark.asyncio
    async def test_show_configuration_message(self):
        """Test showing a configuration message"""
        # Skip - requires complex display mocking
        pass

class TestSimpleScrollingDisplay:
    def test_initialization(self):
        """Test initializing the SimpleScrollingDisplay"""
        # Create mock MatrixPortal and settings manager
        mock_mp = MagicMock()
        mock_mp.graphics.display.height = 32
        mock_settings_manager = MagicMock()
        
        # Create the display
        display = SimpleScrollingDisplay(mock_mp, mock_settings_manager)
        
        # Verify MatrixPortal and settings are stored
        assert display.matrix_portal == mock_mp
        assert display.settings_manager == mock_settings_manager
        assert display.scroll_delay == 0.03  # Default
        
        # Verify text areas were added
        assert display.WAIT_TIME == 0
        assert display.RIDE_NAME == 1
        
        # Verify add_text was called twice
        assert mock_mp.add_text.call_count == 2
    
    def test_show_scroll_message(self):
        """Test showing a scrolling message"""
        # Create mock MatrixPortal and settings manager
        mock_mp = MagicMock()
        mock_settings_manager = MagicMock()
        
        # Create the display
        display = SimpleScrollingDisplay(mock_mp, mock_settings_manager)
        
        # Mock logger
        with patch('src.ui.display_impl.logger') as mock_logger:
            # Call show_scroll_message
            display.show_scroll_message("Test message")
            
            # Verify log message
            mock_logger.debug.assert_called_once_with("Scrolling messageTest message")
            
            # Verify text was set
            mock_mp.set_text.assert_any_call("", display.WAIT_TIME)
            mock_mp.set_text.assert_any_call("Test message", display.RIDE_NAME)
            
            # Verify scroll_text was called
            mock_mp.scroll_text.assert_called_once_with(display.scroll_delay)