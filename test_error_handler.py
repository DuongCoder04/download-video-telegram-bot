#!/usr/bin/env python3
"""
Unit Tests for Error Handler Module

Tests cho các hàm xử lý và mapping lỗi trong error_handler.py.

Requirements: 6.1, 6.2, 6.3, 6.4
"""

import pytest
from error_handler import (
    map_ytdlp_error,
    _is_video_not_found_error,
    _is_access_denied_error,
    _is_network_error,
    _is_ytdlp_update_error,
    get_error_message,
    get_user_friendly_error,
    log_error
)
from models import DownloadError


class TestMapYtdlpErrorVideoNotFound:
    """
    Tests cho mapping lỗi video không tồn tại - Requirement 6.1
    
    IF video không tồn tại hoặc đã bị xóa 
    THEN Bot SHALL thông báo "Video không tồn tại hoặc đã bị xóa"
    """
    
    def test_video_unavailable_error(self):
        """Test: Lỗi 'video unavailable' được map sang VIDEO_NOT_FOUND"""
        error = Exception("Video unavailable")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_not_found_error(self):
        """Test: Lỗi 'not found' được map sang VIDEO_NOT_FOUND"""
        error = Exception("Video not found")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_does_not_exist_error(self):
        """Test: Lỗi 'does not exist' được map sang VIDEO_NOT_FOUND"""
        error = Exception("This video does not exist")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND

    def test_has_been_removed_error(self):
        """Test: Lỗi 'has been removed' được map sang VIDEO_NOT_FOUND"""
        error = Exception("This video has been removed by the user")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_deleted_error(self):
        """Test: Lỗi 'deleted' được map sang VIDEO_NOT_FOUND"""
        error = Exception("Video has been deleted")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_unavailable_error(self):
        """Test: Lỗi 'unavailable' được map sang VIDEO_NOT_FOUND"""
        error = Exception("Content unavailable in your region")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_no_video_error(self):
        """Test: Lỗi 'no video' được map sang VIDEO_NOT_FOUND"""
        error = Exception("No video found at this URL")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_404_error(self):
        """Test: Lỗi '404' được map sang VIDEO_NOT_FOUND"""
        error = Exception("HTTP Error 404: Not Found")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_video_unavailable_case_insensitive(self):
        """Test: Lỗi 'VIDEO UNAVAILABLE' (uppercase) được map sang VIDEO_NOT_FOUND"""
        error = Exception("VIDEO UNAVAILABLE")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND


class TestMapYtdlpErrorAccessDenied:
    """
    Tests cho mapping lỗi video bị giới hạn quyền truy cập - Requirement 6.2
    
    IF video bị giới hạn quyền truy cập 
    THEN Bot SHALL thông báo "Video bị giới hạn, không thể tải"
    """
    
    def test_private_video_error(self):
        """Test: Lỗi 'private' được map sang ACCESS_DENIED"""
        error = Exception("This video is private")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_restricted_error(self):
        """Test: Lỗi 'restricted' được map sang ACCESS_DENIED"""
        error = Exception("Video is restricted")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_age_restricted_hyphen_error(self):
        """Test: Lỗi 'age-restricted' được map sang ACCESS_DENIED"""
        error = Exception("This video is age-restricted")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_age_restricted_space_error(self):
        """Test: Lỗi 'age restricted' được map sang ACCESS_DENIED"""
        error = Exception("This video is age restricted")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED

    def test_login_required_error(self):
        """Test: Lỗi 'login required' được map sang ACCESS_DENIED"""
        error = Exception("Login required to view this video")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_sign_in_error(self):
        """Test: Lỗi 'sign in' được map sang ACCESS_DENIED"""
        error = Exception("Please sign in to view this content")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_members_only_error(self):
        """Test: Lỗi 'members only' được map sang ACCESS_DENIED"""
        error = Exception("This video is for members only")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_subscribers_only_error(self):
        """Test: Lỗi 'subscribers only' được map sang ACCESS_DENIED"""
        error = Exception("This content is for subscribers only")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_permission_denied_error(self):
        """Test: Lỗi 'permission denied' được map sang ACCESS_DENIED"""
        error = Exception("Permission denied")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_access_denied_error(self):
        """Test: Lỗi 'access denied' được map sang ACCESS_DENIED"""
        error = Exception("Access denied to this resource")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_forbidden_error(self):
        """Test: Lỗi 'forbidden' được map sang ACCESS_DENIED"""
        error = Exception("Forbidden: You don't have access")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED
    
    def test_403_error(self):
        """Test: Lỗi '403' được map sang ACCESS_DENIED"""
        error = Exception("HTTP Error 403: Forbidden")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED


class TestMapYtdlpErrorNetworkError:
    """
    Tests cho mapping lỗi kết nối mạng - Requirement 6.3
    
    IF kết nối mạng bị gián đoạn 
    THEN Bot SHALL thông báo lỗi và gợi ý thử lại sau
    """
    
    def test_network_error(self):
        """Test: Lỗi 'network' được map sang NETWORK_ERROR"""
        error = Exception("Network error occurred")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_connection_error(self):
        """Test: Lỗi 'connection' được map sang NETWORK_ERROR"""
        error = Exception("Connection error")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR

    def test_timeout_error(self):
        """Test: Lỗi 'timeout' được map sang NETWORK_ERROR"""
        error = Exception("Request timeout")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_timed_out_error(self):
        """Test: Lỗi 'timed out' được map sang NETWORK_ERROR"""
        error = Exception("Connection timed out")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_unreachable_error(self):
        """Test: Lỗi 'unreachable' được map sang NETWORK_ERROR"""
        error = Exception("Host unreachable")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_dns_error(self):
        """Test: Lỗi 'dns' được map sang NETWORK_ERROR"""
        error = Exception("DNS resolution failed")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_socket_error(self):
        """Test: Lỗi 'socket' được map sang NETWORK_ERROR"""
        error = Exception("Socket error")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_ssl_error(self):
        """Test: Lỗi 'ssl' được map sang NETWORK_ERROR"""
        error = Exception("SSL handshake failed")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_certificate_error(self):
        """Test: Lỗi 'certificate' được map sang NETWORK_ERROR"""
        error = Exception("Certificate verification failed")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_connect_error(self):
        """Test: Lỗi 'connect error' được map sang NETWORK_ERROR"""
        error = Exception("Connect error: Unable to connect")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_connection_refused_error(self):
        """Test: Lỗi 'connection refused' được map sang NETWORK_ERROR"""
        error = Exception("Connection refused by server")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_connection_reset_error(self):
        """Test: Lỗi 'connection reset' được map sang NETWORK_ERROR"""
        error = Exception("Connection reset by peer")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR
    
    def test_no_internet_error(self):
        """Test: Lỗi 'no internet' được map sang NETWORK_ERROR"""
        error = Exception("No internet connection")
        result = map_ytdlp_error(error)
        assert result == DownloadError.NETWORK_ERROR


class TestMapYtdlpErrorYtdlpUpdate:
    """
    Tests cho mapping lỗi yt-dlp cần cập nhật - Requirement 6.4
    
    IF yt-dlp cần cập nhật 
    THEN Bot SHALL thông báo "Cần cập nhật yt-dlp, vui lòng liên hệ admin"
    """
    
    def test_update_error(self):
        """Test: Lỗi 'update' được map sang YTDLP_ERROR"""
        error = Exception("Please update yt-dlp")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR
    
    def test_outdated_error(self):
        """Test: Lỗi 'outdated' được map sang YTDLP_ERROR"""
        error = Exception("yt-dlp is outdated")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR
    
    def test_upgrade_error(self):
        """Test: Lỗi 'upgrade' được map sang YTDLP_ERROR"""
        error = Exception("Please upgrade yt-dlp to the latest version")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR
    
    def test_new_version_error(self):
        """Test: Lỗi 'new version' được map sang YTDLP_ERROR"""
        error = Exception("A new version of yt-dlp is available")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR
    
    def test_please_update_error(self):
        """Test: Lỗi 'please update' được map sang YTDLP_ERROR"""
        error = Exception("Please update your yt-dlp installation")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR
    
    def test_ytdlp_needs_error(self):
        """Test: Lỗi 'yt-dlp needs' được map sang YTDLP_ERROR"""
        error = Exception("yt-dlp needs to be updated")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR
    
    def test_extractor_error(self):
        """Test: Lỗi 'extractor error' được map sang YTDLP_ERROR"""
        error = Exception("Extractor error: Unable to extract video info")
        result = map_ytdlp_error(error)
        assert result == DownloadError.YTDLP_ERROR


class TestMapYtdlpErrorUnknown:
    """Tests cho mapping lỗi không xác định - Fallback case"""
    
    def test_unknown_error_generic(self):
        """Test: Lỗi không khớp với bất kỳ pattern nào được map sang UNKNOWN_ERROR"""
        error = Exception("Some random error message")
        result = map_ytdlp_error(error)
        assert result == DownloadError.UNKNOWN_ERROR
    
    def test_unknown_error_empty_message(self):
        """Test: Lỗi với message rỗng được map sang UNKNOWN_ERROR"""
        error = Exception("")
        result = map_ytdlp_error(error)
        assert result == DownloadError.UNKNOWN_ERROR
    
    def test_unknown_error_special_characters(self):
        """Test: Lỗi với ký tự đặc biệt được map sang UNKNOWN_ERROR"""
        error = Exception("!@#$%^&*()")
        result = map_ytdlp_error(error)
        assert result == DownloadError.UNKNOWN_ERROR
    
    def test_unknown_error_numbers_only(self):
        """Test: Lỗi chỉ có số (không phải 404/403) được map sang UNKNOWN_ERROR"""
        error = Exception("12345")
        result = map_ytdlp_error(error)
        assert result == DownloadError.UNKNOWN_ERROR


class TestIsVideoNotFoundError:
    """Tests cho helper function _is_video_not_found_error"""
    
    def test_video_unavailable_returns_true(self):
        """Test: 'video unavailable' trả về True"""
        assert _is_video_not_found_error("video unavailable") is True
    
    def test_not_found_returns_true(self):
        """Test: 'not found' trả về True"""
        assert _is_video_not_found_error("not found") is True
    
    def test_does_not_exist_returns_true(self):
        """Test: 'does not exist' trả về True"""
        assert _is_video_not_found_error("does not exist") is True
    
    def test_has_been_removed_returns_true(self):
        """Test: 'has been removed' trả về True"""
        assert _is_video_not_found_error("has been removed") is True
    
    def test_deleted_returns_true(self):
        """Test: 'deleted' trả về True"""
        assert _is_video_not_found_error("deleted") is True
    
    def test_unavailable_returns_true(self):
        """Test: 'unavailable' trả về True"""
        assert _is_video_not_found_error("unavailable") is True
    
    def test_no_video_returns_true(self):
        """Test: 'no video' trả về True"""
        assert _is_video_not_found_error("no video") is True
    
    def test_404_returns_true(self):
        """Test: '404' trả về True"""
        assert _is_video_not_found_error("404") is True
    
    def test_unrelated_error_returns_false(self):
        """Test: Lỗi không liên quan trả về False"""
        assert _is_video_not_found_error("some other error") is False
    
    def test_empty_string_returns_false(self):
        """Test: Chuỗi rỗng trả về False"""
        assert _is_video_not_found_error("") is False


class TestIsAccessDeniedError:
    """Tests cho helper function _is_access_denied_error"""
    
    def test_private_returns_true(self):
        """Test: 'private' trả về True"""
        assert _is_access_denied_error("private") is True
    
    def test_restricted_returns_true(self):
        """Test: 'restricted' trả về True"""
        assert _is_access_denied_error("restricted") is True
    
    def test_age_restricted_hyphen_returns_true(self):
        """Test: 'age-restricted' trả về True"""
        assert _is_access_denied_error("age-restricted") is True
    
    def test_login_required_returns_true(self):
        """Test: 'login required' trả về True"""
        assert _is_access_denied_error("login required") is True
    
    def test_sign_in_returns_true(self):
        """Test: 'sign in' trả về True"""
        assert _is_access_denied_error("sign in") is True
    
    def test_members_only_returns_true(self):
        """Test: 'members only' trả về True"""
        assert _is_access_denied_error("members only") is True
    
    def test_forbidden_returns_true(self):
        """Test: 'forbidden' trả về True"""
        assert _is_access_denied_error("forbidden") is True
    
    def test_403_returns_true(self):
        """Test: '403' trả về True"""
        assert _is_access_denied_error("403") is True
    
    def test_unrelated_error_returns_false(self):
        """Test: Lỗi không liên quan trả về False"""
        assert _is_access_denied_error("some other error") is False


class TestIsNetworkError:
    """Tests cho helper function _is_network_error"""
    
    def test_network_returns_true(self):
        """Test: 'network' trả về True"""
        assert _is_network_error("network") is True
    
    def test_connection_returns_true(self):
        """Test: 'connection' trả về True"""
        assert _is_network_error("connection") is True
    
    def test_timeout_returns_true(self):
        """Test: 'timeout' trả về True"""
        assert _is_network_error("timeout") is True
    
    def test_timed_out_returns_true(self):
        """Test: 'timed out' trả về True"""
        assert _is_network_error("timed out") is True
    
    def test_unreachable_returns_true(self):
        """Test: 'unreachable' trả về True"""
        assert _is_network_error("unreachable") is True
    
    def test_dns_returns_true(self):
        """Test: 'dns' trả về True"""
        assert _is_network_error("dns") is True
    
    def test_socket_returns_true(self):
        """Test: 'socket' trả về True"""
        assert _is_network_error("socket") is True
    
    def test_ssl_returns_true(self):
        """Test: 'ssl' trả về True"""
        assert _is_network_error("ssl") is True
    
    def test_certificate_returns_true(self):
        """Test: 'certificate' trả về True"""
        assert _is_network_error("certificate") is True
    
    def test_no_internet_returns_true(self):
        """Test: 'no internet' trả về True"""
        assert _is_network_error("no internet") is True
    
    def test_unrelated_error_returns_false(self):
        """Test: Lỗi không liên quan trả về False"""
        assert _is_network_error("some other error") is False


class TestIsYtdlpUpdateError:
    """Tests cho helper function _is_ytdlp_update_error"""
    
    def test_update_returns_true(self):
        """Test: 'update' trả về True"""
        assert _is_ytdlp_update_error("update") is True
    
    def test_outdated_returns_true(self):
        """Test: 'outdated' trả về True"""
        assert _is_ytdlp_update_error("outdated") is True
    
    def test_upgrade_returns_true(self):
        """Test: 'upgrade' trả về True"""
        assert _is_ytdlp_update_error("upgrade") is True
    
    def test_new_version_returns_true(self):
        """Test: 'new version' trả về True"""
        assert _is_ytdlp_update_error("new version") is True
    
    def test_please_update_returns_true(self):
        """Test: 'please update' trả về True"""
        assert _is_ytdlp_update_error("please update") is True
    
    def test_ytdlp_needs_returns_true(self):
        """Test: 'yt-dlp needs' trả về True"""
        assert _is_ytdlp_update_error("yt-dlp needs") is True
    
    def test_extractor_error_returns_true(self):
        """Test: 'extractor error' trả về True"""
        assert _is_ytdlp_update_error("extractor error") is True
    
    def test_unrelated_error_returns_false(self):
        """Test: Lỗi không liên quan trả về False"""
        assert _is_ytdlp_update_error("some other error") is False


class TestGetErrorMessage:
    """
    Tests cho hàm get_error_message
    
    Kiểm tra việc lấy thông báo lỗi tiếng Việt từ DownloadError enum.
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def test_video_not_found_message(self):
        """Test: VIDEO_NOT_FOUND trả về thông báo tiếng Việt đúng - Requirement 6.1"""
        message = get_error_message(DownloadError.VIDEO_NOT_FOUND)
        assert message == "Video không tồn tại hoặc đã bị xóa"
    
    def test_access_denied_message(self):
        """Test: ACCESS_DENIED trả về thông báo tiếng Việt đúng - Requirement 6.2"""
        message = get_error_message(DownloadError.ACCESS_DENIED)
        assert message == "Video bị giới hạn, không thể tải"
    
    def test_network_error_message(self):
        """Test: NETWORK_ERROR trả về thông báo tiếng Việt đúng - Requirement 6.3"""
        message = get_error_message(DownloadError.NETWORK_ERROR)
        assert message == "Lỗi kết nối mạng, vui lòng thử lại sau"
    
    def test_ytdlp_error_message(self):
        """Test: YTDLP_ERROR trả về thông báo tiếng Việt đúng - Requirement 6.4"""
        message = get_error_message(DownloadError.YTDLP_ERROR)
        assert message == "Lỗi yt-dlp, có thể cần cập nhật"
    
    def test_file_too_large_message(self):
        """Test: FILE_TOO_LARGE trả về thông báo tiếng Việt đúng"""
        message = get_error_message(DownloadError.FILE_TOO_LARGE)
        assert message == "Video quá lớn (>50MB), không thể gửi qua Telegram"
    
    def test_unknown_error_message(self):
        """Test: UNKNOWN_ERROR trả về thông báo tiếng Việt đúng"""
        message = get_error_message(DownloadError.UNKNOWN_ERROR)
        assert message == "Lỗi không xác định"


class TestGetUserFriendlyError:
    """
    Tests cho hàm get_user_friendly_error
    
    Kiểm tra việc chuyển đổi Exception thành thông báo lỗi thân thiện.
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def test_video_not_found_friendly_error(self):
        """Test: Exception 'video unavailable' trả về thông báo thân thiện - Requirement 6.1"""
        error = Exception("Video unavailable")
        message = get_user_friendly_error(error)
        assert message == "Video không tồn tại hoặc đã bị xóa"
    
    def test_access_denied_friendly_error(self):
        """Test: Exception 'private video' trả về thông báo thân thiện - Requirement 6.2"""
        error = Exception("This video is private")
        message = get_user_friendly_error(error)
        assert message == "Video bị giới hạn, không thể tải"
    
    def test_network_error_friendly_error(self):
        """Test: Exception 'connection error' trả về thông báo thân thiện - Requirement 6.3"""
        error = Exception("Connection error occurred")
        message = get_user_friendly_error(error)
        assert message == "Lỗi kết nối mạng, vui lòng thử lại sau"
    
    def test_ytdlp_update_friendly_error(self):
        """Test: Exception 'please update' trả về thông báo thân thiện - Requirement 6.4"""
        error = Exception("Please update yt-dlp")
        message = get_user_friendly_error(error)
        assert message == "Lỗi yt-dlp, có thể cần cập nhật"
    
    def test_unknown_friendly_error(self):
        """Test: Exception không xác định trả về thông báo thân thiện"""
        error = Exception("Some random error")
        message = get_user_friendly_error(error)
        assert message == "Lỗi không xác định"


class TestErrorPriority:
    """
    Tests cho thứ tự ưu tiên khi mapping lỗi
    
    Kiểm tra rằng khi một lỗi có thể khớp với nhiều pattern,
    pattern đầu tiên được ưu tiên.
    """
    
    def test_video_not_found_priority_over_network(self):
        """Test: 'video unavailable' ưu tiên hơn 'network' nếu cả hai xuất hiện"""
        # VIDEO_NOT_FOUND được kiểm tra trước NETWORK_ERROR
        error = Exception("Video unavailable due to network issues")
        result = map_ytdlp_error(error)
        assert result == DownloadError.VIDEO_NOT_FOUND
    
    def test_access_denied_priority_over_update(self):
        """Test: 'private' ưu tiên hơn 'update' nếu cả hai xuất hiện"""
        # ACCESS_DENIED được kiểm tra trước YTDLP_ERROR
        error = Exception("Private video, please update your subscription")
        result = map_ytdlp_error(error)
        assert result == DownloadError.ACCESS_DENIED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
