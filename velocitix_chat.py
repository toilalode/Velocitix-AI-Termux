#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cách dùng trong Termux:
  1. pkg update && pkg install python -y
  2. Chép file này vào điện thoại (ví dụ tải qua trình duyệt vào thư mục Download,
     rồi trong Termux: cp /sdcard/Download/velocitix_chat.py ~/velocitix_chat.py)
  3. python velocitix_chat.py
  4. Lần đầu chạy sẽ hỏi API key -> dán key lấy trong app (Cài đặt -> API Key) -> Enter.
     Key sẽ tự lưu vào ~/.velocitix_key để lần sau khỏi nhập lại.
  5. Gõ chuyện muốn nói, Enter để gửi. Gõ "thoat" hoặc Ctrl+C để dừng.
  6. Gõ "/model" bất cứ lúc nào để đổi model đang dùng.

  echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
"""

import json
import os
import sys
import urllib.request
import urllib.error

# Ép stdout/stdin dùng UTF-8 — một số bản Termux/Android mặc định locale không phải
# UTF-8, khiến tiếng Việt có dấu (ký tự đặc biệt) bị in sai hoặc mất dấu.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass  # Python < 3.7 không có reconfigure() — bỏ qua, hiếm khi gặp trên Termux

API_URL = "https://my-ai-worker.vudanhquy1002.workers.dev/api/external/chat"
KEY_FILE = os.path.expanduser("~/.velocitix_key")
MAX_HISTORY_TURNS = 6  # giữ vài lượt gần nhất để AI nhớ ngữ cảnh (API không tự lưu hội thoại)

MODELS = {
    "1": ("smart", "Smart"),
    "2": ("fast", "Fast"),
    "3": ("lite", "Lite"),
    "4": ("coding", "Coding "),
}
DEFAULT_MODEL = "smart"


def load_or_ask_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            key = f.read().strip()
        if key:
            return key
    print("Chưa có API key được lưu.")
    key = input("Dán API key của bạn (lấy trong app -> Cài đặt -> API Key): ").strip()
    if not key:
        print("Không có key, thoát.")
        sys.exit(1)
    with open(KEY_FILE, "w", encoding="utf-8") as f:
        f.write(key)
    os.chmod(KEY_FILE, 0o600)
    print(f"Đã lưu key vào {KEY_FILE} (lần sau khỏi nhập lại).\n")
    return key


def choose_model(current):
    print("\nChọn model:")
    for k, (value, label) in MODELS.items():
        mark = " (đang dùng)" if value == current else ""
        print(f"  {k}. {label}{mark}")
    choice = input("Nhập số (Enter để giữ nguyên): ").strip()
    if choice in MODELS:
        return MODELS[choice][0]
    return current


def build_prompt(history, user_text):
    """Ghép vài lượt gần nhất thành 1 prompt duy nhất, vì API chỉ nhận 1 chuỗi 'prompt'."""
    if not history:
        return user_text
    lines = []
    for role, text in history[-MAX_HISTORY_TURNS:]:
        prefix = "Người dùng" if role == "user" else "AI"
        lines.append(f"{prefix}: {text}")
    lines.append(f"Người dùng: {user_text}")
    lines.append("AI:")
    return "\n".join(lines)


def ask(api_key, prompt, model):
    body = json.dumps({"prompt": prompt, "model": model}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "x-api-key": api_key,
            "User-Agent": "Mozilla/5.0 (Termux VelocitixChat)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("text") or json.dumps(data, ensure_ascii=False)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(raw)
            msg = err.get("error", raw)
        except Exception:
            msg = raw.strip()[:300] or str(e)
        if e.code == 401:
            return f"[Lỗi 401] API key không hợp lệ. Xoá file {KEY_FILE} rồi chạy lại để nhập key mới. Chi tiết: {msg}"
        if e.code == 429:
            return f"[Lỗi 429] {msg}"
        return f"[Lỗi HTTP {e.code}] {msg}"
    except urllib.error.URLError as e:
        return f"[Lỗi mạng] Không kết nối được tới server: {e.reason}"


def main():
    api_key = load_or_ask_key()
    model = DEFAULT_MODEL
    history = []
    print("========== Velocitix AI ==========")
    print(f"Model hiện tại: {model}. Gõ 'model' để đổi model.")
    print("Gõ 'thoat' hoặc 'exit' để dừng. Ctrl+C cũng thoát được.\n")

    while True:
        try:
            user_text = input("Bro: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐừng mà bro!")
            break

        if not user_text:
            continue
        if user_text.lower() in ("thoat", "exit", "quit"):
            print("Đừng mà bro!")
            break
        if user_text.lower() in ("/model", "model"):
            model = choose_model(model)
            print(f"-> Đang dùng model: {model}\n")
            continue

        prompt = build_prompt(history, user_text)
        reply = ask(api_key, prompt, model)
        print(f"AI: {reply}\n")

        history.append(("user", user_text))
        history.append(("assistant", reply))


if __name__ == "__main__":
    main()
