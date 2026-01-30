#!/usr/bin/env python3
"""
URL Parser Module for Telegram Video Downloader Bot

Module nhận diện và xác thực URL video từ các nền tảng được hỗ trợ.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import re
from models import Platform


# Regex patterns cho từng nền tảng video
# Requirements: 2.1, 2.2, 2.3
PLATFORM_PATTERNS: dict[Platform, list[str]] = {
    Platform.YOUTUBE: [
        # youtube.com/watch?v=VIDEO_ID (có thể có thêm params)
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        # youtube.com/shorts/VIDEO_ID
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+",
        # youtu.be/VIDEO_ID
        r"(?:https?://)?(?:www\.)?youtu\.be/[\w-]+",
    ],
    Platform.FACEBOOK: [
        # facebook.com/*/videos/VIDEO_ID
        r"(?:https?://)?(?:www\.)?facebook\.com/.+/videos/\d+",
        # facebook.com/reel/REEL_ID
        r"(?:https?://)?(?:www\.)?facebook\.com/reel/\d+",
        # facebook.com/stories/STORY_ID
        r"(?:https?://)?(?:www\.)?facebook\.com/stories/\d+",
        # fb.watch/VIDEO_ID
        r"(?:https?://)?fb\.watch/[\w-]+",
    ],
    Platform.INSTAGRAM: [
        # instagram.com/p/POST_ID hoặc instagram.com/reel/REEL_ID hoặc instagram.com/reels/REEL_ID
        r"(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|reels)/[\w-]+",
        # instagram.com/stories/USERNAME/STORY_ID
        r"(?:https?://)?(?:www\.)?instagram\.com/stories/[\w._]+/\d+",
    ],
}


def parse_url(text: str) -> tuple[str | None, Platform]:
    """
    Trích xuất URL từ text và nhận diện platform.
    
    Hàm này quét text để tìm URL video từ các nền tảng được hỗ trợ
    (YouTube, Facebook, Instagram) và trả về URL cùng với platform tương ứng.
    
    Args:
        text: Chuỗi text có thể chứa URL video
        
    Returns:
        Tuple gồm:
        - URL được trích xuất (str) hoặc None nếu không tìm thấy
        - Platform enum tương ứng (YOUTUBE, FACEBOOK, INSTAGRAM, hoặc UNKNOWN)
        
    Examples:
        >>> parse_url("Check this video: https://youtube.com/watch?v=abc123")
        ('https://youtube.com/watch?v=abc123', Platform.YOUTUBE)
        
        >>> parse_url("Hello world")
        (None, Platform.UNKNOWN)
        
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0), platform
    return None, Platform.UNKNOWN


def is_supported_platform(platform: Platform) -> bool:
    """
    Kiểm tra xem platform có được hỗ trợ hay không.
    
    Một platform được coi là hỗ trợ nếu nó không phải là UNKNOWN.
    
    Args:
        platform: Platform enum cần kiểm tra
        
    Returns:
        True nếu platform được hỗ trợ (YOUTUBE, FACEBOOK, INSTAGRAM),
        False nếu platform là UNKNOWN
        
    Examples:
        >>> is_supported_platform(Platform.YOUTUBE)
        True
        
        >>> is_supported_platform(Platform.UNKNOWN)
        False
        
    Requirements: 2.4
    """
    return platform != Platform.UNKNOWN
