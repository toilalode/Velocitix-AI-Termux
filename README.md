# Velocitix AI Chat — Termux

Chat trực tiếp với Velocitix AI ngay trong terminal Termux (Android), không cần mở trình duyệt.
Không cần cài thư viện gì thêm — chỉ dùng thư viện có sẵn của Python.

🔗 App web chính: https://toilalode.github.io/

## Cài đặt

1. Cài Python trong Termux:
   ```
   pkg update && pkg install python -y
   ```

2. Cấp quyền cho Termux đọc bộ nhớ máy (để lấy file đã tải về `Download`):
   ```
   termux-setup-storage
   ```
   Sẽ hiện popup xin quyền — bấm **Cho phép**.

3. Tải file `velocitix_chat.py` về điện thoại (qua trình duyệt, lưu vào `Download`), rồi copy vào Termux:
   ```
   cp /sdcard/Download/velocitix_chat.py ~/velocitix_chat.py
   ```

## Chạy

```
python ~/velocitix_chat.py
```

- **Lần đầu chạy**: script sẽ hỏi API key → mở app → sidebar **⚙️ Cài đặt → API Key** → copy → dán vào Termux → Enter.
  Key tự lưu vào `~/.velocitix_key`, các lần sau khỏi nhập lại.
- Gõ câu hỏi, Enter để gửi.
- Gõ `thoat` (hoặc `exit`, `quit`, hoặc Ctrl+C) để dừng.

Script tự giữ vài lượt hội thoại gần nhất trong phiên chat để AI nhớ ngữ cảnh (API không tự lưu lịch sử phía server, mỗi request là độc lập).

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `[Lỗi 401]` | API key sai/đã bị thu hồi | Xoá `~/.velocitix_key` rồi chạy lại để nhập key mới (lấy key hiện tại trong app → Cài đặt → API Key) |
| `[Lỗi 429]` | Gửi quá nhanh hoặc hết hạn mức trong ngày | Chờ 1 phút (giới hạn 10 request/phút) hoặc chờ qua ngày hôm sau (giới hạn 200 request/ngày) |
| `[Lỗi HTTP 403]` | Bị chặn ở tầng Cloudflare (không phải do key sai) | Thử lại; nếu vẫn lỗi, kiểm tra cài đặt Bot Fight Mode / Security Level trên Cloudflare Dashboard cho worker |
| `[Lỗi mạng]` | Điện thoại mất mạng hoặc worker chưa deploy | Kiểm tra kết nối mạng, hoặc chạy `wrangler deploy` lại worker |

## Cấu hình

Địa chỉ API và nơi lưu key nằm ở đầu file `velocitix_chat.py`, sửa trực tiếp nếu cần:

```python
API_URL = "https://my-ai-worker.vudanhquy1002.workers.dev/api/external/chat"
KEY_FILE = os.path.expanduser("~/.velocitix_key")
```

## Liên quan

- Web app: https://toilalode.github.io/
- Repo GitHub: https://github.com/toilalode/toilalode.github.io
