#!/usr/bin/env python3
"""
Property-Based Tests for URL Parser Module

Property tests sử dụng Hypothesis để kiểm tra URL Platform Detection.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: URL Platform Detection
*For any* URL text, hàm `parse_url(text)` phải:
- Trả về `(url, Platform.YOUTUBE)` nếu URL chứa "youtube.com" hoặc "youtu.be"
- Trả về `(url, Platform.FACEBOOK)` nếu URL chứa "facebook.com" hoặc "fb.watch"
- Trả về `(url, Platform.INSTAGRAM)` nếu URL chứa "instagram.com"
- Trả về `(None, Platform.UNKNOWN)` cho các URL không thuộc các platform trên
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from url_parser import parse_url
from models import Platform


# =============================================================================
# Custom Strategies for URL Generation
# =============================================================================

# Strategy for generating valid video IDs (alphanumeric with dashes)
video_id_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
    min_size=1,
    max_size=20
)

# Strategy for numeric IDs (for Facebook video IDs)
numeric_id_strategy = st.integers(min_value=1, max_value=10**18).map(str)

# Strategy for username/page names
username_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._",
    min_size=1,
    max_size=30
)

# Strategy for optional protocol
protocol_strategy = st.sampled_from(["https://", "http://", ""])

# Strategy for optional www prefix
www_strategy = st.sampled_from(["www.", ""])


# =============================================================================
# YouTube URL Strategies
# =============================================================================

@st.composite
def youtube_watch_url_strategy(draw):
    """Generate valid YouTube watch URLs: youtube.com/watch?v={video_id}"""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    video_id = draw(video_id_strategy)
    assume(len(video_id) > 0)  # Ensure video_id is not empty
    return f"{protocol}{www}youtube.com/watch?v={video_id}"


@st.composite
def youtube_short_url_strategy(draw):
    """Generate valid YouTube short URLs: youtu.be/{video_id}"""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    video_id = draw(video_id_strategy)
    assume(len(video_id) > 0)  # Ensure video_id is not empty
    return f"{protocol}{www}youtu.be/{video_id}"


youtube_url_strategy = st.one_of(
    youtube_watch_url_strategy(),
    youtube_short_url_strategy()
)


# =============================================================================
# Facebook URL Strategies
# =============================================================================

@st.composite
def facebook_videos_url_strategy(draw):
    """Generate valid Facebook video URLs: facebook.com/{user}/videos/{numeric_id}"""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    username = draw(username_strategy)
    video_id = draw(numeric_id_strategy)
    assume(len(username) > 0)  # Ensure username is not empty
    return f"{protocol}{www}facebook.com/{username}/videos/{video_id}"


@st.composite
def fb_watch_url_strategy(draw):
    """Generate valid fb.watch URLs: fb.watch/{id}"""
    protocol = draw(protocol_strategy)
    video_id = draw(video_id_strategy)
    assume(len(video_id) > 0)  # Ensure video_id is not empty
    return f"{protocol}fb.watch/{video_id}"


facebook_url_strategy = st.one_of(
    facebook_videos_url_strategy(),
    fb_watch_url_strategy()
)


# =============================================================================
# Instagram URL Strategies
# =============================================================================

@st.composite
def instagram_post_url_strategy(draw):
    """Generate valid Instagram post URLs: instagram.com/p/{post_id}"""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    post_id = draw(video_id_strategy)
    assume(len(post_id) > 0)  # Ensure post_id is not empty
    return f"{protocol}{www}instagram.com/p/{post_id}"


@st.composite
def instagram_reel_url_strategy(draw):
    """Generate valid Instagram reel URLs: instagram.com/reel/{reel_id}"""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    reel_id = draw(video_id_strategy)
    assume(len(reel_id) > 0)  # Ensure reel_id is not empty
    return f"{protocol}{www}instagram.com/reel/{reel_id}"


instagram_url_strategy = st.one_of(
    instagram_post_url_strategy(),
    instagram_reel_url_strategy()
)


# =============================================================================
# Unknown/Unsupported URL Strategies
# =============================================================================

# List of domains that should NOT be recognized
unsupported_domains = [
    "tiktok.com",
    "twitter.com",
    "x.com",
    "vimeo.com",
    "dailymotion.com",
    "twitch.tv",
    "reddit.com",
    "linkedin.com",
]


@st.composite
def unsupported_url_strategy(draw):
    """Generate URLs from unsupported platforms"""
    protocol = draw(protocol_strategy)
    www = draw(www_strategy)
    domain = draw(st.sampled_from(unsupported_domains))
    path = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789/",
        min_size=1,
        max_size=30
    ))
    return f"{protocol}{www}{domain}/{path}"


@st.composite
def random_non_url_text_strategy(draw):
    """Generate random text that doesn't contain any supported platform URLs"""
    # Generate text that explicitly avoids platform keywords
    text = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789 .,!?",
        min_size=0,
        max_size=100
    ))
    # Ensure the text doesn't accidentally contain platform patterns
    assume("youtube" not in text.lower())
    assume("youtu.be" not in text.lower())
    assume("facebook" not in text.lower())
    assume("fb.watch" not in text.lower())
    assume("instagram" not in text.lower())
    return text


# =============================================================================
# Property Tests - Property 2: URL Platform Detection
# **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
# =============================================================================

class TestURLPlatformDetectionProperty:
    """
    Property 2: URL Platform Detection
    
    *For any* URL text, hàm `parse_url(text)` phải:
    - Trả về `(url, Platform.YOUTUBE)` nếu URL chứa "youtube.com" hoặc "youtu.be"
    - Trả về `(url, Platform.FACEBOOK)` nếu URL chứa "facebook.com" hoặc "fb.watch"
    - Trả về `(url, Platform.INSTAGRAM)` nếu URL chứa "instagram.com"
    - Trả về `(None, Platform.UNKNOWN)` cho các URL không thuộc các platform trên
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    
    @given(url=youtube_url_strategy)
    @settings(max_examples=100)
    def test_youtube_urls_detected_as_youtube(self, url: str):
        """
        Property: Any valid YouTube URL should be detected as Platform.YOUTUBE
        
        **Validates: Requirements 2.1**
        
        For any URL containing "youtube.com" or "youtu.be" with valid video ID,
        parse_url should return (url, Platform.YOUTUBE)
        """
        extracted_url, platform = parse_url(url)
        
        assert platform == Platform.YOUTUBE, (
            f"Expected Platform.YOUTUBE for URL '{url}', got {platform}"
        )
        assert extracted_url is not None, (
            f"Expected non-None URL for YouTube URL '{url}'"
        )
        # Verify the extracted URL contains the expected domain
        assert "youtube.com" in extracted_url or "youtu.be" in extracted_url, (
            f"Extracted URL '{extracted_url}' should contain youtube.com or youtu.be"
        )
    
    @given(url=facebook_url_strategy)
    @settings(max_examples=100)
    def test_facebook_urls_detected_as_facebook(self, url: str):
        """
        Property: Any valid Facebook URL should be detected as Platform.FACEBOOK
        
        **Validates: Requirements 2.2**
        
        For any URL containing "facebook.com" or "fb.watch" with valid video ID,
        parse_url should return (url, Platform.FACEBOOK)
        """
        extracted_url, platform = parse_url(url)
        
        assert platform == Platform.FACEBOOK, (
            f"Expected Platform.FACEBOOK for URL '{url}', got {platform}"
        )
        assert extracted_url is not None, (
            f"Expected non-None URL for Facebook URL '{url}'"
        )
        # Verify the extracted URL contains the expected domain
        assert "facebook.com" in extracted_url or "fb.watch" in extracted_url, (
            f"Extracted URL '{extracted_url}' should contain facebook.com or fb.watch"
        )
    
    @given(url=instagram_url_strategy)
    @settings(max_examples=100)
    def test_instagram_urls_detected_as_instagram(self, url: str):
        """
        Property: Any valid Instagram URL should be detected as Platform.INSTAGRAM
        
        **Validates: Requirements 2.3**
        
        For any URL containing "instagram.com" with valid post/reel ID,
        parse_url should return (url, Platform.INSTAGRAM)
        """
        extracted_url, platform = parse_url(url)
        
        assert platform == Platform.INSTAGRAM, (
            f"Expected Platform.INSTAGRAM for URL '{url}', got {platform}"
        )
        assert extracted_url is not None, (
            f"Expected non-None URL for Instagram URL '{url}'"
        )
        # Verify the extracted URL contains the expected domain
        assert "instagram.com" in extracted_url, (
            f"Extracted URL '{extracted_url}' should contain instagram.com"
        )
    
    @given(text=random_non_url_text_strategy())
    @settings(max_examples=100)
    def test_non_platform_text_returns_unknown(self, text: str):
        """
        Property: Text without supported platform URLs should return Platform.UNKNOWN
        
        **Validates: Requirements 2.4**
        
        For any text that doesn't contain youtube.com, youtu.be, facebook.com,
        fb.watch, or instagram.com patterns, parse_url should return (None, Platform.UNKNOWN)
        """
        extracted_url, platform = parse_url(text)
        
        assert platform == Platform.UNKNOWN, (
            f"Expected Platform.UNKNOWN for text '{text}', got {platform}"
        )
        assert extracted_url is None, (
            f"Expected None URL for non-platform text '{text}', got '{extracted_url}'"
        )
    
    @given(url=unsupported_url_strategy())
    @settings(max_examples=100)
    def test_unsupported_platform_urls_return_unknown(self, url: str):
        """
        Property: URLs from unsupported platforms should return Platform.UNKNOWN
        
        **Validates: Requirements 2.4**
        
        For any URL from platforms like TikTok, Twitter, Vimeo, etc.,
        parse_url should return (None, Platform.UNKNOWN)
        """
        extracted_url, platform = parse_url(url)
        
        assert platform == Platform.UNKNOWN, (
            f"Expected Platform.UNKNOWN for unsupported URL '{url}', got {platform}"
        )
        assert extracted_url is None, (
            f"Expected None URL for unsupported platform URL '{url}', got '{extracted_url}'"
        )


class TestURLExtractionFromText:
    """
    Additional property tests for URL extraction from mixed text.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    
    @given(
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=20),
        url=youtube_url_strategy,
        suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=20)
    )
    @settings(max_examples=50)
    def test_youtube_url_extracted_from_text(self, prefix: str, url: str, suffix: str):
        """
        Property: YouTube URLs should be extracted from surrounding text
        
        **Validates: Requirements 2.1**
        """
        text = f"{prefix} {url} {suffix}"
        extracted_url, platform = parse_url(text)
        
        assert platform == Platform.YOUTUBE, (
            f"Expected Platform.YOUTUBE for text containing YouTube URL"
        )
        assert extracted_url is not None
    
    @given(
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=20),
        url=facebook_url_strategy,
        suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=20)
    )
    @settings(max_examples=50)
    def test_facebook_url_extracted_from_text(self, prefix: str, url: str, suffix: str):
        """
        Property: Facebook URLs should be extracted from surrounding text
        
        **Validates: Requirements 2.2**
        """
        text = f"{prefix} {url} {suffix}"
        extracted_url, platform = parse_url(text)
        
        assert platform == Platform.FACEBOOK, (
            f"Expected Platform.FACEBOOK for text containing Facebook URL"
        )
        assert extracted_url is not None
    
    @given(
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=20),
        url=instagram_url_strategy,
        suffix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=20)
    )
    @settings(max_examples=50)
    def test_instagram_url_extracted_from_text(self, prefix: str, url: str, suffix: str):
        """
        Property: Instagram URLs should be extracted from surrounding text
        
        **Validates: Requirements 2.3**
        """
        text = f"{prefix} {url} {suffix}"
        extracted_url, platform = parse_url(text)
        
        assert platform == Platform.INSTAGRAM, (
            f"Expected Platform.INSTAGRAM for text containing Instagram URL"
        )
        assert extracted_url is not None


class TestPlatformDetectionConsistency:
    """
    Property tests for consistency of platform detection.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    """
    
    @given(url=youtube_url_strategy)
    @settings(max_examples=50)
    def test_youtube_detection_is_idempotent(self, url: str):
        """
        Property: Calling parse_url multiple times on same URL gives same result
        
        **Validates: Requirements 2.1**
        """
        result1 = parse_url(url)
        result2 = parse_url(url)
        
        assert result1 == result2, (
            f"parse_url should be idempotent: {result1} != {result2}"
        )
    
    @given(url=facebook_url_strategy)
    @settings(max_examples=50)
    def test_facebook_detection_is_idempotent(self, url: str):
        """
        Property: Calling parse_url multiple times on same URL gives same result
        
        **Validates: Requirements 2.2**
        """
        result1 = parse_url(url)
        result2 = parse_url(url)
        
        assert result1 == result2, (
            f"parse_url should be idempotent: {result1} != {result2}"
        )
    
    @given(url=instagram_url_strategy)
    @settings(max_examples=50)
    def test_instagram_detection_is_idempotent(self, url: str):
        """
        Property: Calling parse_url multiple times on same URL gives same result
        
        **Validates: Requirements 2.3**
        """
        result1 = parse_url(url)
        result2 = parse_url(url)
        
        assert result1 == result2, (
            f"parse_url should be idempotent: {result1} != {result2}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
