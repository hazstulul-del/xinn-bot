import telebot
from telebot import types
import os
import time
import requests
import random
import pytz
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8623794473:AAHWHIf5qB9Oejtr1Hos6TA91fUvhVeiR3Q")
OWNER_ID = int(os.getenv("OWNER_ID", "7562630960"))
VERSION = "v5.0.1"
WIB = pytz.timezone("Asia/Jakarta")

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# API ENDPOINTS (MULTI FALLBACK)
# ============================================================
TIKTOK_APIS = [
    "https://www.tikwm.com/api/",
    "https://api.tiklydown.eu.org/api/download",
    "https://api.douyin.wtf/api",
]

API_IG = "https://api.nyxs.pw/dl/instagram"
API_YT = "https://api.nyxs.pw/dl/youtube"
API_SPOTIFY = "https://api.nyxs.pw/dl/spotify"
API_CUACA = "https://wttr.in"

# ============================================================
# WAKTU
# ============================================================
def get_wib():
    now = datetime.now(WIB)
    return now.strftime("%H:%M:%S | %d %b %Y")

# ============================================================
# START
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    name = message.from_user.first_name or "Sobat"

    video_url = "https://files.catbox.moe/bqforc.mp4"

    caption = f"""
╔══════════════════════════════╗
║     🔥  XINN MULTI BOT 🔥       ║
║        ✨ {VERSION} ✨             ║
╠══════════════════════════════╣
║  ⏰  {get_wib()}        ║
╠══════════════════════════════╣
║  👋  Hai, {name}!         ║
║  🎧  Real Downloader         ║
║  ▶️  Pilih menu di bawah ya!  ║
╚══════════════════════════════╝
"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📱 TIKTOK DL", callback_data="menu_tt"),
        types.InlineKeyboardButton("📷 IG DL", callback_data="menu_ig"),
        types.InlineKeyboardButton("▶️ YT DL", callback_data="menu_yt"),
        types.InlineKeyboardButton("🟢 SPOTIFY", callback_data="menu_sp"),
        types.InlineKeyboardButton("🌤️ CUACA", callback_data="menu_cuaca"),
        types.InlineKeyboardButton("🔍 SEARCH", callback_data="menu_search"),
        types.InlineKeyboardButton("🎮 GAMES", callback_data="menu_games"),
        types.InlineKeyboardButton("🎭 ANIME", callback_data="menu_anime"),
        types.InlineKeyboardButton("👤 PROFIL", callback_data="menu_profil"),
        types.InlineKeyboardButton("👑 ADMIN", callback_data="menu_admin")
    )

    bot.send_video(message.chat.id, video_url, caption=caption, parse_mode="Markdown", reply_markup=markup)

# ============================================================
# CALLBACK
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    data = call.data
    bot.answer_callback_query(call.id)

    if data == "menu_tt":
        msg = bot.send_message(call.message.chat.id, f"📱 *TIKTOK DOWNLOADER*\n⏰ {get_wib()}\n\nKirim link TikTok:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, download_tiktok)

    elif data == "menu_ig":
        msg = bot.send_message(call.message.chat.id, f"📷 *INSTAGRAM DOWNLOADER*\n⏰ {get_wib()}\n\nKirim link Instagram:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, download_ig)

    elif data == "menu_yt":
        msg = bot.send_message(call.message.chat.id, f"▶️ *YOUTUBE DOWNLOADER*\n⏰ {get_wib()}\n\nKirim link YouTube:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, download_yt)

    elif data == "menu_sp":
        msg = bot.send_message(call.message.chat.id, f"🟢 *SPOTIFY DOWNLOADER*\n⏰ {get_wib()}\n\nKirim link Spotify:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, download_spotify)

    elif data == "menu_cuaca":
        msg = bot.send_message(call.message.chat.id, f"🌤️ *CEK CUACA*\n⏰ {get_wib()}\n\nKetik nama kota:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, cek_cuaca)

    elif data == "menu_search":
        msg = bot.send_message(call.message.chat.id, f"🔍 *SEARCH*\n⏰ {get_wib()}\n\nKetik kata kunci:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, cari_google)

    elif data == "menu_games":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎲 Dadu", callback_data="game_dadu"),
            types.InlineKeyboardButton("🎰 Slot", callback_data="game_slot"),
            types.InlineKeyboardButton("🔙 Kembali", callback_data="back_main")
        )
        bot.send_message(call.message.chat.id, f"🎮 *GAMES*\n⏰ {get_wib()}\nPilih game:", parse_mode="Markdown", reply_markup=markup)

    elif data == "menu_anime":
        quotes = [
            "Jangan menyerah. — Naruto",
            "Percayalah padaku! — Kamina",
            "Rasa sakit membuatmu kuat. — Itachi"
        ]
        bot.send_message(call.message.chat.id, f"🎭 *ANIME QUOTE*\n⏰ {get_wib()}\n\n\"{random.choice(quotes)}\"", parse_mode="Markdown")

    elif data == "menu_profil":
        bot.send_message(call.message.chat.id, f"👤 *PROFIL*\n⏰ {get_wib()}\n🆔 ID: `{uid}`\n📊 XP: {random.randint(50,500)}\n🏆 Level: {random.randint(1,10)}", parse_mode="Markdown")

    elif data == "menu_admin":
        if uid == OWNER_ID:
            bot.send_message(call.message.chat.id, f"👑 *ADMIN*\n⏰ {get_wib()}\n✅ Bot aktif\n📊 {VERSION}", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "⛔ Akses ditolak.")

    elif data == "back_main":
        start(call.message)

    elif data == "game_dadu":
        bot.send_message(call.message.chat.id, f"🎲 Dadu: **{random.randint(1,6)}**", parse_mode="Markdown")

    elif data == "game_slot":
        s = ["🍒","🍋","🍊","💎","7️⃣"]
        h = [random.choice(s) for _ in range(3)]
        m = "🎉 JACKPOT!" if len(set(h)) == 1 else "😢 Coba lagi"
        bot.send_message(call.message.chat.id, f"🎰 [{' | '.join(h)}]\n{m}", parse_mode="Markdown")

# ============================================================
# TIKTOK DOWNLOADER — MULTI API FALLBACK (NO AUDIO)
# ============================================================
def download_tiktok(message):
    url = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏳ *Mendownload dari TikTok...*", parse_mode="Markdown")

    for api in TIKTOK_APIS:
        try:
            res = requests.get(f"{api}?url={url}", timeout=15)
            data = res.json()
            video_url = None
            title = "TikTok Video"
            author = "Unknown"

            if "tikwm" in api:
                if data.get("data"):
                    video_url = data["data"].get("play") or data["data"].get("video")
                    title = data["data"].get("title", title)
                    author = data["data"].get("author", {}).get("name", "Unknown")

            elif "tiklydown" in api:
                if data.get("video"):
                    video_url = data["video"].get("noWatermark") or data["video"].get("url")
                    title = data.get("title", title)

            elif "douyin" in api:
                if data.get("data"):
                    video_url = data["data"].get("play") or data["data"].get("video")

            # SKIP KALAU HANYA AUDIO
            if video_url and ".mp3" in video_url:
                video_url = None

            if video_url and not video_url.endswith(".mp3"):
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_video(
                    message.chat.id,
                    video_url,
                    caption=f"✅ *{title}*\n👤 {author}\n⏰ {get_wib()}",
                    parse_mode="Markdown"
                )
                return
        except:
            continue

    bot.edit_message_text("❌ *Gagal download.*\nSemua API sedang down atau video tidak tersedia.", message.chat.id, msg.message_id, parse_mode="Markdown")

# ============================================================
# INSTAGRAM DOWNLOADER
# ============================================================
def download_ig(message):
    url = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏳ *Instagram...*", parse_mode="Markdown")
    try:
        res = requests.get(f"{API_IG}?url={url}", timeout=15)
        data = res.json()
        if data.get("status") == 200:
            media_url = data.get("data", {}).get("url") or data.get("url")
            if media_url:
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_video(message.chat.id, media_url, caption=f"✅ Sukses\n⏰ {get_wib()}", parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ Tidak bisa ambil media.", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Gagal.", message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Error.", message.chat.id, msg.message_id)

# ============================================================
# YOUTUBE
# ============================================================
def download_yt(message):
    url = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏳ *YouTube...*", parse_mode="Markdown")
    try:
        res = requests.get(f"{API_YT}?url={url}", timeout=15)
        data = res.json()
        if data.get("status") == 200:
            info = data.get("data", {})
            judul = info.get("title", "YT")
            dl = info.get("url") or info.get("download")
            if dl:
                bot.delete_message(message.chat.id, msg.message_id)
                bot.send_video(message.chat.id, dl, caption=f"✅ *{judul}*\n⏰ {get_wib()}", parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ Tidak tersedia.", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Gagal.", message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Error.", message.chat.id, msg.message_id)

# ============================================================
# SPOTIFY
# ============================================================
def download_spotify(message):
    url = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏳ *Spotify → YouTube...*", parse_mode="Markdown")
    try:
        res = requests.get(f"{API_SPOTIFY}?url={url}", timeout=10)
        data = res.json()
        if data.get("status") == 200:
            info = data.get("data", {})
            judul = info.get("title", "Unknown")
            artis = info.get("artist", "Unknown")
            bot.edit_message_text(f"🎵 *{judul}* — {artis}\n⏳ YouTube...", message.chat.id, msg.message_id, parse_mode="Markdown")
            query = f"{judul} {artis} audio"
            yt = requests.get(f"https://api.nyxs.pw/search/youtube?query={query}", timeout=10).json()
            if yt.get("data"):
                yt_url = yt["data"][0]["url"]
                dl = requests.get(f"https://api.nyxs.pw/dl/youtube?url={yt_url}", timeout=15).json()
                if dl.get("data"):
                    audio = dl["data"].get("url") or dl["data"].get("download")
                    if audio:
                        bot.delete_message(message.chat.id, msg.message_id)
                        bot.send_audio(message.chat.id, audio, title=judul, performer=artis, caption=f"✅ *{judul}* — {artis}\n⏰ {get_wib()}", parse_mode="Markdown")
                        return
            bot.edit_message_text("❌ Tidak ditemukan.", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Gagal.", message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Error.", message.chat.id, msg.message_id)

# ============================================================
# CUACA
# ============================================================
def cek_cuaca(message):
    kota = message.text.strip()
    try:
        res = requests.get(f"{API_CUACA}/{kota}?format=%t+%C+%h+%w", timeout=5)
        bot.send_message(message.chat.id, f"🌤️ *{kota.upper()}*\n⏰ {get_wib()}\n\n{res.text}", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "❌ Kota tidak ditemukan.")

# ============================================================
# SEARCH
# ============================================================
def cari_google(message):
    q = message.text.strip()
    bot.send_message(message.chat.id, f"🔍 *{q}*\n⏰ {get_wib()}\n\n🔗 [Google](https://google.com/search?q={q})", parse_mode="Markdown", disable_web_page_preview=True)

# ============================================================
# FALLBACK
# ============================================================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    start(message)

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print(f"⚡ XINN MULTI BOT {VERSION} RUNNING...")
    print(f"⏰ {get_wib()}")
    bot.infinity_polling()
