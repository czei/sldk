"""Unit tests for OTAUpdater"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.ota.ota_updater import OTAUpdater
from src.network.http_client import HttpClient


class TestOTAUpdater:
    """Test cases for OTAUpdater"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client"""
        return Mock()
    
    @pytest.fixture
    def ota_updater(self, mock_http_client):
        """Create an OTAUpdater instance with mocked dependencies"""
        updater = OTAUpdater(
            http_client_param=mock_http_client,
            github_repo='test/repo',
            main_dir='src',
            headers={'Authorization': 'token test_token'}
        )
        return updater
    
    def test_check_for_new_version_returns_tuple(self, ota_updater):
        """Test that check_for_new_version returns a tuple of (current_version, latest_version)"""
        # Mock get_version to return current version
        with patch.object(ota_updater, 'get_version', return_value='1.0'):
            # Mock get_latest_version to return latest version
            with patch.object(ota_updater, 'get_latest_version', return_value='2.0'):
                result = ota_updater.check_for_new_version()
                
                # Should return a tuple
                assert isinstance(result, tuple)
                assert len(result) == 2
                assert result == ('1.0', '2.0')
    
    def test_check_for_new_version_same_version(self, ota_updater):
        """Test when current and latest versions are the same"""
        with patch.object(ota_updater, 'get_version', return_value='1.5'):
            with patch.object(ota_updater, 'get_latest_version', return_value='1.5'):
                result = ota_updater.check_for_new_version()
                
                assert result == ('1.5', '1.5')
    
    def test_check_for_new_version_older_latest(self, ota_updater):
        """Test when latest version is older than current (edge case)"""
        with patch.object(ota_updater, 'get_version', return_value='2.0'):
            with patch.object(ota_updater, 'get_latest_version', return_value='1.0'):
                result = ota_updater.check_for_new_version()
                
                assert result == ('2.0', '1.0')
    
    def test_get_version_with_version_file(self, ota_updater):
        """Test get_version when version file exists"""
        with patch('os.listdir', return_value=['.version', 'other_file.py']):
            mock_open = MagicMock()
            mock_open.__enter__.return_value.read.return_value = '1.2.3'
            
            with patch('builtins.open', return_value=mock_open):
                version = ota_updater.get_version('/test/dir')
                
                assert version == '1.2.3'
    
    def test_get_version_no_version_file(self, ota_updater):
        """Test get_version when version file doesn't exist"""
        with patch('os.listdir', return_value=['other_file.py']):
            version = ota_updater.get_version('/test/dir')
            
            # Should return default version
            assert version == '0.0'
    
    def test_get_version_directory_not_found(self, ota_updater):
        """Test get_version when directory doesn't exist"""
        with patch('os.listdir', side_effect=FileNotFoundError()):
            version = ota_updater.get_version('/nonexistent/dir')
            
            # Should return default version
            assert version == '0.0'
    
    def test_get_latest_version_stable_release(self, ota_updater, mock_http_client):
        """Test get_latest_version for stable releases"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'tag_name': 'v1.5.0',
            'prerelease': False
        }
        mock_http_client.get_sync.return_value = mock_response
        
        # use_prerelease is False by default
        version = ota_updater.get_latest_version()
        
        assert version == 'v1.5.0'
        mock_http_client.get_sync.assert_called_once()
    
    def test_get_latest_version_with_prerelease(self, ota_updater, mock_http_client):
        """Test get_latest_version when including prereleases"""
        # Set to use prereleases
        ota_updater.use_prerelease = True
        
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'tag_name': 'v2.0.0-beta',
                'prerelease': True
            },
            {
                'tag_name': 'v1.5.0',
                'prerelease': False
            }
        ]
        mock_http_client.get_sync.return_value = mock_response
        
        version = ota_updater.get_latest_version()
        
        assert version == 'v2.0.0-beta'
        mock_http_client.get_sync.assert_called_once()
    
    def test_update_available_at_boot_with_new_version_dir(self, ota_updater):
        """Test update_available_at_boot when new version directory exists"""
        # Mock the listing of the module directory and the next directory
        with patch('os.listdir') as mock_listdir:
            def listdir_side_effect(path):
                if path == '.' or path == '':
                    return ['next', 'src', 'other_dir']
                elif path.endswith('next'):
                    return ['.version', 'some_file.py']
                else:
                    return []
            
            mock_listdir.side_effect = listdir_side_effect
            assert ota_updater.update_available_at_boot() is True
    
    def test_update_available_at_boot_without_new_version_dir(self, ota_updater):
        """Test update_available_at_boot when new version directory doesn't exist"""
        with patch('os.listdir', return_value=['src', 'other_dir']):
            assert ota_updater.update_available_at_boot() is False
    
    def test_update_available_at_boot_empty_module_path(self, ota_updater):
        """Test update_available_at_boot with empty module path"""
        ota_updater.module = ''
        with patch('os.listdir') as mock_listdir:
            def listdir_side_effect(path):
                if path == '.' or path == '':
                    return ['next', 'src']
                elif path == 'next' or path.endswith('next'):
                    return ['.version', 'some_file.py']
                else:
                    return []
            
            mock_listdir.side_effect = listdir_side_effect
            assert ota_updater.update_available_at_boot() is True
    
    def test_update_available_at_boot_directory_error(self, ota_updater):
        """Test update_available_at_boot when directory listing fails"""
        with patch('os.listdir', side_effect=FileNotFoundError()):
            assert ota_updater.update_available_at_boot() is False
    
    def test_real_api_get_latest_version(self):
        """Test get_latest_version with real API call"""
        # Create a real HTTP client
        http_client = HttpClient()
        
        # Create OTAUpdater with real GitHub repo
        updater = OTAUpdater(
            http_client_param=http_client,
            github_repo='https://github.com/Czeiszperger/themeparkwaits.release',
            main_dir='src',
            headers={'Authorization': 'token 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'}
        )
        
        # Test getting latest version
        try:
            latest_version = updater.get_latest_version()
            # Should return a version string
            assert isinstance(latest_version, str)
            assert len(latest_version) > 0
            # Version should be something like "1.9" or "v1.9.0"
            assert latest_version[0].isdigit() or latest_version[0] == 'v'
        except Exception as e:
            pytest.fail(f"Real API call failed: {e}")