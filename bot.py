#!/usr/bin/env python3
"""
Telegram Video Downloader Bot

Bot Telegram cá nhân để tải video từ YouTube, Facebook, Instagram.
Chạy bằng lệnh: python bot.py

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from auth import auth_decorator
from url_parser import parse_url, is_supported_platform
from downloader import download_video
from sender import send_video
from progress import ProgressManager
from error_handler import get_user_friendly_error
from models import Platform

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global owner_id (set in main)
OWNER_ID: int = 0


# ============================================================================
# Command Handlers (Requirements: 9.1, 9.2, 9.3)
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler cho lệnh /start.
    
    Gửi tin nhắn chào mừng và hướng dẫn sử dụng cơ bản.
    
    Requirements: 9.1
    """
    welcome_message = (
        "👋 Chào mừng bạn đến với Video Downloader Bot!\n\n"
        "🎬 Tôi có thể giúp bạn tải video từ:\n"
        "• YouTube\n"
        "• Facebook\n"
        "• Instagram\n\n"
        "📝 Cách sử dụng: Chỉ cần gửi link video cho tôi!\n\n"
        "💡 Gõ /help để xem hướng dẫn chi tiết."
    )
    await update.message.reply_text(welcome_message)
    logger.info(f"User {update.effective_user.id} đã gọi /start")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler cho lệnh /help.
    
    Gửi danh sách các nền tảng được hỗ trợ và cách sử dụng chi tiết.
    
    Requirements: 9.2
    """
    help_message = (
        "📖 Hướng dẫn sử dụng Video Downloader Bot\n\n"
        "🎯 Các nền tảng được hỗ trợ:\n"
        "• YouTube (youtube.com, youtu.be)\n"
        "• Facebook (facebook.com, fb.watch)\n"
        "• Instagram (instagram.com/p/, instagram.com/reel/)\n\n"
        "📝 Cách sử dụng:\n"
        "1. Copy link video từ nền tảng bạn muốn\n"
        "2. Gửi link đó cho bot\n"
        "3. Đợi bot tải và gửi video về cho bạn\n\n"
        "⚠️ Lưu ý:\n"
        "• Video phải có kích thước dưới 50MB\n"
        "• Một số video riêng tư có thể không tải được\n\n"
        "🔧 Các lệnh:\n"
        "/start - Bắt đầu sử dụng bot\n"
        "/help - Xem hướng dẫn này\n"
        "/status - Kiểm tra trạng thái bot"
    )
    await update.message.reply_text(help_message)
    logger.info(f"User {update.effective_user.id} đã gọi /help")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler cho lệnh /status.
    
    Gửi trạng thái hoạt động của bot.
    
    Requirements: 9.3
    """
    status_message = (
        "✅ Bot đang hoạt động bình thường!\n\n"
        "🎬 Sẵn sàng tải video từ:\n"
        "• YouTube ✓\n"
        "• Facebook ✓\n"
        "• Instagram ✓\n\n"
        "📤 Gửi link video để bắt đầu!"
    )
    await update.message.reply_text(status_message)
    logger.info(f"User {update.effective_user.id} đã gọi /status")


# ============================================================================
# Message Handler (Requirements: 2.5, 3.1, 3.2, 3.4, 4.1, 5.1, 5.3)
# ============================================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler chính để xử lý URL video.
    
    Tích hợp auth, url parser, downloader, sender, progress manager.
    
    Requirements: 2.5, 3.1, 3.2, 3.4, 4.1, 5.1, 5.3
    """
    text = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    logger.info(f"Nhận tin nhắn từ user {user_id}: {text[:50]}...")
    
    # Parse URL và nhận diện platform
    url, platform = parse_url(text)
    
    # Requirement 2.5: Nếu không có URL hợp lệ, gửi hướng dẫn sử dụng
    if url is None:
        await update.message.reply_text(
            "❓ Tôi không tìm thấy link video trong tin nhắn của bạn.\n\n"
            "📝 Vui lòng gửi link video từ:\n"
            "• YouTube\n"
            "• Facebook\n"
            "• Instagram\n\n"
            "💡 Gõ /help để xem hướng dẫn chi tiết."
        )
        return
    
    # Requirement 2.4: Nếu platform không được hỗ trợ
    if not is_supported_platform(platform):
        await update.message.reply_text(
            "❌ Nền tảng này chưa được hỗ trợ.\n\n"
            "🎬 Các nền tảng được hỗ trợ:\n"
            "• YouTube (youtube.com, youtu.be)\n"
            "• Facebook (facebook.com, fb.watch)\n"
            "• Instagram (instagram.com)"
        )
        return
    
    # Khởi tạo progress manager
    progress = ProgressManager(context.bot)
    progress_msg_id = None
    
    try:
        # Requirement 5.1: Gửi tin nhắn "Đang tải video..."
        progress_msg_id = await progress.send_downloading(chat_id)
        
        # Callback để cập nhật tiến trình
        last_percent = [0]  # Use list to allow modification in closure
        
        async def update_progress_callback(percent: float):
            # Chỉ cập nhật khi thay đổi đáng kể (>5%)
            if percent - last_percent[0] >= 5 or percent >= 100:
                last_percent[0] = percent
                await progress.update_downloading_percent(chat_id, progress_msg_id, percent)
        
        # Tạo sync callback wrapper (yt-dlp không hỗ trợ async callback)
        def sync_progress_callback(percent: float):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(update_progress_callback(percent))
            except Exception:
                pass  # Ignore progress update errors
        
        # Requirement 3.1: Tải video
        logger.info(f"Bắt đầu tải video từ {platform.value}: {url}")
        result = download_video(
            url=url,
            output_dir="/tmp",
            progress_callback=sync_progress_callback
        )
        
        # Requirement 3.4: Nếu tải thất bại
        if not result.success:
            error_msg = get_user_friendly_error(Exception(result.error_message or "Unknown error"))
            await progress.update_progress(chat_id, progress_msg_id, f"❌ {error_msg}")
            logger.error(f"Tải video thất bại: {result.error_message}")
            return
        
        # Requirement 5.3: Cập nhật tin nhắn thành "Đang gửi video..."
        await progress.update_sending(chat_id, progress_msg_id)
        
        # Requirement 4.1: Gửi video về Telegram
        logger.info(f"Gửi video: {result.file_path} ({result.file_size / (1024*1024):.1f}MB)")
        success, error = await send_video(
            bot=context.bot,
            chat_id=chat_id,
            file_path=result.file_path
        )
        
        if success:
            # Xóa tin nhắn tiến trình khi hoàn tất
            await progress.delete_progress(chat_id, progress_msg_id)
            logger.info(f"Gửi video thành công cho user {user_id}")
        else:
            await progress.update_progress(chat_id, progress_msg_id, f"❌ {error}")
            logger.error(f"Gửi video thất bại: {error}")
            
    except Exception as e:
        error_msg = get_user_friendly_error(e)
        logger.error(f"Lỗi xử lý tin nhắn: {e}")
        
        if progress_msg_id:
            await progress.update_progress(chat_id, progress_msg_id, f"❌ {error_msg}")
        else:
            await update.message.reply_text(f"❌ {error_msg}")


# ============================================================================
# Main Function (Requirements: 8.3, 8.4, 8.5)
# ============================================================================

def main() -> None:
    """
    Main function để khởi động bot.
    
    - Đọc cấu hình từ biến môi trường
    - Khởi tạo Application với token
    - Đăng ký tất cả handlers với auth decorator
    - Khởi động polling mode
    
    Requirements: 8.3, 8.4, 8.5
    """
    global OWNER_ID
    
    # Load configuration from environment variables (Requirements 8.1, 8.2)
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    owner_id_str = os.getenv("OWNER_ID")
    
    # Validate required environment variables
    if not telegram_token:
        logger.error("TELEGRAM_TOKEN không được cấu hình trong biến môi trường")
        return
    
    if not owner_id_str:
        logger.error("OWNER_ID không được cấu hình trong biến môi trường")
        return
    
    try:
        OWNER_ID = int(owner_id_str)
    except ValueError:
        logger.error("OWNER_ID phải là một số nguyên")
        return
    
    # Requirement 8.5: Log khởi động thành công
    logger.info("=" * 50)
    logger.info("Telegram Video Downloader Bot")
    logger.info("=" * 50)
    logger.info(f"Owner ID: {OWNER_ID}")
    
    # Initialize bot application
    application = Application.builder().token(telegram_token).build()
    
    # Create auth-protected handlers
    auth = auth_decorator(OWNER_ID)
    
    # Register command handlers (Requirements 9.1, 9.2, 9.3)
    application.add_handler(CommandHandler("start", auth(start_command)))
    application.add_handler(CommandHandler("help", auth(help_command)))
    application.add_handler(CommandHandler("status", auth(status_command)))
    
    # Register message handler for video URLs (Requirements 2.5, 3.1, 4.1, 5.1)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auth(handle_message))
    )
    
    # Requirement 8.5: Log successful startup
    logger.info("Bot đã sẵn sàng!")
    logger.info("Đang chạy ở chế độ polling...")
    logger.info("=" * 50)
    
    # Requirement 8.3: Start polling mode
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
