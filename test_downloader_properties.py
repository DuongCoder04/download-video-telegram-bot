#!/usr/bin/env python3
"""
Property-Based Tests for Video Downloader Module

Property tests sử dụng Hypothesis để kiểm tra Unique Filename Generation.

**Validates: Requirements 3.3, 7.3**

Property 3: Unique Filename Generation
*For any* hai lần gọi download với cùng URL, các file path được tạo ra phải khác nhau (không trùng lặp).
"""

import os
import uuid
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, strategies as st, settings, assume

from downloader import download_video
from models import DownloadResult


# =============================================================================
# Custom Strategies for URL and Directory Generation
# =============================================================================

# Strategy for generating valid video IDs (alphanumeric with dashes)
video_id_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
    min_size=1,
    max_size=20
)

# Strategy for optional protocol
protocol_strategy = st.sampled_from(["https://", "http://"])

# Strategy for optional www prefix
www_strategy = st.sampled_from(["www.", ""])


@st.composite
def youtube_url_strategy(draw):
    """Generate valid YouTube URLs for testing."""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    video_id = draw(video_id_strategy)
    assume(len(video_id) > 0)
    return f"{protocol}{www}youtube.com/watch?v={video_id}"


@st.composite
def facebook_url_strategy(draw):
    """Generate valid Facebook URLs for testing."""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    username = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=1,
        max_size=15
    ))
    video_id = draw(st.integers(min_value=1, max_value=10**15))
    assume(len(username) > 0)
    return f"{protocol}{www}facebook.com/{username}/videos/{video_id}"


@st.composite
def instagram_url_strategy(draw):
    """Generate valid Instagram URLs for testing."""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    post_type = draw(st.sampled_from(["p", "reel"]))
    post_id = draw(video_id_strategy)
    assume(len(post_id) > 0)
    return f"{protocol}{www}instagram.com/{post_type}/{post_id}"


# Combined strategy for any supported platform URL
any_video_url_strategy = st.one_of(
    youtube_url_strategy(),
    facebook_url_strategy(),
    instagram_url_strategy()
)


# Strategy for output directories
output_dir_strategy = st.sampled_from([
    "/tmp",
    "/tmp/videos",
    "/var/tmp",
    "/home/user/downloads",
    "/data/videos"
])


# Strategy for number of download calls (at least 2 to test uniqueness)
num_calls_strategy = st.integers(min_value=2, max_value=20)


# =============================================================================
# Property Tests - Property 3: Unique Filename Generation
# **Validates: Requirements 3.3, 7.3**
# =============================================================================

class TestUniqueFilenameGenerationProperty:
    """
    Property 3: Unique Filename Generation
    
    *For any* hai lần gọi download với cùng URL, các file path được tạo ra 
    phải khác nhau (không trùng lặp).
    
    **Validates: Requirements 3.3, 7.3**
    """
    
    @given(url=any_video_url_strategy, num_calls=num_calls_strategy)
    @settings(max_examples=100)
    def test_multiple_downloads_same_url_generate_unique_paths(
        self, url: str, num_calls: int
    ):
        """
        Property: Multiple download calls with the same URL should generate unique file paths.
        
        **Validates: Requirements 3.3, 7.3**
        
        For any URL and any number of download calls (>= 2), each call should
        generate a different file path using UUID to ensure uniqueness.
        """
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            # Setup mock to avoid actual downloads
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            generated_paths = []
            
            for _ in range(num_calls):
                download_video(url, output_dir="/tmp")
                
                # Extract the output path from the yt-dlp options
                call_args = mock_ydl.call_args
                opts = call_args[0][0]
                output_path = opts['outtmpl']
                generated_paths.append(output_path)
            
            # All paths should be unique
            unique_paths = set(generated_paths)
            assert len(unique_paths) == len(generated_paths), (
                f"Expected {len(generated_paths)} unique paths, "
                f"but got {len(unique_paths)}. "
                f"Duplicate paths found for URL: {url}"
            )
    
    @given(url=any_video_url_strategy, output_dir=output_dir_strategy)
    @settings(max_examples=100)
    def test_unique_paths_across_different_directories(
        self, url: str, output_dir: str
    ):
        """
        Property: Download calls should generate unique paths regardless of output directory.
        
        **Validates: Requirements 3.3, 7.3**
        
        For any URL and output directory, multiple download calls should
        generate unique file paths within that directory.
        """
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            generated_paths = []
            
            # Call download 5 times with the same URL and directory
            for _ in range(5):
                download_video(url, output_dir=output_dir)
                
                call_args = mock_ydl.call_args
                opts = call_args[0][0]
                output_path = opts['outtmpl']
                generated_paths.append(output_path)
            
            # All paths should be unique
            unique_paths = set(generated_paths)
            assert len(unique_paths) == len(generated_paths), (
                f"Expected 5 unique paths in directory '{output_dir}', "
                f"but got {len(unique_paths)} unique paths"
            )
            
            # All paths should be in the correct directory
            for path in generated_paths:
                assert path.startswith(output_dir), (
                    f"Path '{path}' should start with '{output_dir}'"
                )
    
    @given(url=any_video_url_strategy)
    @settings(max_examples=100)
    def test_generated_filename_contains_valid_uuid(self, url: str):
        """
        Property: Generated filename should contain a valid UUID.
        
        **Validates: Requirements 3.3, 7.3**
        
        For any URL, the generated filename should be a valid UUID followed by .mp4 extension.
        """
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            download_video(url, output_dir="/tmp")
            
            call_args = mock_ydl.call_args
            opts = call_args[0][0]
            output_path = opts['outtmpl']
            
            # Extract filename from path
            filename = os.path.basename(output_path)
            
            # Filename should end with .mp4
            assert filename.endswith('.mp4'), (
                f"Filename '{filename}' should end with .mp4"
            )
            
            # Extract UUID part (remove .mp4 extension)
            uuid_str = filename[:-4]  # Remove '.mp4'
            
            # Should be a valid UUID
            try:
                parsed_uuid = uuid.UUID(uuid_str)
                assert parsed_uuid is not None
            except ValueError:
                pytest.fail(
                    f"Filename '{filename}' does not contain a valid UUID. "
                    f"UUID part: '{uuid_str}'"
                )


class TestUniqueFilenameAcrossURLs:
    """
    Additional property tests for filename uniqueness across different URLs.
    
    **Validates: Requirements 3.3, 7.3**
    """
    
    @given(
        url1=youtube_url_strategy(),
        url2=facebook_url_strategy(),
        url3=instagram_url_strategy()
    )
    @settings(max_examples=50)
    def test_different_urls_generate_different_paths(
        self, url1: str, url2: str, url3: str
    ):
        """
        Property: Different URLs should also generate unique file paths.
        
        **Validates: Requirements 3.3, 7.3**
        
        Even when downloading from different URLs, each download should
        generate a unique file path.
        """
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            generated_paths = []
            
            for url in [url1, url2, url3]:
                download_video(url, output_dir="/tmp")
                
                call_args = mock_ydl.call_args
                opts = call_args[0][0]
                output_path = opts['outtmpl']
                generated_paths.append(output_path)
            
            # All paths should be unique
            unique_paths = set(generated_paths)
            assert len(unique_paths) == len(generated_paths), (
                f"Expected 3 unique paths for different URLs, "
                f"but got {len(unique_paths)} unique paths"
            )
    
    @given(url=any_video_url_strategy)
    @settings(max_examples=50)
    def test_uuid_uniqueness_is_statistically_guaranteed(self, url: str):
        """
        Property: UUID generation should provide statistical uniqueness guarantee.
        
        **Validates: Requirements 3.3, 7.3**
        
        Generate a larger number of paths and verify all are unique,
        demonstrating the statistical guarantee of UUID uniqueness.
        """
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            generated_uuids = []
            num_iterations = 50
            
            for _ in range(num_iterations):
                download_video(url, output_dir="/tmp")
                
                call_args = mock_ydl.call_args
                opts = call_args[0][0]
                output_path = opts['outtmpl']
                
                # Extract UUID from filename
                filename = os.path.basename(output_path)
                uuid_str = filename[:-4]  # Remove '.mp4'
                generated_uuids.append(uuid_str)
            
            # All UUIDs should be unique
            unique_uuids = set(generated_uuids)
            assert len(unique_uuids) == num_iterations, (
                f"Expected {num_iterations} unique UUIDs, "
                f"but got {len(unique_uuids)} unique UUIDs"
            )


class TestFilenameFormatConsistency:
    """
    Property tests for filename format consistency.
    
    **Validates: Requirements 3.3, 7.3**
    """
    
    @given(url=any_video_url_strategy, output_dir=output_dir_strategy)
    @settings(max_examples=50)
    def test_filename_format_is_consistent(self, url: str, output_dir: str):
        """
        Property: Filename format should be consistent: {uuid}.mp4
        
        **Validates: Requirements 3.3, 7.3**
        
        For any URL and output directory, the generated filename should
        follow the format: {uuid}.mp4 where uuid is a valid UUID4.
        """
        with patch('downloader.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
            
            download_video(url, output_dir=output_dir)
            
            call_args = mock_ydl.call_args
            opts = call_args[0][0]
            output_path = opts['outtmpl']
            
            # Path should be: output_dir/uuid.mp4
            expected_dir = os.path.dirname(output_path)
            filename = os.path.basename(output_path)
            
            # Directory should match
            assert expected_dir == output_dir, (
                f"Expected directory '{output_dir}', got '{expected_dir}'"
            )
            
            # Filename should be uuid.mp4 format
            assert filename.endswith('.mp4'), (
                f"Filename should end with .mp4"
            )
            
            # UUID part should be exactly 36 characters (standard UUID format)
            uuid_part = filename[:-4]
            assert len(uuid_part) == 36, (
                f"UUID part should be 36 characters, got {len(uuid_part)}"
            )
            
            # UUID should have correct format with dashes
            parts = uuid_part.split('-')
            assert len(parts) == 5, (
                f"UUID should have 5 parts separated by dashes"
            )
            assert [len(p) for p in parts] == [8, 4, 4, 4, 12], (
                f"UUID parts should have lengths [8, 4, 4, 4, 12]"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
