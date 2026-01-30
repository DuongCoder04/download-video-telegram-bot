#!/usr/bin/env python3
"""
Progress Manager Module for Telegram Video Downloader Bot

Module quản lý tin nhắn tiến trình khi tải và gửi video.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


# Default progress messages (Vietnamese)
DEFAULT_MESSAGES = {
    "downloading": "Đang tải video...",
    "sending": "Đang gửi video...",
    "completed": "Hoàn tất!",
    "error": "Có lỗi xảy ra"
}


class ProgressManager:
    """
    Quản lý tin nhắn tiến trình trong Telegram.
    
    Class này cung cấp các phương thức để gửi, cập nhật và xóa
    tin nhắn tiến trình khi bot đang tải và gửi video.
    
    Attributes:
        bot: Instance của Telegram Bot để gửi tin nhắn
        
    Requirements: 5.1, 5.2, 5.3, 5.4
    
    Example:
        >>> progress = ProgressManager(bot)
        >>> msg_id = await progress.send_progress(chat_id, "Đang tải video...")
        >>> await progress.update_progress(chat_id, msg_id, "Đang tải: 50%")
        >>> await progress.delete_progress(chat_id, msg_id)
    """
    
    def __init__(self, bot):
        """
        Khởi tạo ProgressManager.
        
        Args:
            bot: Instance của Telegram Bot (python-telegram-bot)
        """
        self.bot = bot
    
    async def send_progress(self, chat_id: int, text: str) -> int:
        """
        Gửi tin nhắn tiến trình mới.
        
        Gửi một tin nhắn mới để hiển thị tiến trình và trả về message_id
        để có thể cập nhật hoặc xóa tin nhắn sau này.
        
        Args:
            chat_id: ID của chat để gửi tin nhắn
            text: Nội dung tin nhắn tiến trình
            
        Returns:
            message_id của tin nhắn đã gửi
            
        Raises:
            Exception: Nếu không thể gửi tin nhắn (lỗi Telegram API)
            
        Requirements: 5.1
        
        Example:
            >>> msg_id = await progress.send_progress(123456, "Đang tải video...")
            >>> print(msg_id)  # 42
        """
        logger.debug(f"Gửi tin nhắn tiến trình đến chat {chat_id}: {text}")
        msg = await self.bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Đã gửi tin nhắn tiến trình (message_id={msg.message_id})")
        return msg.message_id
    
    async def update_progress(
        self, 
        chat_id: int, 
        message_id: int, 
        text: str
    ) -> bool:
        """
        Cập nhật tin nhắn tiến trình đã tồn tại.
        
        Sửa đổi nội dung của tin nhắn tiến trình đã gửi trước đó.
        Thường được sử dụng để cập nhật phần trăm hoàn thành hoặc
        thay đổi trạng thái (ví dụ: từ "Đang tải" sang "Đang gửi").
        
        Args:
            chat_id: ID của chat chứa tin nhắn
            message_id: ID của tin nhắn cần cập nhật
            text: Nội dung mới của tin nhắn
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
            
        Requirements: 5.2, 5.3
        
        Example:
            >>> success = await progress.update_progress(123456, 42, "Đang tải: 75%")
            >>> print(success)  # True
        """
        try:
            logger.debug(
                f"Cập nhật tin nhắn tiến trình (chat={chat_id}, msg={message_id}): {text}"
            )
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
            logger.info(f"Đã cập nhật tin nhắn tiến trình (message_id={message_id})")
            return True
        except Exception as e:
            # Có thể xảy ra nếu tin nhắn đã bị xóa hoặc nội dung không thay đổi
            logger.warning(f"Không thể cập nhật tin nhắn tiến trình: {e}")
            return False
    
    async def delete_progress(self, chat_id: int, message_id: int) -> bool:
        """
        Xóa tin nhắn tiến trình.
        
        Xóa tin nhắn tiến trình sau khi quá trình hoàn tất.
        Giúp giữ chat sạch sẽ, không có tin nhắn tiến trình cũ.
        
        Args:
            chat_id: ID của chat chứa tin nhắn
            message_id: ID của tin nhắn cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
            
        Requirements: 5.4
        
        Example:
            >>> success = await progress.delete_progress(123456, 42)
            >>> print(success)  # True
        """
        try:
            logger.debug(f"Xóa tin nhắn tiến trình (chat={chat_id}, msg={message_id})")
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"Đã xóa tin nhắn tiến trình (message_id={message_id})")
            return True
        except Exception as e:
            # Có thể xảy ra nếu tin nhắn đã bị xóa trước đó
            logger.warning(f"Không thể xóa tin nhắn tiến trình: {e}")
            return False
    
    async def send_downloading(self, chat_id: int) -> int:
        """
        Gửi tin nhắn "Đang tải video...".
        
        Phương thức tiện ích để gửi tin nhắn bắt đầu tải video.
        
        Args:
            chat_id: ID của chat để gửi tin nhắn
            
        Returns:
            message_id của tin nhắn đã gửi
            
        Requirements: 5.1
        """
        return await self.send_progress(chat_id, DEFAULT_MESSAGES["downloading"])
    
    async def update_downloading_percent(
        self, 
        chat_id: int, 
        message_id: int, 
        percent: float
    ) -> bool:
        """
        Cập nhật tin nhắn với phần trăm hoàn thành.
        
        Phương thức tiện ích để cập nhật tiến trình tải với phần trăm.
        
        Args:
            chat_id: ID của chat chứa tin nhắn
            message_id: ID của tin nhắn cần cập nhật
            percent: Phần trăm hoàn thành (0-100)
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
            
        Requirements: 5.2
        """
        # Đảm bảo percent nằm trong khoảng 0-100
        percent = max(0, min(100, percent))
        text = f"Đang tải video... {percent:.0f}%"
        return await self.update_progress(chat_id, message_id, text)
    
    async def update_sending(self, chat_id: int, message_id: int) -> bool:
        """
        Cập nhật tin nhắn thành "Đang gửi video...".
        
        Phương thức tiện ích để cập nhật trạng thái khi video đã tải xong
        và đang được gửi về Telegram.
        
        Args:
            chat_id: ID của chat chứa tin nhắn
            message_id: ID của tin nhắn cần cập nhật
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
            
        Requirements: 5.3
        """
        return await self.update_progress(chat_id, message_id, DEFAULT_MESSAGES["sending"])
    
    async def finalize_progress(
        self, 
        chat_id: int, 
        message_id: int, 
        delete: bool = True,
        final_text: Optional[str] = None
    ) -> bool:
        """
        Hoàn tất tin nhắn tiến trình.
        
        Xóa hoặc cập nhật tin nhắn tiến trình thành trạng thái cuối cùng
        sau khi quá trình hoàn tất.
        
        Args:
            chat_id: ID của chat chứa tin nhắn
            message_id: ID của tin nhắn cần xử lý
            delete: True để xóa tin nhắn, False để cập nhật thành final_text
            final_text: Nội dung cuối cùng nếu không xóa (mặc định "Hoàn tất!")
            
        Returns:
            True nếu thành công, False nếu thất bại
            
        Requirements: 5.4
        """
        if delete:
            return await self.delete_progress(chat_id, message_id)
        else:
            text = final_text or DEFAULT_MESSAGES["completed"]
            return await self.update_progress(chat_id, message_id, text)
