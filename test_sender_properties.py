#!/usr/bin/env python3
"""
Property-Based Tests for Video Sender Module

Property tests sử dụng Hypothesis để kiểm tra File Size Validation.

**Validates: Requirements 4.2**

Property 4: File Size Validation
*For any* file_size và max_size, hàm kiểm tra kích thước phải trả về `True` khi 
`file_size <= max_size` và `False` khi `file_size > max_size`.
"""

import os
import tempfile
import pytest
from hypothesis import given, strategies as st, settings, assume

from sender import is_file_size_valid, get_file_size, DEFAULT_MAX_FILE_SIZE


# =============================================================================
# Custom Strategies for File Size Generation
# =============================================================================

# Strategy for file sizes (0 to 100MB in bytes)
file_size_strategy = st.integers(min_value=0, max_value=100 * 1024 * 1024)

# Strategy for max sizes (1 byte to 100MB)
max_size_strategy = st.integers(min_value=1, max_value=100 * 1024 * 1024)

# Strategy for small file sizes (for faster test execution)
small_file_size_strategy = st.integers(min_value=0, max_value=10 * 1024)  # 0 to 10KB

# Strategy for small max sizes
small_max_size_strategy = st.integers(min_value=1, max_value=10 * 1024)  # 1 byte to 10KB


# =============================================================================
# Property Tests - Property 4: File Size Validation
# **Validates: Requirements 4.2**
# =============================================================================

class TestFileSizeValidationProperty:
    """
    Property 4: File Size Validation
    
    *For any* file_size và max_size, hàm kiểm tra kích thước phải trả về `True` 
    khi `file_size <= max_size` và `False` khi `file_size > max_size`.
    
    **Validates: Requirements 4.2**
    """
    
    @given(file_size=small_file_size_strategy, max_size=small_max_size_strategy)
    @settings(max_examples=100)
    def test_file_size_validation_returns_true_when_size_within_limit(
        self, file_size: int, max_size: int
    ):
        """
        Property: is_file_size_valid returns True when file_size <= max_size
        
        **Validates: Requirements 4.2**
        
        For any file_size and max_size where file_size <= max_size,
        is_file_size_valid should return True.
        """
        # Only test cases where file_size <= max_size
        assume(file_size <= max_size)
        
        # Create a temporary file with the specified size
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * file_size)
            tmp_path = tmp_file.name
        
        try:
            result = is_file_size_valid(tmp_path, max_size)
            
            assert result is True, (
                f"Expected True for file_size={file_size} <= max_size={max_size}, "
                f"but got {result}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    @given(file_size=small_file_size_strategy, max_size=small_max_size_strategy)
    @settings(max_examples=100)
    def test_file_size_validation_returns_false_when_size_exceeds_limit(
        self, file_size: int, max_size: int
    ):
        """
        Property: is_file_size_valid returns False when file_size > max_size
        
        **Validates: Requirements 4.2**
        
        For any file_size and max_size where file_size > max_size,
        is_file_size_valid should return False.
        """
        # Only test cases where file_size > max_size
        assume(file_size > max_size)
        
        # Create a temporary file with the specified size
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * file_size)
            tmp_path = tmp_file.name
        
        try:
            result = is_file_size_valid(tmp_path, max_size)
            
            assert result is False, (
                f"Expected False for file_size={file_size} > max_size={max_size}, "
                f"but got {result}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    @given(file_size=small_file_size_strategy, max_size=small_max_size_strategy)
    @settings(max_examples=100)
    def test_file_size_validation_boundary_condition(
        self, file_size: int, max_size: int
    ):
        """
        Property: is_file_size_valid correctly handles boundary condition (file_size == max_size)
        
        **Validates: Requirements 4.2**
        
        When file_size equals max_size exactly, is_file_size_valid should return True.
        """
        # Test the exact boundary: file_size == max_size
        boundary_size = max_size
        
        # Create a temporary file with size exactly equal to max_size
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * boundary_size)
            tmp_path = tmp_file.name
        
        try:
            result = is_file_size_valid(tmp_path, max_size)
            
            assert result is True, (
                f"Expected True for file_size={boundary_size} == max_size={max_size}, "
                f"but got {result}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestFileSizeValidationConsistency:
    """
    Additional property tests for file size validation consistency.
    
    **Validates: Requirements 4.2**
    """
    
    @given(file_size=small_file_size_strategy)
    @settings(max_examples=50)
    def test_file_size_validation_is_idempotent(self, file_size: int):
        """
        Property: Calling is_file_size_valid multiple times gives same result
        
        **Validates: Requirements 4.2**
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * file_size)
            tmp_path = tmp_file.name
        
        try:
            result1 = is_file_size_valid(tmp_path, DEFAULT_MAX_FILE_SIZE)
            result2 = is_file_size_valid(tmp_path, DEFAULT_MAX_FILE_SIZE)
            
            assert result1 == result2, (
                f"is_file_size_valid should be idempotent: {result1} != {result2}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    @given(
        file_size=small_file_size_strategy,
        max_size1=small_max_size_strategy,
        max_size2=small_max_size_strategy
    )
    @settings(max_examples=50)
    def test_file_size_validation_monotonicity(
        self, file_size: int, max_size1: int, max_size2: int
    ):
        """
        Property: If valid for max_size1, then valid for any max_size2 >= max_size1
        
        **Validates: Requirements 4.2**
        
        If a file is valid for a certain max_size, it should also be valid
        for any larger max_size (monotonicity property).
        """
        # Ensure max_size2 >= max_size1
        assume(max_size2 >= max_size1)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * file_size)
            tmp_path = tmp_file.name
        
        try:
            result1 = is_file_size_valid(tmp_path, max_size1)
            result2 = is_file_size_valid(tmp_path, max_size2)
            
            # If valid for smaller max_size, must be valid for larger max_size
            if result1:
                assert result2 is True, (
                    f"If valid for max_size={max_size1}, "
                    f"should be valid for max_size={max_size2} >= {max_size1}"
                )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestFileSizeValidationEdgeCases:
    """
    Property tests for edge cases in file size validation.
    
    **Validates: Requirements 4.2**
    """
    
    @given(max_size=small_max_size_strategy)
    @settings(max_examples=50)
    def test_empty_file_is_always_valid(self, max_size: int):
        """
        Property: An empty file (0 bytes) should always be valid for any max_size > 0
        
        **Validates: Requirements 4.2**
        """
        # Create an empty temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
            # Don't write anything - file is empty (0 bytes)
        
        try:
            result = is_file_size_valid(tmp_path, max_size)
            
            assert result is True, (
                f"Empty file (0 bytes) should be valid for max_size={max_size}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_nonexistent_file_returns_false(self):
        """
        Property: A non-existent file should return False
        
        **Validates: Requirements 4.2**
        """
        nonexistent_path = "/tmp/nonexistent_file_12345.mp4"
        
        # Ensure file doesn't exist
        if os.path.exists(nonexistent_path):
            os.remove(nonexistent_path)
        
        result = is_file_size_valid(nonexistent_path, DEFAULT_MAX_FILE_SIZE)
        
        assert result is False, (
            "Non-existent file should return False"
        )
    
    @given(file_size=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50)
    def test_file_one_byte_over_limit_returns_false(self, file_size: int):
        """
        Property: A file exactly one byte over the limit should return False
        
        **Validates: Requirements 4.2**
        """
        max_size = file_size - 1  # max_size is one byte less than file_size
        assume(max_size > 0)  # Ensure max_size is positive
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * file_size)
            tmp_path = tmp_file.name
        
        try:
            result = is_file_size_valid(tmp_path, max_size)
            
            assert result is False, (
                f"File with size={file_size} should be invalid for max_size={max_size}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestGetFileSizeFunction:
    """
    Property tests for the get_file_size helper function.
    
    **Validates: Requirements 4.2**
    """
    
    @given(file_size=small_file_size_strategy)
    @settings(max_examples=50)
    def test_get_file_size_returns_correct_size(self, file_size: int):
        """
        Property: get_file_size returns the exact size of the file
        
        **Validates: Requirements 4.2**
        """
        # Create a temporary file with the specified size
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b'\x00' * file_size)
            tmp_path = tmp_file.name
        
        try:
            result = get_file_size(tmp_path)
            
            assert result == file_size, (
                f"Expected file size {file_size}, but got {result}"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_get_file_size_nonexistent_file_returns_negative(self):
        """
        Property: get_file_size returns -1 for non-existent files
        
        **Validates: Requirements 4.2**
        """
        nonexistent_path = "/tmp/nonexistent_file_67890.mp4"
        
        # Ensure file doesn't exist
        if os.path.exists(nonexistent_path):
            os.remove(nonexistent_path)
        
        result = get_file_size(nonexistent_path)
        
        assert result == -1, (
            f"Expected -1 for non-existent file, but got {result}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# =============================================================================
# Property Tests - Property 5: Cleanup Guarantee
# **Validates: Requirements 4.3, 4.4, 7.1**
# =============================================================================

# Import additional modules for cleanup tests
import asyncio
from unittest.mock import AsyncMock, MagicMock

from sender import cleanup_file, send_video


# Strategy for random file content (small sizes for fast tests)
file_content_strategy = st.binary(min_size=0, max_size=1024)  # 0 to 1KB

# Strategy for file names (valid filename characters)
filename_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='_-'),
    min_size=1,
    max_size=20
).map(lambda s: f"test_{s}.mp4")


class TestCleanupGuaranteeProperty:
    """
    Property 5: Cleanup Guarantee
    
    *For any* file path được tạo trong quá trình download, sau khi gọi 
    `cleanup_file(file_path)`, file đó không còn tồn tại trên hệ thống 
    (bất kể quá trình gửi thành công hay thất bại).
    
    **Validates: Requirements 4.3, 4.4, 7.1**
    """
    
    @given(content=file_content_strategy)
    @settings(max_examples=100)
    def test_cleanup_file_removes_existing_file(self, content: bytes):
        """
        Property: cleanup_file always removes an existing file
        
        **Validates: Requirements 4.3, 4.4, 7.1**
        
        For any file that exists on the filesystem, after calling cleanup_file,
        the file should no longer exist.
        """
        # Create a temporary file with random content
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Verify file exists before cleanup
        assert os.path.exists(tmp_path), "File should exist before cleanup"
        
        # Call cleanup_file
        result = cleanup_file(tmp_path)
        
        # Verify file no longer exists
        assert not os.path.exists(tmp_path), (
            f"File should not exist after cleanup_file: {tmp_path}"
        )
        
        # cleanup_file should return True for successful deletion
        assert result is True, "cleanup_file should return True for successful deletion"
    
    @given(filename=filename_strategy)
    @settings(max_examples=50)
    def test_cleanup_file_handles_nonexistent_file(self, filename: str):
        """
        Property: cleanup_file returns True for non-existent files
        
        **Validates: Requirements 4.3, 4.4, 7.1**
        
        For any file path that doesn't exist, cleanup_file should return True
        (considered successful since the goal is to ensure file doesn't exist).
        """
        # Create a path that doesn't exist
        nonexistent_path = os.path.join(tempfile.gettempdir(), filename)
        
        # Ensure file doesn't exist
        if os.path.exists(nonexistent_path):
            os.remove(nonexistent_path)
        
        # Call cleanup_file on non-existent file
        result = cleanup_file(nonexistent_path)
        
        # Should return True (file doesn't exist = goal achieved)
        assert result is True, (
            "cleanup_file should return True for non-existent files"
        )
        
        # File should still not exist
        assert not os.path.exists(nonexistent_path), (
            "File should not exist after cleanup_file"
        )
    
    @given(content=file_content_strategy)
    @settings(max_examples=50)
    def test_cleanup_file_is_idempotent(self, content: bytes):
        """
        Property: Calling cleanup_file multiple times is safe (idempotent)
        
        **Validates: Requirements 4.3, 4.4, 7.1**
        
        Calling cleanup_file multiple times on the same path should not cause errors.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # First cleanup - should succeed
        result1 = cleanup_file(tmp_path)
        assert result1 is True, "First cleanup should succeed"
        assert not os.path.exists(tmp_path), "File should not exist after first cleanup"
        
        # Second cleanup - should also succeed (file already gone)
        result2 = cleanup_file(tmp_path)
        assert result2 is True, "Second cleanup should also succeed"
        assert not os.path.exists(tmp_path), "File should still not exist"
        
        # Third cleanup - should also succeed
        result3 = cleanup_file(tmp_path)
        assert result3 is True, "Third cleanup should also succeed"


class TestSendVideoCleanupGuarantee:
    """
    Property tests for send_video cleanup guarantee.
    
    Tests that send_video ALWAYS cleans up the file, regardless of whether
    sending succeeds or fails.
    
    **Validates: Requirements 4.3, 4.4, 7.1**
    """
    
    @given(content=file_content_strategy)
    @settings(max_examples=50)
    def test_send_video_cleans_up_on_success(self, content: bytes):
        """
        Property: send_video cleans up file after successful send
        
        **Validates: Requirements 4.3, 7.1**
        
        When video is sent successfully, the temporary file should be deleted.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Verify file exists before send
        assert os.path.exists(tmp_path), "File should exist before send_video"
        
        # Create a mock bot that succeeds
        mock_bot = MagicMock()
        mock_bot.send_video = AsyncMock(return_value=None)
        
        # Run send_video
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, error = loop.run_until_complete(
                send_video(mock_bot, chat_id=12345, file_path=tmp_path)
            )
        finally:
            loop.close()
        
        # File should be cleaned up regardless of result
        assert not os.path.exists(tmp_path), (
            f"File should be cleaned up after send_video (success={success}): {tmp_path}"
        )
    
    @given(content=file_content_strategy)
    @settings(max_examples=50)
    def test_send_video_cleans_up_on_send_failure(self, content: bytes):
        """
        Property: send_video cleans up file even when sending fails
        
        **Validates: Requirements 4.4, 7.1**
        
        When video sending fails (e.g., Telegram API error), the temporary file
        should still be deleted to prevent storage overflow.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Verify file exists before send
        assert os.path.exists(tmp_path), "File should exist before send_video"
        
        # Create a mock bot that fails
        mock_bot = MagicMock()
        mock_bot.send_video = AsyncMock(side_effect=Exception("Telegram API error"))
        
        # Run send_video
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, error = loop.run_until_complete(
                send_video(mock_bot, chat_id=12345, file_path=tmp_path)
            )
        finally:
            loop.close()
        
        # send_video should return failure
        assert success is False, "send_video should return False on failure"
        
        # File should STILL be cleaned up even on failure
        assert not os.path.exists(tmp_path), (
            f"File should be cleaned up even after send_video failure: {tmp_path}"
        )
    
    @given(content=st.binary(min_size=100, max_size=1024))
    @settings(max_examples=50)
    def test_send_video_cleans_up_on_file_too_large(self, content: bytes):
        """
        Property: send_video cleans up file when file exceeds size limit
        
        **Validates: Requirements 4.4, 7.1**
        
        When video file is too large to send, the file should still be deleted.
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Verify file exists before send
        assert os.path.exists(tmp_path), "File should exist before send_video"
        
        # Create a mock bot
        mock_bot = MagicMock()
        mock_bot.send_video = AsyncMock(return_value=None)
        
        # Set max_size smaller than file content to trigger "file too large" error
        max_size = len(content) - 1
        
        # Run send_video with small max_size
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, error = loop.run_until_complete(
                send_video(mock_bot, chat_id=12345, file_path=tmp_path, max_size=max_size)
            )
        finally:
            loop.close()
        
        # send_video should return failure due to file size
        assert success is False, "send_video should return False for oversized file"
        assert error is not None, "Error message should be provided"
        
        # File should STILL be cleaned up
        assert not os.path.exists(tmp_path), (
            f"File should be cleaned up even when file is too large: {tmp_path}"
        )


class TestCleanupGuaranteeEdgeCases:
    """
    Edge case tests for cleanup guarantee.
    
    **Validates: Requirements 4.3, 4.4, 7.1**
    """
    
    @given(content=file_content_strategy)
    @settings(max_examples=30)
    def test_cleanup_after_multiple_read_operations(self, content: bytes):
        """
        Property: cleanup_file works after file has been read multiple times
        
        **Validates: Requirements 4.3, 7.1**
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Read the file multiple times (simulating what send_video does)
        for _ in range(3):
            with open(tmp_path, 'rb') as f:
                _ = f.read()
        
        # Cleanup should still work
        result = cleanup_file(tmp_path)
        
        assert result is True, "cleanup_file should succeed after multiple reads"
        assert not os.path.exists(tmp_path), "File should not exist after cleanup"
    
    def test_send_video_cleans_up_nonexistent_file(self):
        """
        Property: send_video handles non-existent file gracefully
        
        **Validates: Requirements 4.4, 7.1**
        
        When send_video is called with a non-existent file, it should not crash
        and should handle the cleanup gracefully.
        """
        nonexistent_path = os.path.join(tempfile.gettempdir(), "nonexistent_video_test.mp4")
        
        # Ensure file doesn't exist
        if os.path.exists(nonexistent_path):
            os.remove(nonexistent_path)
        
        # Create a mock bot
        mock_bot = MagicMock()
        mock_bot.send_video = AsyncMock(return_value=None)
        
        # Run send_video with non-existent file
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, error = loop.run_until_complete(
                send_video(mock_bot, chat_id=12345, file_path=nonexistent_path)
            )
        finally:
            loop.close()
        
        # Should return failure (file doesn't exist)
        assert success is False, "send_video should return False for non-existent file"
        
        # File should still not exist (cleanup is a no-op)
        assert not os.path.exists(nonexistent_path), "File should not exist"
    
    @given(content=file_content_strategy)
    @settings(max_examples=30)
    def test_cleanup_guarantee_with_empty_file(self, content: bytes):
        """
        Property: cleanup_file works correctly with empty files
        
        **Validates: Requirements 4.3, 7.1**
        """
        # Create an empty temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            # Don't write anything - empty file
            tmp_path = tmp_file.name
        
        # Verify file exists (even if empty)
        assert os.path.exists(tmp_path), "Empty file should exist"
        
        # Cleanup should work
        result = cleanup_file(tmp_path)
        
        assert result is True, "cleanup_file should succeed for empty file"
        assert not os.path.exists(tmp_path), "Empty file should be deleted"
