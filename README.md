# Telegram Video Downloader Bot

Bot Telegram cá nhân để tải video từ YouTube, Facebook, Instagram. Bot chỉ phục vụ một người dùng duy nhất (chủ sở hữu).

## Tính năng

- Tải video từ YouTube, Facebook, Instagram
- Hiển thị tiến trình tải
- Tự động xóa file tạm sau khi gửi
- Xác thực người dùng (chỉ chủ sở hữu mới dùng được)

## Yêu cầu

- Python 3.10+
- Telegram Bot Token (lấy từ [@BotFather](https://t.me/BotFather))
- Telegram User ID (lấy từ [@userinfobot](https://t.me/userinfobot))

## Cài đặt

### 1. Clone repository

```bash
git clone git@github.com:DuongCoder04/download-video-telegram-bot.git
cd download-video-telegram-bot
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường

Copy file `.env.example` thành `.env` và điền thông tin:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```
TELEGRAM_TOKEN=your_telegram_bot_token_here
OWNER_ID=your_telegram_user_id_here
```

### 4. Chạy bot

```bash
python bot.py
```

## Triển khai

### Railway

1. Tạo project mới trên [Railway](https://railway.app)
2. Kết nối với GitHub repository
3. Thêm biến môi trường `TELEGRAM_TOKEN` và `OWNER_ID`
4. Deploy tự động

### Render

1. Tạo Web Service mới trên [Render](https://render.com)
2. Kết nối với GitHub repository
3. Chọn Environment: Python
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python bot.py`
6. Thêm biến môi trường `TELEGRAM_TOKEN` và `OWNER_ID`

### VPS/Server

```bash
# Cài đặt
git clone git@github.com:DuongCoder04/download-video-telegram-bot.git
cd download-video-telegram-bot
pip install -r requirements.txt

# Chạy với screen hoặc tmux
screen -S bot
python bot.py
# Ctrl+A, D để detach
```

## Sử dụng

1. Mở chat với bot trên Telegram
2. Gửi link video từ YouTube, Facebook hoặc Instagram
3. Chờ bot tải và gửi video về

### Lệnh

- `/start` - Tin nhắn chào mừng
- `/help` - Hướng dẫn sử dụng
- `/status` - Trạng thái bot

## Giới hạn

- Kích thước file tối đa: 50MB (giới hạn của Telegram Bot API)
- Chỉ hỗ trợ: YouTube, Facebook, Instagram

## License

MIT
