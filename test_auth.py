#!/usr/bin/env python3
"""
Unit Tests for Auth Module

Tests cho các hàm xác thực trong auth.py.

Requirements: 1.1, 1.2, 1.3
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from auth import is_authorized, auth_decorator


class TestIsAuthorized:
    """Tests cho hàm is_authorized"""
    
    def test_authorized_when_ids_match(self):
        """Test: User được phép khi user_id khớp với owner_id"""
        # Requirements: 1.2
        assert is_authorized(123456789, 123456789) is True
    
    def test_not_authorized_when_ids_differ(self):
        """Test: User không được phép khi user_id khác owner_id"""
        # Requirements: 1.1
        assert is_authorized(123456789, 987654321) is False
    
    def test_authorized_with_zero_ids(self):
        """Test: Xử lý đúng khi cả hai ID đều là 0"""
        assert is_authorized(0, 0) is True
    
    def test_not_authorized_with_zero_user_id(self):
        """Test: User không được phép khi user_id là 0 nhưng owner_id khác"""
        assert is_authorized(0, 123456789) is False
    
    def test_not_authorized_with_zero_owner_id(self):
        """Test: User không được phép khi owner_id là 0 nhưng user_id khác"""
        assert is_authorized(123456789, 0) is False
    
    def test_authorized_with_large_ids(self):
        """Test: Xử lý đúng với ID lớn (Telegram user IDs có thể rất lớn)"""
        large_id = 9999999999999
        assert is_authorized(large_id, large_id) is True
    
    def test_not_authorized_with_negative_ids(self):
        """Test: Xử lý đúng với ID âm (edge case)"""
        assert is_authorized(-1, -1) is True
        assert is_authorized(-1, 1) is False


class TestAuthDecorator:
    """Tests cho auth_decorator"""
    
    @pytest.mark.asyncio
    async def test_decorator_allows_authorized_user(self):
        """Test: Decorator cho phép user được phép thực thi handler"""
        # Requirements: 1.2
        owner_id = 123456789
        
        # Mock handler
        mock_handler = AsyncMock(return_value="success")
        decorated_handler = auth_decorator(owner_id)(mock_handler)
        
        # Mock update với user được phép
        mock_update = MagicMock()
        mock_update.effective_user.id = owner_id
        mock_context = MagicMock()
        
        result = await decorated_handler(mock_update, mock_context)
        
        assert result == "success"
        mock_handler.assert_called_once_with(mock_update, mock_context)
    
    @pytest.mark.asyncio
    async def test_decorator_blocks_unauthorized_user(self):
        """Test: Decorator chặn user không được phép"""
        # Requirements: 1.1
        owner_id = 123456789
        unauthorized_user_id = 987654321
        
        # Mock handler
        mock_handler = AsyncMock(return_value="success")
        decorated_handler = auth_decorator(owner_id)(mock_handler)
        
        # Mock update với user không được phép
        mock_update = MagicMock()
        mock_update.effective_user.id = unauthorized_user_id
        mock_context = MagicMock()
        
        result = await decorated_handler(mock_update, mock_context)
        
        assert result is None
        mock_handler.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_decorator_handles_no_effective_user(self):
        """Test: Decorator xử lý đúng khi không có effective_user"""
        owner_id = 123456789
        
        # Mock handler
        mock_handler = AsyncMock(return_value="success")
        decorated_handler = auth_decorator(owner_id)(mock_handler)
        
        # Mock update không có effective_user
        mock_update = MagicMock()
        mock_update.effective_user = None
        mock_context = MagicMock()
        
        result = await decorated_handler(mock_update, mock_context)
        
        assert result is None
        mock_handler.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_decorator_preserves_function_metadata(self):
        """Test: Decorator giữ nguyên metadata của function gốc"""
        owner_id = 123456789
        
        async def original_handler(update, context):
            """Original docstring"""
            return "success"
        
        decorated_handler = auth_decorator(owner_id)(original_handler)
        
        assert decorated_handler.__name__ == "original_handler"
        assert decorated_handler.__doc__ == "Original docstring"
    
    @pytest.mark.asyncio
    async def test_decorator_passes_return_value(self):
        """Test: Decorator truyền đúng giá trị trả về từ handler"""
        owner_id = 123456789
        expected_return = {"status": "ok", "data": [1, 2, 3]}
        
        mock_handler = AsyncMock(return_value=expected_return)
        decorated_handler = auth_decorator(owner_id)(mock_handler)
        
        mock_update = MagicMock()
        mock_update.effective_user.id = owner_id
        mock_context = MagicMock()
        
        result = await decorated_handler(mock_update, mock_context)
        
        assert result == expected_return


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
