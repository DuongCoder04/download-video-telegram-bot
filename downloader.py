#!/usr/bin/env python3
"""
Video Downloader Module for Telegram Video Downloader Bot

Module sử dụng yt-dlp để tải video từ các nền tảng được hỗ trợ.

Requirements: 3.1, 3.3, 3.5
"""

import os
import uuid
from typing import Callable

import yt_dlp

from models import DownloadResult


def get_yt_dlp_options(
    output_path: str,
    max_size: int = 50 * 1024 * 1024,
    progress_callback: Callable[[float], None] | None = None
) -> dict:
    """
    Tạo options cho yt-dlp.
    
    Args:
        output_path: Đường dẫn file output
        max_size: Kích thước tối đa của video (bytes), mặc định 50MB
        progress_callback: Callback function để cập nhật tiến trình (0.0 - 100.0)
    
    Returns:
        Dictionary chứa các options cho yt-dlp
    
    Requirements: 3.5
    """
    # Format selection: prefer best format under max_size, fallback to best available
    # Note: filesize filter may not work for all videos (some don't report size)
    format_string = f'best[filesize<{max_size}]/bestvideo[filesize<{max_size}]+bestaudio/best'
    
    opts = {
        'format': format_string,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }
    
    # Add progress hook if callback is provided
    if progress_callback is not None:
        opts['progress_hooks'] = [
            lambda d: _handle_progress(d, progress_callback)
        ]
    
    return opts


def _handle_progress(
    progress_dict: dict,
    callback: Callable[[float], None] | None
) -> None:
    """
    Xử lý progress hook từ yt-dlp và gọi callback với phần trăm hoàn thành.
    
    Args:
        progress_dict: Dictionary chứa thông tin tiến trình từ yt-dlp
        callback: Callback function để cập nhật tiến trình
    
    Requirements: 3.1 (progress tracking during download)
    """
    if callback is None:
        return
    
    status = progress_dict.get('status', '')
    
    if status == 'downloading':
        # Try to calculate percentage from downloaded and total bytes
        downloaded = progress_dict.get('downloaded_bytes', 0)
        total = progress_dict.get('total_bytes') or progress_dict.get('total_bytes_estimate') or 0
        
        if total > 0:
            percentage = (downloaded / total) * 100.0
            callback(min(percentage, 99.0))  # Cap at 99% until finished
        else:
            # If total is unknown, use fragment info if available
            fragment_index = progress_dict.get('fragment_index', 0)
            fragment_count = progress_dict.get('fragment_count', 0)
            if fragment_count > 0:
                percentage = (fragment_index / fragment_count) * 100.0
                callback(min(percentage, 99.0))
    
    elif status == 'finished':
        callback(100.0)


def download_video(
    url: str,
    output_dir: str = "/tmp",
    max_size: int = 50 * 1024 * 1024,
    progress_callback: Callable[[float], None] | None = None
) -> DownloadResult:
    """
    Tải video từ URL với giới hạn kích thước.
    
    Sử dụng yt-dlp để tải video và lưu vào thư mục output với tên file duy nhất
    được tạo bằng UUID.
    
    Args:
        url: URL của video cần tải
        output_dir: Thư mục lưu file output, mặc định "/tmp"
        max_size: Kích thước tối đa của video (bytes), mặc định 50MB
        progress_callback: Callback function để cập nhật tiến trình (0.0 - 100.0)
    
    Returns:
        DownloadResult với thông tin về kết quả tải:
        - success: True nếu tải thành công
        - file_path: Đường dẫn file đã tải (None nếu thất bại)
        - error_message: Thông báo lỗi (None nếu thành công)
        - file_size: Kích thước file (0 nếu thất bại)
    
    Requirements: 3.1, 3.3, 3.5
    """
    # Generate unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, unique_filename)
    
    # Get yt-dlp options
    ydl_opts = get_yt_dlp_options(output_path, max_size, progress_callback)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Check if file was created and get its size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            return DownloadResult(
                success=True,
                file_path=output_path,
                error_message=None,
                file_size=file_size
            )
        else:
            # File wasn't created - check for alternative extensions
            # yt-dlp might save with different extension
            base_path = output_path.rsplit('.', 1)[0]
            for ext in ['.mp4', '.mkv', '.webm', '.m4a']:
                alt_path = base_path + ext
                if os.path.exists(alt_path):
                    file_size = os.path.getsize(alt_path)
                    return DownloadResult(
                        success=True,
                        file_path=alt_path,
                        error_message=None,
                        file_size=file_size
                    )
            
            return DownloadResult(
                success=False,
                file_path=None,
                error_message="File không được tạo sau khi tải",
                file_size=0
            )
    
    except yt_dlp.utils.DownloadError as e:
        return DownloadResult(
            success=False,
            file_path=None,
            error_message=str(e),
            file_size=0
        )
    except Exception as e:
        return DownloadResult(
            success=False,
            file_path=None,
            error_message=str(e),
            file_size=0
        )
