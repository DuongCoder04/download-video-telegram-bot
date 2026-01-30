#!/usr/bin/env python3
"""
Auth Module for Telegram Video Downloader Bot

Module xác thực người dùng dựa trên OWNER_ID.
Chỉ cho phép người dùng có user_id khớp với OWNER_ID sử dụng bot.

Requirements: 1.1, 1.2, 1.3
"""

from functools import wraps
from typing import Callable, Any


def is_authorized(user_id: int, owner_id: int) -> bool:
    """
    Kiểm tra user có được phép sử dụng bot không.
    
    Args:
        user_id: ID của người dùng gửi tin nhắn
        owner_id: ID của chủ sở hữu bot (từ biến môi trường OWNER_ID)
    
    Returns:
        True nếu user_id khớp với owner_id, False nếu không khớp
    
    Requirements: 1.1, 1.2
    
    Examples:
        >>> is_authorized(123456789, 123456789)
        True
        >>> is_authorized(123456789, 987654321)
        False
    """
    return user_id == owner_id


def auth_decorator(owner_id: int) -> Callable:
    """
    Decorator để bảo vệ các handler, chỉ cho phép owner sử dụng.
    
    Decorator này kiểm tra user_id của người gửi tin nhắn với owner_id.
    Nếu không khớp, handler sẽ bỏ qua tin nhắn mà không phản hồi.
    
    Args:
        owner_id: ID của chủ sở hữu bot (từ biến môi trường OWNER_ID)
    
    Returns:
        Decorator function để wrap các async handler
    
    Requirements: 1.1, 1.2, 1.3
    
    Usage:
        @auth_decorator(owner_id=123456789)
        async def my_handler(update, context):
            # Handler code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Any, context: Any) -> Any:
            # Kiểm tra xem update có effective_user không
            if update.effective_user is None:
                return None  # Bỏ qua nếu không có thông tin user
            
            # Kiểm tra xác thực
            if not is_authorized(update.effective_user.id, owner_id):
                return None  # Bỏ qua tin nhắn từ user không được phép
            
            # User được phép, thực thi handler
            return await func(update, context)
        return wrapper
    return decorator
