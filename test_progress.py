#!/usr/bin/env python3
"""
Unit Tests for Progress Manager Module

Tests cho ProgressManager class và các phương thức quản lý tin nhắn tiến trình.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from progress import ProgressManager, DEFAULT_MESSAGES


class TestProgressManager:
    """Tests cho ProgressManager class."""
    
    @pytest.fixture
    def mock_bot(self):
        """Tạo mock bot cho testing."""
        bot = MagicMock()
        bot.send_message = AsyncMock()
        bot.edit_message_text = AsyncMock()
        bot.delete_message = AsyncMock()
        return bot
    
    @pytest.fixture
    def progress_manager(self, mock_bot):
        """Tạo ProgressManager instance với mock bot."""
        return ProgressManager(mock_bot)
    
    # ==================== Test send_progress ====================
    
    @pytest.mark.asyncio
    async def test_send_progress_returns_message_id(self, progress_manager, mock_bot):
        """
        Test send_progress trả về message_id đúng.
        
        Validates: Requirement 5.1
        """
        # Arrange
        mock_message = MagicMock()
        mock_message.message_id = 42
        mock_bot.send_message.return_value = mock_message
        
        # Act
        result = await progress_manager.send_progress(123456, "Đang tải video...")
        
        # Assert
        assert result == 42
        mock_bot.send_message.assert_called_once_with(
            chat_id=123456, 
            text="Đang tải video..."
        )
    
    @pytest.mark.asyncio
    async def test_send_progress_with_different_text(self, progress_manager, mock_bot):
        """
        Test send_progress với các nội dung khác nhau.
        
        Validates: Requirement 5.1
        """
        # Arrange
        mock_message = MagicMock()
        mock_message.message_id = 100
        mock_bot.send_message.return_value = mock_message
        
        # Act
        result = await progress_manager.send_progress(999, "Custom message")
        
        # Assert
        assert result == 100
        mock_bot.send_message.assert_called_once_with(
            chat_id=999, 
            text="Custom message"
        )
    
    # ==================== Test update_progress ====================
    
    @pytest.mark.asyncio
    async def test_update_progress_success(self, progress_manager, mock_bot):
        """
        Test update_progress cập nhật tin nhắn thành công.
        
        Validates: Requirements 5.2, 5.3
        """
        # Act
        result = await progress_manager.update_progress(123456, 42, "Đang tải: 50%")
        
        # Assert
        assert result is True
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Đang tải: 50%"
        )
    
    @pytest.mark.asyncio
    async def test_update_progress_failure(self, progress_manager, mock_bot):
        """
        Test update_progress xử lý lỗi gracefully.
        
        Validates: Requirements 5.2, 5.3
        """
        # Arrange
        mock_bot.edit_message_text.side_effect = Exception("Message not found")
        
        # Act
        result = await progress_manager.update_progress(123456, 42, "New text")
        
        # Assert
        assert result is False
    
    # ==================== Test delete_progress ====================
    
    @pytest.mark.asyncio
    async def test_delete_progress_success(self, progress_manager, mock_bot):
        """
        Test delete_progress xóa tin nhắn thành công.
        
        Validates: Requirement 5.4
        """
        # Act
        result = await progress_manager.delete_progress(123456, 42)
        
        # Assert
        assert result is True
        mock_bot.delete_message.assert_called_once_with(
            chat_id=123456,
            message_id=42
        )
    
    @pytest.mark.asyncio
    async def test_delete_progress_failure(self, progress_manager, mock_bot):
        """
        Test delete_progress xử lý lỗi gracefully.
        
        Validates: Requirement 5.4
        """
        # Arrange
        mock_bot.delete_message.side_effect = Exception("Message already deleted")
        
        # Act
        result = await progress_manager.delete_progress(123456, 42)
        
        # Assert
        assert result is False
    
    # ==================== Test send_downloading ====================
    
    @pytest.mark.asyncio
    async def test_send_downloading(self, progress_manager, mock_bot):
        """
        Test send_downloading gửi tin nhắn "Đang tải video...".
        
        Validates: Requirement 5.1
        """
        # Arrange
        mock_message = MagicMock()
        mock_message.message_id = 55
        mock_bot.send_message.return_value = mock_message
        
        # Act
        result = await progress_manager.send_downloading(123456)
        
        # Assert
        assert result == 55
        mock_bot.send_message.assert_called_once_with(
            chat_id=123456,
            text="Đang tải video..."
        )
    
    # ==================== Test update_downloading_percent ====================
    
    @pytest.mark.asyncio
    async def test_update_downloading_percent(self, progress_manager, mock_bot):
        """
        Test update_downloading_percent cập nhật phần trăm.
        
        Validates: Requirement 5.2
        """
        # Act
        result = await progress_manager.update_downloading_percent(123456, 42, 75.5)
        
        # Assert
        assert result is True
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Đang tải video... 76%"
        )
    
    @pytest.mark.asyncio
    async def test_update_downloading_percent_clamps_to_0(self, progress_manager, mock_bot):
        """
        Test update_downloading_percent giới hạn percent >= 0.
        
        Validates: Requirement 5.2
        """
        # Act
        await progress_manager.update_downloading_percent(123456, 42, -10)
        
        # Assert
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Đang tải video... 0%"
        )
    
    @pytest.mark.asyncio
    async def test_update_downloading_percent_clamps_to_100(self, progress_manager, mock_bot):
        """
        Test update_downloading_percent giới hạn percent <= 100.
        
        Validates: Requirement 5.2
        """
        # Act
        await progress_manager.update_downloading_percent(123456, 42, 150)
        
        # Assert
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Đang tải video... 100%"
        )
    
    # ==================== Test update_sending ====================
    
    @pytest.mark.asyncio
    async def test_update_sending(self, progress_manager, mock_bot):
        """
        Test update_sending cập nhật tin nhắn thành "Đang gửi video...".
        
        Validates: Requirement 5.3
        """
        # Act
        result = await progress_manager.update_sending(123456, 42)
        
        # Assert
        assert result is True
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Đang gửi video..."
        )
    
    # ==================== Test finalize_progress ====================
    
    @pytest.mark.asyncio
    async def test_finalize_progress_delete(self, progress_manager, mock_bot):
        """
        Test finalize_progress xóa tin nhắn khi delete=True.
        
        Validates: Requirement 5.4
        """
        # Act
        result = await progress_manager.finalize_progress(123456, 42, delete=True)
        
        # Assert
        assert result is True
        mock_bot.delete_message.assert_called_once_with(
            chat_id=123456,
            message_id=42
        )
        mock_bot.edit_message_text.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_finalize_progress_update_default_text(self, progress_manager, mock_bot):
        """
        Test finalize_progress cập nhật với text mặc định khi delete=False.
        
        Validates: Requirement 5.4
        """
        # Act
        result = await progress_manager.finalize_progress(123456, 42, delete=False)
        
        # Assert
        assert result is True
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Hoàn tất!"
        )
        mock_bot.delete_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_finalize_progress_update_custom_text(self, progress_manager, mock_bot):
        """
        Test finalize_progress cập nhật với custom text.
        
        Validates: Requirement 5.4
        """
        # Act
        result = await progress_manager.finalize_progress(
            123456, 42, 
            delete=False, 
            final_text="Video đã được gửi thành công!"
        )
        
        # Assert
        assert result is True
        mock_bot.edit_message_text.assert_called_once_with(
            chat_id=123456,
            message_id=42,
            text="Video đã được gửi thành công!"
        )


class TestDefaultMessages:
    """Tests cho DEFAULT_MESSAGES constants."""
    
    def test_default_messages_contains_downloading(self):
        """Test DEFAULT_MESSAGES có key 'downloading'."""
        assert "downloading" in DEFAULT_MESSAGES
        assert DEFAULT_MESSAGES["downloading"] == "Đang tải video..."
    
    def test_default_messages_contains_sending(self):
        """Test DEFAULT_MESSAGES có key 'sending'."""
        assert "sending" in DEFAULT_MESSAGES
        assert DEFAULT_MESSAGES["sending"] == "Đang gửi video..."
    
    def test_default_messages_contains_completed(self):
        """Test DEFAULT_MESSAGES có key 'completed'."""
        assert "completed" in DEFAULT_MESSAGES
        assert DEFAULT_MESSAGES["completed"] == "Hoàn tất!"
    
    def test_default_messages_contains_error(self):
        """Test DEFAULT_MESSAGES có key 'error'."""
        assert "error" in DEFAULT_MESSAGES
        assert DEFAULT_MESSAGES["error"] == "Có lỗi xảy ra"
