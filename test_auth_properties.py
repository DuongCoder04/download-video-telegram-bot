#!/usr/bin/env python3
"""
Property-Based Tests for Auth Module

Property tests sử dụng Hypothesis để kiểm tra tính đúng đắn của
hàm is_authorized trong mọi trường hợp.

**Validates: Requirements 1.1, 1.2**

Feature: telegram-video-downloader-bot, Property 1: Authorization Check
"""

from hypothesis import given, strategies as st, settings
from auth import is_authorized


class TestAuthorizationProperty:
    """
    Property 1: Authorization Check
    
    *For any* user_id và owner_id, hàm `is_authorized(user_id, owner_id)` 
    trả về `True` khi và chỉ khi `user_id == owner_id`.
    
    **Validates: Requirements 1.1, 1.2**
    """
    
    @given(
        user_id=st.integers(),
        owner_id=st.integers()
    )
    @settings(max_examples=200)
    def test_authorization_returns_true_iff_ids_match(
        self, user_id: int, owner_id: int
    ) -> None:
        """
        Property: is_authorized(user_id, owner_id) == (user_id == owner_id)
        
        Kiểm tra rằng hàm is_authorized trả về True khi và chỉ khi
        user_id bằng owner_id.
        
        **Validates: Requirements 1.1, 1.2**
        """
        result = is_authorized(user_id, owner_id)
        expected = user_id == owner_id
        
        assert result == expected, (
            f"is_authorized({user_id}, {owner_id}) returned {result}, "
            f"expected {expected}"
        )
    
    @given(user_id=st.integers())
    @settings(max_examples=100)
    def test_same_id_always_authorized(self, user_id: int) -> None:
        """
        Property: For any user_id, is_authorized(user_id, user_id) == True
        
        Kiểm tra rằng khi user_id và owner_id giống nhau, 
        kết quả luôn là True.
        
        **Validates: Requirements 1.2**
        """
        result = is_authorized(user_id, user_id)
        
        assert result is True, (
            f"is_authorized({user_id}, {user_id}) should return True, "
            f"but returned {result}"
        )
    
    @given(
        user_id=st.integers(),
        owner_id=st.integers().filter(lambda x: True)  # Will filter in test
    )
    @settings(max_examples=100)
    def test_different_ids_never_authorized(
        self, user_id: int, owner_id: int
    ) -> None:
        """
        Property: For any user_id != owner_id, is_authorized returns False
        
        Kiểm tra rằng khi user_id và owner_id khác nhau,
        kết quả luôn là False.
        
        **Validates: Requirements 1.1**
        """
        # Skip if IDs happen to be equal
        if user_id == owner_id:
            return
        
        result = is_authorized(user_id, owner_id)
        
        assert result is False, (
            f"is_authorized({user_id}, {owner_id}) should return False "
            f"when IDs differ, but returned {result}"
        )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
