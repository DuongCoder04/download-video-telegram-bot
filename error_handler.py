#!/usr/bin/env python3
"""
Error Handler Module for Telegram Video Downloader Bot

Module xử lý và mapping các lỗi từ yt-dlp sang thông báo lỗi tiếng Việt.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import logging
from models import DownloadError

# Cấu hình logging để debug
logger = logging.getLogger(__name__)


def map_ytdlp_error(error: Exception) -> DownloadError:
    """
    Map lỗi từ yt-dlp sang DownloadError enum.
    
    Phân tích nội dung lỗi để xác định loại lỗi cụ thể và trả về
    DownloadError tương ứng với thông báo tiếng Việt.
    
    Args:
        error: Exception từ yt-dlp hoặc quá trình tải video
        
    Returns:
        DownloadError enum tương ứng với loại lỗi
        
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    
    Examples:
        >>> map_ytdlp_error(Exception("Video unavailable"))
        DownloadError.VIDEO_NOT_FOUND
        >>> map_ytdlp_error(Exception("Private video"))
        DownloadError.ACCESS_DENIED
    """
    # Log lỗi để debug (Requirement 6.5)
    log_error(error)
    
    error_str = str(error).lower()
    
    # Requirement 6.1: Video không tồn tại hoặc đã bị xóa
    if _is_video_not_found_error(error_str):
        return DownloadError.VIDEO_NOT_FOUND
    
    # Requirement 6.2: Video bị giới hạn quyền truy cập
    if _is_access_denied_error(error_str):
        return DownloadError.ACCESS_DENIED
    
    # Requirement 6.3: Lỗi kết nối mạng
    if _is_network_error(error_str):
        return DownloadError.NETWORK_ERROR
    
    # Requirement 6.4: yt-dlp cần cập nhật
    if _is_ytdlp_update_error(error_str):
        return DownloadError.YTDLP_ERROR
    
    # Lỗi không xác định
    return DownloadError.UNKNOWN_ERROR


def _is_video_not_found_error(error_str: str) -> bool:
    """
    Kiểm tra xem lỗi có phải là video không tồn tại không.
    
    Args:
        error_str: Chuỗi lỗi đã được chuyển thành lowercase
        
    Returns:
        True nếu lỗi liên quan đến video không tồn tại
        
    Requirement: 6.1
    """
    not_found_keywords = [
        "video unavailable",
        "not found",
        "does not exist",
        "has been removed",
        "deleted",
        "unavailable",
        "no video",
        "404"
    ]
    return any(keyword in error_str for keyword in not_found_keywords)


def _is_access_denied_error(error_str: str) -> bool:
    """
    Kiểm tra xem lỗi có phải là video bị giới hạn quyền truy cập không.
    
    Args:
        error_str: Chuỗi lỗi đã được chuyển thành lowercase
        
    Returns:
        True nếu lỗi liên quan đến quyền truy cập bị giới hạn
        
    Requirement: 6.2
    """
    access_denied_keywords = [
        "private",
        "restricted",
        "age-restricted",
        "age restricted",
        "login required",
        "sign in",
        "members only",
        "subscribers only",
        "permission denied",
        "access denied",
        "forbidden",
        "403"
    ]
    return any(keyword in error_str for keyword in access_denied_keywords)


def _is_network_error(error_str: str) -> bool:
    """
    Kiểm tra xem lỗi có phải là lỗi kết nối mạng không.
    
    Args:
        error_str: Chuỗi lỗi đã được chuyển thành lowercase
        
    Returns:
        True nếu lỗi liên quan đến kết nối mạng
        
    Requirement: 6.3
    """
    network_keywords = [
        "network",
        "connection",
        "timeout",
        "timed out",
        "unreachable",
        "dns",
        "socket",
        "ssl",
        "certificate",
        "connect error",
        "connection refused",
        "connection reset",
        "no internet"
    ]
    return any(keyword in error_str for keyword in network_keywords)


def _is_ytdlp_update_error(error_str: str) -> bool:
    """
    Kiểm tra xem lỗi có phải là yt-dlp cần cập nhật không.
    
    Args:
        error_str: Chuỗi lỗi đã được chuyển thành lowercase
        
    Returns:
        True nếu lỗi liên quan đến yt-dlp cần cập nhật
        
    Requirement: 6.4
    """
    update_keywords = [
        "update",
        "outdated",
        "upgrade",
        "new version",
        "please update",
        "yt-dlp needs",
        "extractor error"
    ]
    return any(keyword in error_str for keyword in update_keywords)


def log_error(error: Exception, context: str = "") -> None:
    """
    Log lỗi vào console để debug.
    
    Args:
        error: Exception cần log
        context: Thông tin ngữ cảnh bổ sung (optional)
        
    Requirement: 6.5
    """
    if context:
        logger.error(f"[{context}] Error: {type(error).__name__}: {error}")
    else:
        logger.error(f"Error: {type(error).__name__}: {error}")


def get_error_message(error: DownloadError) -> str:
    """
    Lấy thông báo lỗi tiếng Việt từ DownloadError enum.
    
    Args:
        error: DownloadError enum
        
    Returns:
        Thông báo lỗi tiếng Việt
        
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    return error.value


def get_user_friendly_error(error: Exception) -> str:
    """
    Chuyển đổi Exception thành thông báo lỗi thân thiện với người dùng.
    
    Hàm tiện ích kết hợp map_ytdlp_error và get_error_message.
    
    Args:
        error: Exception từ yt-dlp hoặc quá trình tải video
        
    Returns:
        Thông báo lỗi tiếng Việt thân thiện với người dùng
        
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    download_error = map_ytdlp_error(error)
    return get_error_message(download_error)
