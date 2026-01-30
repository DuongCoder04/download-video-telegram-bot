#!/usr/bin/env python3
"""
Unit Tests for Video Downloader Module

Tests cho các hàm trong downloader.py

Requirements: 3.1, 3.3, 3.5
"""

import os
import tempfile
import uuid
from unittest.mock import MagicMock, patch

import pytest

from downloader import (
    get_yt_dlp_options,
    download_video,
    _handle_progress,
)
from models import DownloadResult


class TestGetYtDlpOptions:
    """Tests for get_yt_dlp_options function."""
    
    def test_returns_dict(self):
        """Should return a dictionary."""
        result = get_yt_dlp_options("/tmp/test.mp4")
        assert isinstance(result, dict)
    
    def test_contains_format_option(self):
        """Should contain format option for size limit."""
        max_size = 50 * 1024 * 1024
        result = get_yt_dlp_options("/tmp/test.mp4", max_size)
        assert 'format' in result
        assert str(max_size) in result['format']
    
    def test_contains_output_template(self):
        """Should contain output template with provided path."""
        output_path = "/tmp/my_video.mp4"
        result = get_yt_dlp_options(output_path)
        assert result['outtmpl'] == output_path
    
    def test_quiet_mode_enabled(self):
        """Should have quiet mode enabled."""
        result = get_yt_dlp_options("/tmp/test.mp4")
        assert result.get('quiet') is True
    
    def test_no_progress_hooks_without_callback(self):
        """Should not have progress_hooks when no callback provided."""
        result = get_yt_dlp_options("/tmp/test.mp4", progress_callback=None)
        assert 'progress_hooks' not in result
    
    def test_has_progress_hooks_with_callback(self):
        """Should have progress_hooks when callback is provided."""
        callback = MagicMock()
        result = get_yt_dlp_options("/tmp/test.mp4", progress_callback=callback)
        assert 'progress_hooks' in result
        assert len(result['progress_hooks']) == 1
    
    def test_custom_max_size(self):
        """Should use custom max_size in format string."""
        custom_size = 100 * 1024 * 1024  # 100MB
        result = get_yt_dlp_options("/tmp/test.mp4", max_size=custom_size)
        assert str(custom_size) in result['format']


class TestHandleProgress:
    """Tests for _handle_progress function."""
    
    def test_no_callback_does_nothing(self):
        """Should do nothing when callback is None."""
        # Should not raise any exception
        _handle_progress({'status': 'downloading'}, None)
    
    def test_downloading_with_total_bytes(self):
        """Should calculate percentage from downloaded and total bytes."""
        callback = MagicMock()
        progress_dict = {
            'status': 'downloading',
            'downloaded_bytes': 50,
            'total_bytes': 100
        }
        _handle_progress(progress_dict, callback)
        callback.assert_called_once()
        # Should be 50%
        assert callback.call_args[0][0] == 50.0
    
    def test_downloading_with_total_bytes_estimate(self):
        """Should use total_bytes_estimate when total_bytes is not available."""
        callback = MagicMock()
        progress_dict = {
            'status': 'downloading',
            'downloaded_bytes': 25,
            'total_bytes': None,
            'total_bytes_estimate': 100
        }
        _handle_progress(progress_dict, callback)
        callback.assert_called_once()
        assert callback.call_args[0][0] == 25.0
    
    def test_downloading_caps_at_99_percent(self):
        """Should cap percentage at 99% during downloading."""
        callback = MagicMock()
        progress_dict = {
            'status': 'downloading',
            'downloaded_bytes': 100,
            'total_bytes': 100
        }
        _handle_progress(progress_dict, callback)
        callback.assert_called_once()
        assert callback.call_args[0][0] == 99.0
    
    def test_finished_status_calls_100_percent(self):
        """Should call callback with 100% when status is finished."""
        callback = MagicMock()
        progress_dict = {'status': 'finished'}
        _handle_progress(progress_dict, callback)
        callback.assert_called_once_with(100.0)
    
    def test_downloading_with_fragments(self):
        """Should calculate percentage from fragment info when bytes not available."""
        callback = MagicMock()
        progress_dict = {
            'status': 'downloading',
            'downloaded_bytes': 0,
            'total_bytes': None,
            'total_bytes_estimate': None,
            'fragment_index': 5,
            'fragment_count': 10
        }
        _handle_progress(progress_dict, callback)
        callback.assert_called_once()
        assert callback.call_args[0][0] == 50.0
    
    def test_unknown_status_does_not_call_callback(self):
        """Should not call callback for unknown status."""
        callback = MagicMock()
        progress_dict = {'status': 'unknown'}
        _handle_progress(progress_dict, callback)
        callback.assert_not_called()


class TestDownloadVideo:
    """Tests for download_video function."""
    
    def test_returns_download_result(self):
        """Should return a DownloadResult instance."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            result = download_video("https://example.com/video")
            assert isinstance(result, DownloadResult)
    
    def test_generates_unique_filename_with_uuid(self):
        """Should generate unique filename using UUID."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            # Call download_video twice and check that different UUIDs are used
            with patch('downloader.uuid.uuid4') as mock_uuid:
                mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
                download_video("https://example.com/video", output_dir="/tmp")
                
                # Verify the output path contains the UUID
                call_args = mock_ydl.call_args
                opts = call_args[0][0]
                assert '12345678-1234-5678-1234-567812345678' in opts['outtmpl']
    
    def test_uses_provided_output_dir(self):
        """Should use the provided output directory."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            custom_dir = "/custom/output"
            download_video("https://example.com/video", output_dir=custom_dir)
            
            call_args = mock_ydl.call_args
            opts = call_args[0][0]
            assert opts['outtmpl'].startswith(custom_dir)
    
    def test_uses_provided_max_size(self):
        """Should use the provided max_size in format string."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            custom_size = 100 * 1024 * 1024
            download_video("https://example.com/video", max_size=custom_size)
            
            call_args = mock_ydl.call_args
            opts = call_args[0][0]
            assert str(custom_size) in opts['format']
    
    def test_success_when_file_exists(self):
        """Should return success when file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.mp4")
            
            with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
                mock_instance = MagicMock()
                mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
                mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
                
                # Create the file to simulate successful download
                def create_file(urls):
                    # Get the output path from the options
                    opts = mock_ydl.call_args[0][0]
                    with open(opts['outtmpl'], 'w') as f:
                        f.write("test content")
                
                mock_instance.download.side_effect = create_file
                
                result = download_video("https://example.com/video", output_dir=tmpdir)
                
                assert result.success is True
                assert result.file_path is not None
                assert result.error_message is None
                assert result.file_size > 0
    
    def test_failure_on_download_error(self):
        """Should return failure when yt-dlp raises DownloadError."""
        import yt_dlp
        
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            mock_instance.download.side_effect = yt_dlp.utils.DownloadError("Video not found")
            
            result = download_video("https://example.com/video")
            
            assert result.success is False
            assert result.file_path is None
            assert result.error_message is not None
            assert result.file_size == 0
    
    def test_failure_on_generic_exception(self):
        """Should return failure when generic exception is raised."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            mock_instance.download.side_effect = Exception("Unknown error")
            
            result = download_video("https://example.com/video")
            
            assert result.success is False
            assert result.file_path is None
            assert "Unknown error" in result.error_message
            assert result.file_size == 0
    
    def test_progress_callback_is_passed(self):
        """Should pass progress_callback to yt-dlp options."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            callback = MagicMock()
            download_video("https://example.com/video", progress_callback=callback)
            
            call_args = mock_ydl.call_args
            opts = call_args[0][0]
            assert 'progress_hooks' in opts


class TestUniqueFilenameGeneration:
    """Tests to verify unique filename generation (Property 3 related)."""
    
    def test_multiple_downloads_generate_different_paths(self):
        """Multiple download calls should generate different file paths."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            paths = []
            for _ in range(10):
                download_video("https://example.com/video", output_dir="/tmp")
                call_args = mock_ydl.call_args
                opts = call_args[0][0]
                paths.append(opts['outtmpl'])
            
            # All paths should be unique
            assert len(paths) == len(set(paths))
    
    def test_filename_contains_uuid_format(self):
        """Generated filename should contain valid UUID format."""
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            download_video("https://example.com/video", output_dir="/tmp")
            
            call_args = mock_ydl.call_args
            opts = call_args[0][0]
            filename = os.path.basename(opts['outtmpl'])
            
            # Remove .mp4 extension and try to parse as UUID
            uuid_str = filename.replace('.mp4', '')
            # Should not raise exception
            parsed_uuid = uuid.UUID(uuid_str)
            assert parsed_uuid is not None
