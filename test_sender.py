#!/usr/bin/env python3
"""
Unit Tests for Video Sender Module

Tests cho các hàm cleanup_file, is_file_size_valid, và send_video.

Requirements: 4.1, 4.2, 4.3, 4.4, 7.1, 7.2
"""

import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sender import (
    cleanup_file,
    get_file_size,
    is_file_size_valid,
    send_video,
    DEFAULT_MAX_FILE_SIZE,
)


class TestCleanupFile:
    """Tests cho hàm cleanup_file"""
    
    def test_cleanup_existing_file(self):
        """Test xóa file tồn tại thành công"""
        # Tạo file tạm
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b"test content")
        
        # Verify file tồn tại
        assert os.path.exists(temp_path)
        
        # Xóa file
        result = cleanup_file(temp_path)
        
        # Verify kết quả
        assert result is True
        assert not os.path.exists(temp_path)
    
    def test_cleanup_nonexistent_file(self):
        """Test xóa file không tồn tại - trả về True"""
        nonexistent_path = "/tmp/nonexistent_file_12345.mp4"
        
        # Đảm bảo file không tồn tại
        assert not os.path.exists(nonexistent_path)
        
        # Xóa file không tồn tại
        result = cleanup_file(nonexistent_path)
        
        # Vẫn trả về True vì file đã không tồn tại
        assert result is True
    
    def test_cleanup_invalid_path(self):
        """Test xóa với đường dẫn không hợp lệ - xử lý gracefully"""
        # Đường dẫn không hợp lệ (thư mục không tồn tại)
        invalid_path = "/nonexistent_dir/file.mp4"
        
        # Không raise exception
        result = cleanup_file(invalid_path)
        
        # Trả về True vì file không tồn tại
        assert result is True
    
    def test_cleanup_directory_fails(self):
        """Test xóa thư mục thay vì file - trả về False"""
        # Tạo thư mục tạm
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Cố gắng xóa thư mục bằng cleanup_file
            result = cleanup_file(temp_dir)
            
            # Trả về False vì không thể xóa thư mục bằng os.remove
            assert result is False
        finally:
            # Cleanup thư mục
            os.rmdir(temp_dir)


class TestGetFileSize:
    """Tests cho hàm get_file_size"""
    
    def test_get_size_existing_file(self):
        """Test lấy kích thước file tồn tại"""
        content = b"Hello, World!"
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(content)
        
        try:
            size = get_file_size(temp_path)
            assert size == len(content)
        finally:
            os.remove(temp_path)
    
    def test_get_size_nonexistent_file(self):
        """Test lấy kích thước file không tồn tại - trả về -1"""
        nonexistent_path = "/tmp/nonexistent_file_67890.mp4"
        
        size = get_file_size(nonexistent_path)
        
        assert size == -1
    
    def test_get_size_empty_file(self):
        """Test lấy kích thước file rỗng"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            size = get_file_size(temp_path)
            assert size == 0
        finally:
            os.remove(temp_path)


class TestIsFileSizeValid:
    """Tests cho hàm is_file_size_valid"""
    
    def test_valid_size_under_limit(self):
        """Test file nhỏ hơn giới hạn - trả về True"""
        # Tạo file 1KB
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b"x" * 1024)  # 1KB
        
        try:
            result = is_file_size_valid(temp_path, max_size=50 * 1024 * 1024)
            assert result is True
        finally:
            os.remove(temp_path)
    
    def test_valid_size_at_limit(self):
        """Test file đúng bằng giới hạn - trả về True"""
        # Tạo file 100 bytes với giới hạn 100 bytes
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b"x" * 100)
        
        try:
            result = is_file_size_valid(temp_path, max_size=100)
            assert result is True
        finally:
            os.remove(temp_path)
    
    def test_invalid_size_over_limit(self):
        """Test file lớn hơn giới hạn - trả về False"""
        # Tạo file 200 bytes với giới hạn 100 bytes
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b"x" * 200)
        
        try:
            result = is_file_size_valid(temp_path, max_size=100)
            assert result is False
        finally:
            os.remove(temp_path)
    
    def test_nonexistent_file(self):
        """Test file không tồn tại - trả về False"""
        nonexistent_path = "/tmp/nonexistent_file_size_check.mp4"
        
        result = is_file_size_valid(nonexistent_path)
        
        assert result is False
    
    def test_default_max_size(self):
        """Test sử dụng giới hạn mặc định 50MB"""
        # Tạo file nhỏ
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b"small file")
        
        try:
            # Không truyền max_size, sử dụng mặc định
            result = is_file_size_valid(temp_path)
            assert result is True
        finally:
            os.remove(temp_path)


class TestSendVideo:
    """Tests cho hàm send_video"""
    
    @pytest.mark.asyncio
    async def test_send_video_success(self):
        """Test gửi video thành công"""
        # Tạo file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path = f.name
            f.write(b"video content")
        
        # Mock bot
        mock_bot = AsyncMock()
        mock_bot.send_video = AsyncMock()
        
        # Gửi video
        success, error = await send_video(mock_bot, chat_id=123, file_path=temp_path)
        
        # Verify kết quả
        assert success is True
        assert error is None
        
        # Verify bot.send_video được gọi
        mock_bot.send_video.assert_called_once()
        
        # Verify file đã bị xóa (cleanup)
        assert not os.path.exists(temp_path)
    
    @pytest.mark.asyncio
    async def test_send_video_file_too_large(self):
        """Test gửi video quá lớn - trả về lỗi"""
        # Tạo file 200 bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path = f.name
            f.write(b"x" * 200)
        
        # Mock bot
        mock_bot = AsyncMock()
        
        # Gửi video với giới hạn 100 bytes
        success, error = await send_video(
            mock_bot, 
            chat_id=123, 
            file_path=temp_path,
            max_size=100
        )
        
        # Verify kết quả
        assert success is False
        assert error is not None
        assert "quá lớn" in error
        
        # Verify bot.send_video KHÔNG được gọi
        mock_bot.send_video.assert_not_called()
        
        # Verify file vẫn bị xóa (cleanup)
        assert not os.path.exists(temp_path)
    
    @pytest.mark.asyncio
    async def test_send_video_file_not_found(self):
        """Test gửi video không tồn tại - trả về lỗi"""
        nonexistent_path = "/tmp/nonexistent_video_12345.mp4"
        
        # Mock bot
        mock_bot = AsyncMock()
        
        # Gửi video
        success, error = await send_video(mock_bot, chat_id=123, file_path=nonexistent_path)
        
        # Verify kết quả
        assert success is False
        assert error is not None
        assert "không tồn tại" in error
        
        # Verify bot.send_video KHÔNG được gọi
        mock_bot.send_video.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_video_telegram_error(self):
        """Test lỗi khi gửi video qua Telegram - cleanup vẫn được thực hiện"""
        # Tạo file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path = f.name
            f.write(b"video content")
        
        # Mock bot với lỗi
        mock_bot = AsyncMock()
        mock_bot.send_video = AsyncMock(side_effect=Exception("Telegram API error"))
        
        # Gửi video
        success, error = await send_video(mock_bot, chat_id=123, file_path=temp_path)
        
        # Verify kết quả
        assert success is False
        assert error is not None
        assert "Lỗi khi gửi video" in error
        
        # Verify file vẫn bị xóa (cleanup trong finally)
        assert not os.path.exists(temp_path)
    
    @pytest.mark.asyncio
    async def test_send_video_cleanup_always_runs(self):
        """Test cleanup luôn chạy bất kể kết quả"""
        # Tạo file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path = f.name
            f.write(b"video content")
        
        # Mock bot thành công
        mock_bot = AsyncMock()
        
        # Gửi video thành công
        await send_video(mock_bot, chat_id=123, file_path=temp_path)
        
        # File phải bị xóa
        assert not os.path.exists(temp_path)
        
        # Tạo file mới
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path2 = f.name
            f.write(b"video content 2")
        
        # Mock bot với lỗi
        mock_bot_error = AsyncMock()
        mock_bot_error.send_video = AsyncMock(side_effect=Exception("Error"))
        
        # Gửi video thất bại
        await send_video(mock_bot_error, chat_id=123, file_path=temp_path2)
        
        # File vẫn phải bị xóa
        assert not os.path.exists(temp_path2)
    
    @pytest.mark.asyncio
    async def test_send_video_at_size_limit(self):
        """Test gửi video đúng bằng giới hạn kích thước"""
        # Tạo file đúng 100 bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path = f.name
            f.write(b"x" * 100)
        
        # Mock bot
        mock_bot = AsyncMock()
        
        # Gửi video với giới hạn 100 bytes
        success, error = await send_video(
            mock_bot, 
            chat_id=123, 
            file_path=temp_path,
            max_size=100
        )
        
        # Verify kết quả - file đúng bằng giới hạn vẫn được gửi
        assert success is True
        assert error is None
        
        # Verify bot.send_video được gọi
        mock_bot.send_video.assert_called_once()


class TestDefaultMaxFileSize:
    """Tests cho hằng số DEFAULT_MAX_FILE_SIZE"""
    
    def test_default_max_file_size_is_50mb(self):
        """Test giá trị mặc định là 50MB"""
        expected_size = 50 * 1024 * 1024  # 50MB in bytes
        assert DEFAULT_MAX_FILE_SIZE == expected_size
