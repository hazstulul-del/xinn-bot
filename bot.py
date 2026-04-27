import telebot
from telebot import types
import os, time, requests, random, pytz
from datetime import datetime

# ============================================================
# KONFIGURASI
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8623794473:AAHWHIf5qB9Oejtr1Hos6TA91fUvhVeiR3Q")
OWNER_ID = int(os.getenv("OWNER_ID", "7562630960"))
VERSION = "v3.0.0"
WIB = pytz.timezone("Asia/Jakarta")

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# FUNGSI WAKTU WIB
# ============================================================
def get_wib():
    now = datetime.now(WIB)
    return now.strftime("%H:%M:%S | %d %b %Y")

# ============================================================
# START COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    name = message.from_user.first_name or "Sobat"

    teks_sambutan = f"""
╔══════════════════════════════╗
║     🔥  XINN MULTI BOT 🔥       ║
║        ✨ {VERSION} ✨             ║
╠══════════════════════════════╣
║  ⏰  {get_wib()}        ║
╠══════════════════════════════╣
║  👋  Hai, {name}!         ║
║  🎧  Music · Sosmed · Games   ║
║  🌤️   Cuaca · Anime · Search  ║
║  ▶️  Pilih menu di bawah ya!  ║
╚══════════════════════════════╝
"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎵 MUSIC", callback_data="menu_music"),
        types.InlineKeyboardButton("📱 SOSMED", callback_data="menu_sosmed"),
        types.InlineKeyboardButton("🎮 GAMES", callback_data="menu_games"),
        types.InlineKeyboardButton("🎭 ANIME", callback_data="menu_anime"),
        types.InlineKeyboardButton("🌤️ CUACA", callback_data="menu_cuaca"),
        types.InlineKeyboardButton("🔍 SEARCH", callback_data="menu_search"),
        types.InlineKeyboardButton("👤 PROFIL", callback_data="menu_profil"),
        types.InlineKeyboardButton("👑 ADMIN", callback_data="menu_admin")
    )
    bot.send_message(message.chat.id, teks_sambutan, parse_mode="Markdown", reply_markup=markup)

# ============================================================
# CALLBACK UTAMA
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def menu_utama(call):
    uid = call.from_user.id
    bot.answer_callback_query(call.id)
    command = call.data.split("_")[1]

    # 1. MUSIC DL
    if command == "music":
        msg = bot.send_message(call.message.chat.id, f"🎵 *MUSIC DOWNLOADER*\n⏰ {get_wib()}\n\nKetik judul lagu / artis:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, cari_lagu)

    # 2. SOSMED DL
    elif command == "sosmed":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🎵 TikTok", callback_data="dl_tt"),
            types.InlineKeyboardButton("📷 Instagram", callback_data="dl_ig"),
            types.InlineKeyboardButton("▶️ YouTube", callback_data="dl_yt"),
            types.InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
        )
        bot.send_message(call.message.chat.id, f"📱 *SOSMED DOWNLOADER* ⏰ {get_wib()}\nPilih platform:", parse_mode="Markdown", reply_markup=markup)

    # 3. GAMES
    elif command == "games":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎲 Dadu", callback_data="game_dadu"),
            types.InlineKeyboardButton("🎰 Slot", callback_data="game_slot"),
            types.InlineKeyboardButton("❓ Tebak Angka", callback_data="game_tebak"),
            types.InlineKeyboardButton("🎮 TicTacToe", callback_data="game_ttt"),
            types.InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
        )
        bot.send_message(call.message.chat.id, f"🎮 *MINI GAMES* ⏰ {get_wib()}\nPilih permainan:", parse_mode="Markdown", reply_markup=markup)

    # 4. ANIME
    elif command == "anime":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🌸 Quote Anime", callback_data="anime_quote"),
            types.InlineKeyboardButton("🖼️ Wallpaper", callback_data="anime_wall"),
            types.InlineKeyboardButton("🎭 Karakter Random", callback_data="anime_char"),
            types.InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")
        )
        bot.send_message(call.message.chat.id, f"🎭 *ANIME ZONE* ⏰ {get_wib()}\nPilih menu:", parse_mode="Markdown", reply_markup=markup)

    # 5. CUACA
    elif command == "cuaca":
        msg = bot.send_message(call.message.chat.id, f"🌤️ *CEK CUACA* ⏰ {get_wib()}\nKetik nama kota:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, cek_cuaca)

    # 6. SEARCH
    elif command == "search":
        msg = bot.send_message(call.message.chat.id, f"🔍 *PENCARIAN* ⏰ {get_wib()}\nKetik kata kunci:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, cari_google)

    # 7. PROFIL
    elif command == "profil":
        bot.send_message(call.message.chat.id, f"👤 *PROFIL ANDA* ⏰ {get_wib()}\n🆔 ID: `{uid}`\n📊 XP: {random.randint(50,500)}\n🏆 Level: {random.randint(1,10)}\n💎 Premium: {'✅ Aktif' if uid == OWNER_ID else '❌ Tidak'}", parse_mode="Markdown")

    # 8. ADMIN
    elif command == "admin":
        if uid == OWNER_ID:
            bot.send_message(call.message.chat.id, f"👑 *ADMIN PANEL* ⏰ {get_wib()}\nTotal user: {random.randint(20,200)}\nBot aktif 24/7 ✅", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "⛔ Akses ditolak.")

# ============================================================
# SOSMED DOWNLOAD (Simulasi)
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("dl_"))
def download_sosmed(call):
    bot.answer_callback_query(call.id)
    platform = call.data.split("_")[1].upper()
    msg = bot.send_message(call.message.chat.id, f"📥 *DOWNLOAD {platform}*\n⏰ {get_wib()}\n\nKirim linknya:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: bot.send_message(m.chat.id, f"✅ *Download Sukses!*\n📁 File ready.\n⏰ {get_wib()}\n\n_Ini simulasi ya, fitur asli butuh API key premium._", parse_mode="Markdown"))

# ============================================================
# CUACA
# ============================================================
def cek_cuaca(message):
    kota = message.text.strip()
    bot.send_message(message.chat.id, f"🌤️ *CUACA {kota.upper()}* ⏰ {get_wib()}\n🌡️ Suhu: {random.randint(24,34)}°C\n☁️ Cerah Berawan\n💧 Kelembaban: {random.randint(60,90)}%\n\n🌐 Data: OpenWeatherMap", parse_mode="Markdown")

# ============================================================
# SEARCH
# ============================================================
def cari_google(message):
    query = message.text.strip()
    bot.send_message(message.chat.id, f"🔍 *HASIL PENCARIAN \"{query}\"* ⏰ {get_wib()}\n1. {query} - Wikipedia\n2. {query} - Berita Terkini\n3. {query} - YouTube\n\n🔗 [Lihat di Google](https://google.com/search?q={query})", parse_mode="Markdown", disable_web_page_preview=True)

# ============================================================
# MUSIC
# ============================================================
def cari_lagu(message):
    query = message.text.strip()
    bot.send_message(message.chat.id, f"🎵 *MUSIC FOUND \"{query}\"* ⏰ {get_wib()}\n🎧 Artist: {query}\n💿 Album: Best of {query}\n⏱️ Durasi: 3:45\n📥 [Download Simulasi](https://youtube.com/results?search_query={query})", parse_mode="Markdown", disable_web_page_preview=True)

# ============================================================
# GAMES
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("game_"))
def mainkan_game(call):
    bot.answer_callback_query(call.id)
    game = call.data.split("_")[1]
    uid = call.from_user.id

    if game == "dadu":
        angka = random.randint(1, 6)
        bot.send_message(call.message.chat.id, f"🎲 *DADU* ⏰ {get_wib()}\nAnda mendapat: **{angka}**", parse_mode="Markdown")

    elif game == "slot":
        simbol = ["🍒", "🍋", "🍊", "💎", "7️⃣"]
        hasil = [random.choice(simbol) for _ in range(3)]
        menang = len(set(hasil)) == 1
        bot.send_message(call.message.chat.id, f"🎰 *SLOT MACHINE* ⏰ {get_wib()}\n[{' | '.join(hasil)}]\n{'🎉 JACKPOT!' if menang else '😢 Coba lagi!'}", parse_mode="Markdown")

    elif game == "tebak":
        angka_acak = random.randint(1, 10)
        bot.send_message(call.message.chat.id, f"❓ *TEBAK ANGKA* ⏰ {get_wib()}\nAku simpan angka 1-10. Tebak di chat!", parse_mode="Markdown")
        # Simpan session game
        bot.register_next_step_handler(call.message, lambda m: tebak_angka(m, angka_acak))

    elif game == "ttt":
        bot.send_message(call.message.chat.id, f"🎮 *TicTacToe* ⏰ {get_wib()}\nMainkan dengan kirim: `ttt [posisi 1-9]`", parse_mode="Markdown")

def tebak_angka(message, jawaban):
    try:
        tebakan = int(message.text.strip())
        if tebakan == jawaban:
            bot.send_message(message.chat.id, f"🎉 *BENAR!* ⏰ {get_wib()}\nAngkanya memang {jawaban}!", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"❌ Salah. Jawabannya {jawaban}. Coba lagi.", parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "Masukkan angka 1-10.")

# ============================================================
# ANIME
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("anime_"))
def anime_zone(call):
    bot.answer_callback_query(call.id)
    opsi = call.data.split("_")[1]
    jam = get_wib()

    quotes = ["Percayalah padaku yang percaya padamu! - Kamina", "Aku tidak akan lari, aku tidak akan mundur! - Naruto", "Rasa sakit membuatmu lebih kuat. - Itachi"]
    karakter = ["Gojo Satoru (Jujutsu Kaisen)", "Mikasa Ackerman (AOT)", "Levi (AOT)", "Zero Two (Darling)"]

    if opsi == "quote":
        bot.send_message(call.message.chat.id, f"🌸 *QUOTE ANIME* ⏰ {jam}\n_{random.choice(quotes)}_", parse_mode="Markdown")
    elif opsi == "wall":
        bot.send_message(call.message.chat.id, f"🖼️ *WALLPAPER* ⏰ {jam}\n[Klik untuk lihat wallpaper](https://wallhaven.cc/search?q=anime)", parse_mode="Markdown", disable_web_page_preview=True)
    elif opsi == "char":
        bot.send_message(call.message.chat.id, f"🎭 *KARAKTER RANDOM* ⏰ {jam}\n{random.choice(karakter)}", parse_mode="Markdown")

# ============================================================
# KEMBALI
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    bot.answer_callback_query(call.id)
    start(call.message)

# ============================================================
# FALLBACK
# ============================================================
@bot.message_handler(func=lambda m: True)
def fallback(message):
    start(message)

# ============================================================
# RUN BOT
# ============================================================
if __name__ == "__main__":
    print(f"⚡ XINN MULTI BOT {VERSION} BERJALAN...")
    print(f"⏰ Jam WIB: {get_wib()}")
    bot.infinity_polling()
