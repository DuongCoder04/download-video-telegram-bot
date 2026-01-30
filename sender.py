#!/usr/bin/env python3
"""
Video Sender Module for Telegram Video Downloader Bot

Module xử lý việc gửi video về Telegram và quản lý file tạm.

Requirements: 4.1, 4.2, 4.3, 4.4, 7.1, 7.2
"""

import os
import logging

# Default file size limit for Telegram bots (50MB)
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

# Configure logging
logger = logging.getLogger(__name__)


def cleanup_file(file_path: str) -> bool:
    """
    Xóa file tạm một cách an toàn.
    
    Hàm này xóa file tại đường dẫn được chỉ định. Nếu file không tồn tại
    hoặc có lỗi khi xóa, hàm sẽ xử lý gracefully mà không raise exception.
    
    Args:
        file_path: Đường dẫn đến file cần xóa
        
    Returns:
        True nếu file được xóa thành công hoặc không tồn tại,
        False nếu có lỗi khi xóa
        
    Requirements: 4.3, 4.4, 7.1
    
    Example:
        >>> cleanup_file("/tmp/video_123.mp4")
        True
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Đã xóa file tạm: {file_path}")
            return True
        else:
            # File không tồn tại, coi như đã xóa thành công
            logger.debug(f"File không tồn tại, bỏ qua: {file_path}")
            return True
    except Exception as e:
        # Log lỗi nhưng không raise exception
        logger.error(f"Lỗi khi xóa file {file_path}: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Lấy kích thước file tính bằng bytes.
    
    Args:
        file_path: Đường dẫn đến file
        
    Returns:
        Kích thước file tính bằng bytes, hoặc -1 nếu file không tồn tại
        
    Requirements: 4.1, 4.2
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return -1
    except Exception as e:
        logger.error(f"Lỗi khi lấy kích thước file {file_path}: {e}")
        return -1


def is_file_size_valid(file_path: str, max_size: int = DEFAULT_MAX_FILE_SIZE) -> bool:
    """
    Kiểm tra xem kích thước file có nằm trong giới hạn cho phép không.
    
    Telegram Bot API giới hạn kích thước file gửi là 50MB.
    Hàm này kiểm tra file có vượt quá giới hạn này không.
    
    Args:
        file_path: Đường dẫn đến file cần kiểm tra
        max_size: Kích thước tối đa cho phép (mặc định 50MB)
        
    Returns:
        True nếu file_size <= max_size, False nếu file_size > max_size
        hoặc nếu không thể đọc kích thước file
        
    Requirements: 4.1, 4.2
    
    Example:
        >>> is_file_size_valid("/tmp/small_video.mp4")  # 10MB file
        True
        >>> is_file_size_valid("/tmp/large_video.mp4")  # 100MB file
        False
    """
    file_size = get_file_size(file_path)
    if file_size < 0:
        # Không thể đọc kích thước file
        return False
    return file_size <= max_size


async def send_video(
    bot,
    chat_id: int,
    file_path: str,
    max_size: int = DEFAULT_MAX_FILE_SIZE
) -> tuple[bool, str | None]:
    """
    Gửi video về Telegram và xóa file sau đó.
    
    Hàm này thực hiện các bước:
    1. Kiểm tra kích thước file (phải <= 50MB)
    2. Gửi video về chat Telegram
    3. Xóa file tạm (bất kể thành công hay thất bại)
    
    Args:
        bot: Instance của Telegram Bot
        chat_id: ID của chat để gửi video
        file_path: Đường dẫn đến file video
        max_size: Kích thước tối đa cho phép (mặc định 50MB)
        
    Returns:
        Tuple (success, error_message):
        - (True, None) nếu gửi thành công
        - (False, error_message) nếu thất bại
        
    Requirements: 4.1, 4.2, 4.3, 4.4, 7.1, 7.2
    
    Note:
        File tạm sẽ LUÔN được xóa sau khi gửi, bất kể thành công hay thất bại.
        Điều này đảm bảo không tràn bộ nhớ trên server.
    """
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            logger.error(f"File không tồn tại: {file_path}")
            return False, "File video không tồn tại"
        
        # Kiểm tra kích thước file trước khi gửi
        file_size = get_file_size(file_path)
        if file_size < 0:
            logger.error(f"Không thể đọc kích thước file: {file_path}")
            return False, "Không thể đọc kích thước file"
        
        if file_size > max_size:
            size_mb = file_size / (1024 * 1024)
            max_mb = max_size / (1024 * 1024)
            error_msg = (
                f"Video quá lớn ({size_mb:.1f}MB > {max_mb:.0f}MB). "
                "Vui lòng thử giảm chất lượng hoặc cắt video ngắn hơn."
            )
            logger.warning(f"File quá lớn: {file_path} ({size_mb:.1f}MB)")
            return False, error_msg
        
        # Gửi video về Telegram
        logger.info(f"Đang gửi video: {file_path} ({file_size / (1024 * 1024):.1f}MB)")
        with open(file_path, 'rb') as video:
            await bot.send_video(chat_id=chat_id, video=video)
        
        logger.info(f"Gửi video thành công: {file_path}")
        return True, None
        
    except Exception as e:
        error_msg = f"Lỗi khi gửi video: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
        
    finally:
        # LUÔN xóa file tạm, bất kể thành công hay thất bại
        # Đảm bảo không tràn bộ nhớ trên server
        cleanup_file(file_path)
