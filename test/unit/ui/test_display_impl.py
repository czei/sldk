"""
Tests for the display implementation module.
"""
import time
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.ui.display_impl import AsyncScrollingDisplay, SimpleScrollingDisplay
from src.utils.color_utils import ColorUtils

class TestAsyncScrollingDisplay:
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    def test_initialization(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test initializing the AsyncScrollingDisplay"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_hardware.width = 64
        mock_hardware.height = 32
        
        mock_settings_manager = MagicMock()
        mock_settings_manager.settings = {
            "brightness_scale": "0.5",
            "default_color": "0xffff00",  # Yellow
        }
        
        # Mock font loading
        mock_bitmap_font.load_font.return_value = MagicMock()
        
        # Create mock displayio Group and Label classes
        mock_group = MagicMock()
        mock_label = MagicMock()
        mock_displayio.Group.return_value = mock_group
        
        # Create the display
        display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
        
        # Verify hardware and settings are stored
        assert display.hardware == mock_hardware
        assert display.settings_manager == mock_settings_manager
        
        # Verify that main group was set as root_group
        assert mock_hardware.root_group == display.main_group
        
        # Verify all the labels were created
        assert hasattr(display, 'scrolling_label')
        assert hasattr(display, 'wait_time_name')
        assert hasattr(display, 'wait_time')
        assert hasattr(display, 'closed')
        assert hasattr(display, 'splash_line1')
        assert hasattr(display, 'splash_line2')
        
        # Verify font loading was called for custom fonts
        mock_bitmap_font.load_font.assert_any_call("src/fonts/tom-thumb.bdf")
    
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    def test_set_colors(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test setting colors from settings"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_settings_manager = MagicMock()
        mock_settings_manager.settings = {
            "brightness_scale": "0.5",
            "default_color": "0xffff00",  # Yellow
            "ride_name_color": "0x0000aa",  # Blue
            "ride_wait_time_color": "0xfdf5e6",  # Old Lace
        }
        
        # Create the display
        with patch('src.ui.display_impl.logger') as mock_logger:
            display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
            
            # Reset mock attributes to clear initialization calls
            mock_logger.reset_mock()
            
            # Call set_colors with updated settings
            mock_settings = MagicMock()
            mock_settings.settings = {
                "brightness_scale": "0.75",
                "default_color": "0xff0000",  # Red
                "ride_name_color": "0x00ff00",  # Green
                "ride_wait_time_color": "0x0000ff",  # Blue
            }
            
            display.set_colors(mock_settings)
            
            # Verify log message
            mock_logger.info.assert_called_once_with("New brightness scale is0.75")
            
            # Verify color attributes were set on all labels
            # Here we would need to check each label's color property, but since 
            # we're using mocks, we can't directly check the values, just that they were set
    
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    def test_off(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test turning off all display elements"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_settings_manager = MagicMock()
        mock_settings_manager.settings = {
            "brightness_scale": "0.5",
            "default_color": "0xffff00",
        }
        
        # Create the display
        display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
        
        # Reset the hidden state of all groups
        display.scrolling_group.hidden = False
        display.wait_time_name_group.hidden = False
        display.wait_time_group.hidden = False
        display.closed_group.hidden = False
        display.splash_group.hidden = False
        display.update_group.hidden = False
        display.required_group.hidden = False
        display.centered_group.hidden = False
        
        # Call off()
        display.off()
        
        # Verify all groups are hidden
        assert display.scrolling_group.hidden is True
        assert display.wait_time_name_group.hidden is True
        assert display.wait_time_group.hidden is True
        assert display.closed_group.hidden is True
        assert display.splash_group.hidden is True
        assert display.update_group.hidden is True
        assert display.required_group.hidden is True
        assert display.centered_group.hidden is True
    
    @pytest.mark.asyncio
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    async def test_show_splash(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test showing the splash screen"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_settings_manager = MagicMock()
        mock_settings_manager.settings = {
            "brightness_scale": "0.5",
            "default_color": "0xffff00",
        }
        
        # Create the display
        display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
        
        # Mock off() method
        display.off = MagicMock()
        
        # Mock asyncio.sleep
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            with patch('src.ui.display_impl.logger') as mock_logger:
                # Call show_splash with default duration
                await display.show_splash()
                
                # Verify off() was called
                display.off.assert_called_once()
                
                # Verify logger call
                mock_logger.debug.assert_called_once_with("Showing the splash screen for 4 seconds")
                
                # Verify splash group was shown
                assert display.splash_group.hidden is False
                
                # Verify sleep was called
                mock_sleep.assert_called_once_with(4)
                
                # Verify splash group is hidden again
                assert display.splash_group.hidden is True
    
    @pytest.mark.asyncio
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    async def test_show_ride_closed(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test showing that a ride is closed"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_settings_manager = MagicMock()
        
        # Create the display
        display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
        
        # Mock parent method
        with patch('src.ui.display_base.Display.show_ride_closed', new_callable=AsyncMock) as mock_parent:
            # Call show_ride_closed
            await display.show_ride_closed("dummy")
            
            # Verify parent method was called
            mock_parent.assert_called_once_with("dummy")
            
            # Verify closed group is shown
            assert display.closed_group.hidden is False
    
    @pytest.mark.asyncio
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    async def test_show_ride_wait_time(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test showing a ride's wait time"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_settings_manager = MagicMock()
        
        # Create the display
        display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
        
        # Mock parent method and center_time
        with patch('src.ui.display_base.Display.show_ride_wait_time', new_callable=AsyncMock) as mock_parent:
            display.center_time = MagicMock()
            
            # Call show_ride_wait_time
            await display.show_ride_wait_time("15")
            
            # Verify parent method was called
            mock_parent.assert_called_once_with("15")
            
            # Verify text was set
            assert display.wait_time.text == "15"
            
            # Verify center_time was called
            display.center_time.assert_called_once_with(display.wait_time)
            
            # Verify wait time group is shown
            assert display.wait_time_group.hidden is False
    
    @pytest.mark.asyncio
    @patch('src.ui.display_impl.displayio')
    @patch('src.ui.display_impl.terminalio')
    @patch('src.ui.display_impl.bitmap_font')
    async def test_show_configuration_message(self, mock_bitmap_font, mock_terminalio, mock_displayio):
        """Test showing a configuration message"""
        # Create mock hardware and settings manager
        mock_hardware = MagicMock()
        mock_settings_manager = MagicMock()
        
        # Create the display
        display = AsyncScrollingDisplay(mock_hardware, mock_settings_manager)
        
        # Mock off() and parent method
        display.off = MagicMock()
        with patch('src.ui.display_base.Display.show_configuration_message', new_callable=AsyncMock) as mock_parent:
            # Call show_configuration_message
            await display.show_configuration_message()
            
            # Verify off() was called
            display.off.assert_called_once()
            
            # Verify parent method was called
            mock_parent.assert_called_once()

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