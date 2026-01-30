#!/usr/bin/env python3
"""
Data Models for Telegram Video Downloader Bot

Module chứa các data models và configuration cho bot.

Requirements: 8.1, 8.2
"""

import os
from dataclasses import dataclass
from enum import Enum


@dataclass
class BotConfig:
    """
    Configuration class for the bot.
    
    Attributes:
        telegram_token: Token của Telegram Bot từ BotFather
        owner_id: ID của người dùng duy nhất được phép sử dụng bot
        temp_dir: Thư mục lưu trữ tạm thời video
        max_file_size: Kích thước file tối đa (mặc định 50MB - giới hạn Telegram)
    
    Requirements: 8.1, 8.2
    """
    telegram_token: str
    owner_id: int
    temp_dir: str = "/tmp"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        """
        Tạo BotConfig từ biến môi trường.
        
        Đọc TELEGRAM_TOKEN và OWNER_ID từ environment variables.
        
        Returns:
            BotConfig instance với giá trị từ biến môi trường
        
        Requirements: 8.1, 8.2
        """
        return cls(
            telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
            owner_id=int(os.getenv("OWNER_ID", "0"))
        )


class Platform(Enum):
    """
    Enum đại diện cho các nền tảng video được hỗ trợ.
    
    Requirements: 2.1, 2.2, 2.3, 2.4
    """
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    UNKNOWN = "unknown"


class DownloadError(Enum):
    """
    Enum đại diện cho các loại lỗi khi tải video.
    
    Mỗi giá trị chứa thông báo lỗi tiếng Việt để hiển thị cho người dùng.
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    VIDEO_NOT_FOUND = "Video không tồn tại hoặc đã bị xóa"
    ACCESS_DENIED = "Video bị giới hạn, không thể tải"
    NETWORK_ERROR = "Lỗi kết nối mạng, vui lòng thử lại sau"
    FILE_TOO_LARGE = "Video quá lớn (>50MB), không thể gửi qua Telegram"
    YTDLP_ERROR = "Lỗi yt-dlp, có thể cần cập nhật"
    UNKNOWN_ERROR = "Lỗi không xác định"


@dataclass
class DownloadResult:
    """
    Kết quả của quá trình tải video.
    
    Attributes:
        success: True nếu tải thành công, False nếu thất bại
        file_path: Đường dẫn đến file video đã tải (None nếu thất bại)
        error_message: Thông báo lỗi (None nếu thành công)
        file_size: Kích thước file tính bằng bytes (0 nếu thất bại)
    
    Requirements: 3.1, 3.3, 4.1, 4.2
    """
    success: bool
    file_path: str | None
    error_message: str | None
    file_size: int
