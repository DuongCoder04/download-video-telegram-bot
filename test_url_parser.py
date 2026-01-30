#!/usr/bin/env python3
"""
Unit Tests for URL Parser Module

Tests cho các hàm parse URL và nhận diện platform trong url_parser.py.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
from url_parser import parse_url, is_supported_platform, PLATFORM_PATTERNS
from models import Platform


class TestParseUrlYouTube:
    """Tests cho nhận diện URL YouTube - Requirements: 2.1"""
    
    def test_youtube_watch_url_with_https_www(self):
        """Test: Nhận diện URL youtube.com/watch với https và www"""
        url, platform = parse_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert platform == Platform.YOUTUBE
        assert "youtube.com/watch?v=dQw4w9WgXcQ" in url
    
    def test_youtube_watch_url_with_https_no_www(self):
        """Test: Nhận diện URL youtube.com/watch với https không có www"""
        url, platform = parse_url("https://youtube.com/watch?v=abc123")
        assert platform == Platform.YOUTUBE
        assert "youtube.com/watch?v=abc123" in url
    
    def test_youtube_watch_url_with_http(self):
        """Test: Nhận diện URL youtube.com/watch với http"""
        url, platform = parse_url("http://www.youtube.com/watch?v=xyz789")
        assert platform == Platform.YOUTUBE
        assert "youtube.com/watch?v=xyz789" in url
    
    def test_youtube_watch_url_no_protocol(self):
        """Test: Nhận diện URL youtube.com/watch không có protocol"""
        url, platform = parse_url("youtube.com/watch?v=test123")
        assert platform == Platform.YOUTUBE
        assert "youtube.com/watch?v=test123" in url
    
    def test_youtu_be_short_url_with_https(self):
        """Test: Nhận diện URL youtu.be với https"""
        url, platform = parse_url("https://youtu.be/dQw4w9WgXcQ")
        assert platform == Platform.YOUTUBE
        assert "youtu.be/dQw4w9WgXcQ" in url
    
    def test_youtu_be_short_url_no_protocol(self):
        """Test: Nhận diện URL youtu.be không có protocol"""
        url, platform = parse_url("youtu.be/abc123")
        assert platform == Platform.YOUTUBE
        assert "youtu.be/abc123" in url
    
    def test_youtube_url_in_text(self):
        """Test: Trích xuất URL YouTube từ text dài"""
        text = "Check out this video: https://youtube.com/watch?v=test123 it's great!"
        url, platform = parse_url(text)
        assert platform == Platform.YOUTUBE
        assert "youtube.com/watch?v=test123" in url


class TestParseUrlFacebook:
    """Tests cho nhận diện URL Facebook - Requirements: 2.2"""
    
    def test_facebook_videos_url_with_https_www(self):
        """Test: Nhận diện URL facebook.com/videos với https và www"""
        url, platform = parse_url("https://www.facebook.com/user/videos/123456789")
        assert platform == Platform.FACEBOOK
        assert "facebook.com/user/videos/123456789" in url
    
    def test_facebook_videos_url_no_www(self):
        """Test: Nhận diện URL facebook.com/videos không có www"""
        url, platform = parse_url("https://facebook.com/page/videos/987654321")
        assert platform == Platform.FACEBOOK
        assert "facebook.com/page/videos/987654321" in url
    
    def test_facebook_videos_url_no_protocol(self):
        """Test: Nhận diện URL facebook.com/videos không có protocol"""
        url, platform = parse_url("facebook.com/user/videos/111222333")
        assert platform == Platform.FACEBOOK
        assert "facebook.com/user/videos/111222333" in url
    
    def test_fb_watch_url_with_https(self):
        """Test: Nhận diện URL fb.watch với https"""
        url, platform = parse_url("https://fb.watch/abc123xyz")
        assert platform == Platform.FACEBOOK
        assert "fb.watch/abc123xyz" in url
    
    def test_fb_watch_url_no_protocol(self):
        """Test: Nhận diện URL fb.watch không có protocol"""
        url, platform = parse_url("fb.watch/xyz789")
        assert platform == Platform.FACEBOOK
        assert "fb.watch/xyz789" in url
    
    def test_facebook_url_in_text(self):
        """Test: Trích xuất URL Facebook từ text dài"""
        text = "Watch this: https://fb.watch/video123 amazing content!"
        url, platform = parse_url(text)
        assert platform == Platform.FACEBOOK
        assert "fb.watch/video123" in url


class TestParseUrlInstagram:
    """Tests cho nhận diện URL Instagram - Requirements: 2.3"""
    
    def test_instagram_post_url_with_https_www(self):
        """Test: Nhận diện URL instagram.com/p với https và www"""
        url, platform = parse_url("https://www.instagram.com/p/ABC123xyz")
        assert platform == Platform.INSTAGRAM
        assert "instagram.com/p/ABC123xyz" in url
    
    def test_instagram_post_url_no_www(self):
        """Test: Nhận diện URL instagram.com/p không có www"""
        url, platform = parse_url("https://instagram.com/p/XYZ789abc")
        assert platform == Platform.INSTAGRAM
        assert "instagram.com/p/XYZ789abc" in url
    
    def test_instagram_post_url_no_protocol(self):
        """Test: Nhận diện URL instagram.com/p không có protocol"""
        url, platform = parse_url("instagram.com/p/test123")
        assert platform == Platform.INSTAGRAM
        assert "instagram.com/p/test123" in url
    
    def test_instagram_reel_url_with_https(self):
        """Test: Nhận diện URL instagram.com/reel với https"""
        url, platform = parse_url("https://www.instagram.com/reel/DEF456ghi")
        assert platform == Platform.INSTAGRAM
        assert "instagram.com/reel/DEF456ghi" in url
    
    def test_instagram_reel_url_no_www(self):
        """Test: Nhận diện URL instagram.com/reel không có www"""
        url, platform = parse_url("https://instagram.com/reel/reel123")
        assert platform == Platform.INSTAGRAM
        assert "instagram.com/reel/reel123" in url
    
    def test_instagram_url_in_text(self):
        """Test: Trích xuất URL Instagram từ text dài"""
        text = "Check this reel: https://instagram.com/reel/cool123 so funny!"
        url, platform = parse_url(text)
        assert platform == Platform.INSTAGRAM
        assert "instagram.com/reel/cool123" in url


class TestParseUrlUnknown:
    """Tests cho URL không được hỗ trợ - Requirements: 2.4, 2.5"""
    
    def test_unsupported_platform_tiktok(self):
        """Test: URL TikTok trả về UNKNOWN"""
        url, platform = parse_url("https://www.tiktok.com/@user/video/123456")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_unsupported_platform_twitter(self):
        """Test: URL Twitter/X trả về UNKNOWN"""
        url, platform = parse_url("https://twitter.com/user/status/123456")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_unsupported_platform_vimeo(self):
        """Test: URL Vimeo trả về UNKNOWN"""
        url, platform = parse_url("https://vimeo.com/123456789")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_no_url_in_text(self):
        """Test: Text không chứa URL trả về UNKNOWN"""
        url, platform = parse_url("Hello world, this is just text!")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_empty_string(self):
        """Test: Chuỗi rỗng trả về UNKNOWN"""
        url, platform = parse_url("")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_only_whitespace(self):
        """Test: Chuỗi chỉ có whitespace trả về UNKNOWN"""
        url, platform = parse_url("   \n\t  ")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_partial_youtube_url(self):
        """Test: URL YouTube không đầy đủ trả về UNKNOWN"""
        url, platform = parse_url("youtube.com")
        assert platform == Platform.UNKNOWN
        assert url is None
    
    def test_partial_facebook_url(self):
        """Test: URL Facebook không đầy đủ trả về UNKNOWN"""
        url, platform = parse_url("facebook.com/user")
        assert platform == Platform.UNKNOWN
        assert url is None


class TestIsSupportedPlatform:
    """Tests cho hàm is_supported_platform - Requirements: 2.4"""
    
    def test_youtube_is_supported(self):
        """Test: YouTube là platform được hỗ trợ"""
        assert is_supported_platform(Platform.YOUTUBE) is True
    
    def test_facebook_is_supported(self):
        """Test: Facebook là platform được hỗ trợ"""
        assert is_supported_platform(Platform.FACEBOOK) is True
    
    def test_instagram_is_supported(self):
        """Test: Instagram là platform được hỗ trợ"""
        assert is_supported_platform(Platform.INSTAGRAM) is True
    
    def test_unknown_is_not_supported(self):
        """Test: UNKNOWN không phải platform được hỗ trợ"""
        assert is_supported_platform(Platform.UNKNOWN) is False


class TestPlatformPatterns:
    """Tests cho PLATFORM_PATTERNS constant"""
    
    def test_all_supported_platforms_have_patterns(self):
        """Test: Tất cả platform được hỗ trợ đều có patterns"""
        assert Platform.YOUTUBE in PLATFORM_PATTERNS
        assert Platform.FACEBOOK in PLATFORM_PATTERNS
        assert Platform.INSTAGRAM in PLATFORM_PATTERNS
    
    def test_unknown_platform_has_no_patterns(self):
        """Test: Platform UNKNOWN không có patterns"""
        assert Platform.UNKNOWN not in PLATFORM_PATTERNS
    
    def test_youtube_has_multiple_patterns(self):
        """Test: YouTube có nhiều patterns (youtube.com và youtu.be)"""
        assert len(PLATFORM_PATTERNS[Platform.YOUTUBE]) >= 2
    
    def test_facebook_has_multiple_patterns(self):
        """Test: Facebook có nhiều patterns (facebook.com và fb.watch)"""
        assert len(PLATFORM_PATTERNS[Platform.FACEBOOK]) >= 2
    
    def test_instagram_has_patterns(self):
        """Test: Instagram có ít nhất 1 pattern"""
        assert len(PLATFORM_PATTERNS[Platform.INSTAGRAM]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
