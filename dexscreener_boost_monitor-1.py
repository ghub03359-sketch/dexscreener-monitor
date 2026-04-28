"""
DexScreener Boost Monitor - Telegram Notifier
Memantau coin yang baru mengaktifkan boost di DexScreener
dan mengirim notifikasi ke Telegram.

Setup:
1. pip install requests python-telegram-bot schedule
2. Isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID
3. Jalankan: python dexscreener_boost_monitor.py
"""

import requests
import time
import json
import schedule
from datetime import datetime

# ============================================================
# KONFIGURASI - ISI BAGIAN INI
# ============================================================
TELEGRAM_BOT_TOKEN = "ISI_TOKEN_BOT_TELEGRAM_ANDA"  # dari @BotFather
TELEGRAM_CHAT_ID   = "ISI_CHAT_ID_ANDA"             # dari @userinfobot

CHECK_INTERVAL_SECONDS = 30   # cek setiap 30 detik
# ============================================================

DEXSCREENER_BOOSTED_URL = "https://api.dexscreener.com/token-boosts/latest/v1"

# Simpan token yang sudah pernah dinotifikasi agar tidak spam
seen_boosts: set = set()


def send_telegram(message: str) -> None:
    """Kirim pesan ke Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Gagal kirim Telegram: {e}")


def format_number(n) -> str:
    """Format angka besar agar mudah dibaca."""
    try:
        n = float(n)
        if n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return f"{n:.4f}"
    except Exception:
        return str(n)


def fetch_boosted_tokens() -> list:
    """Ambil daftar token yang sedang di-boost dari DexScreener."""
    try:
        resp = requests.get(DEXSCREENER_BOOSTED_URL, timeout=15)
        resp.raise_for_status()
        return resp.json() if isinstance(resp.json(), list) else []
    except Exception as e:
        print(f"[ERROR] Gagal fetch DexScreener: {e}")
        return []


def check_new_boosts() -> None:
    """Cek apakah ada boost baru, kirim notifikasi jika ada."""
    global seen_boosts

    tokens = fetch_boosted_tokens()
    if not tokens:
        return

    now_str = datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}] Mengecek {len(tokens)} token ter-boost...")

    for token in tokens:
        # Buat unique key dari chainId + tokenAddress
        chain    = token.get("chainId", "unknown")
        address  = token.get("tokenAddress", "")
        boost_id = f"{chain}:{address}"

        if boost_id in seen_boosts:
            continue  # sudah pernah dinotifikasi

        # Token baru! Tandai dan kirim notifikasi
        seen_boosts.add(boost_id)

        name        = token.get("description", "N/A")
        url         = token.get("url", "")
        icon        = token.get("icon", "")
        amount      = token.get("amount", 0)
        total_amount= token.get("totalAmount", 0)
        links       = token.get("links", [])

        # Ambil link sosial jika ada
        social_links = ""
        for link in links:
            label = link.get("label") or link.get("type", "")
            href  = link.get("url", "")
            if href:
                social_links += f"  • <a href='{href}'>{label}</a>\n"

        message = (
            f"🚀 <b>BOOST BARU TERDETEKSI!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 Chain     : <b>{chain.upper()}</b>\n"
            f"📛 Token     : <b>{name}</b>\n"
            f"💰 Boost     : <b>{format_number(amount)}</b>\n"
            f"📊 Total Boost: <b>{format_number(total_amount)}</b>\n"
            f"📍 Address   : <code>{address}</code>\n"
        )

        if social_links:
            message += f"\n🌐 Links:\n{social_links}"

        if url:
            message += f"\n🔍 <a href='{url}'>Lihat di DexScreener</a>\n"

        message += f"\n⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        print(f"  ✅ BOOST BARU: {name} ({chain}) - boost: {amount}")
        send_telegram(message)


def main():
    print("=" * 50)
    print("  DexScreener Boost Monitor - Telegram Edition")
    print("=" * 50)
    print(f"  Interval cek : setiap {CHECK_INTERVAL_SECONDS} detik")
    print(f"  Telegram ID  : {TELEGRAM_CHAT_ID}")
    print("  Tekan Ctrl+C untuk berhenti")
    print("=" * 50)

    # Kirim pesan test ke Telegram
    send_telegram(
        "✅ <b>DexScreener Boost Monitor aktif!</b>\n"
        f"Memantau boost baru setiap {CHECK_INTERVAL_SECONDS} detik.\n"
        "Notifikasi akan dikirim saat ada token baru yang di-boost."
    )

    # Jalankan pertama kali langsung, lalu jadwalkan
    check_new_boosts()
    schedule.every(CHECK_INTERVAL_SECONDS).seconds.do(check_new_boosts)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
