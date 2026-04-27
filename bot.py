import telebot
from telebot import types
import sqlite3
import requests
import time
import os
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
BOT_TOKEN = "8623794473:AAHWHIf5qB9Oejtr1Hos6TA91fUvhVeiR3Q"
OWNER_ID = 7562630960
ADMIN_USERNAME = "@xinn_93"
DANA_NUMBER = "083175050030"
PTERO_URL = os.getenv("PTERO_URL", "https://panel.tuan.com")
PTERO_API_KEY = os.getenv("PTERO_API_KEY", "ptlc_xxxxx")
PTERO_NEST_ID = int(os.getenv("PTERO_NEST_ID", "1"))
PTERO_EGG_ID = int(os.getenv("PTERO_EGG_ID", "1"))
PTERO_LOCATION_ID = int(os.getenv("PTERO_LOCATION_ID", "1"))

# ============================================================
# BOT INIT
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# DATABASE
# ============================================================
conn = sqlite3.connect("xinn_panel.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    package TEXT,
    panel_user TEXT,
    panel_pass TEXT,
    status TEXT DEFAULT 'pending_payment',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_seen TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ============================================================
# PTERODACTYL API
# ============================================================
HEADERS = {}

def update_headers():
    global HEADERS
    HEADERS = {
        "Authorization": f"Bearer {PTERO_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

update_headers()

def ptero_create_user(email, username, password, first_name, last_name):
    url = f"{PTERO_URL}/api/application/users"
    payload = {
        "email": email,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "password": password
    }
    r = requests.post(url, json=payload, headers=HEADERS)
    return r.json()

def ptero_create_server(name, user_id, ram, disk=5120, cpu=100):
    url = f"{PTERO_URL}/api/application/servers"
    payload = {
        "name": name,
        "user": user_id,
        "nest": PTERO_NEST_ID,
        "egg": PTERO_EGG_ID,
        "docker_image": "ghcr.io/pterodactyl/yolks:nodejs_18",
        "startup": "if [[ -d .git ]] && [[ {{AUTO_UPDATE}} == \"1\" ]]; then git pull; fi; npm install; node index.js",
        "limits": {
            "memory": ram,
            "swap": 0,
            "disk": disk,
            "io": 500,
            "cpu": cpu
        },
        "feature_limits": {
            "databases": 1,
            "backups": 1,
            "allocations": 1
        },
        "environment": {},
        "allocation": {
            "default": PTERO_LOCATION_ID
        }
    }
    r = requests.post(url, json=payload, headers=HEADERS)
    return r.json()

PACKAGE_MAP = {
    "1gb": 1024, "2gb": 2048, "3gb": 3072, "4gb": 4096,
    "5gb": 5120, "6gb": 6144, "7gb": 7168, "8gb": 8192,
    "9gb": 9216, "10gb": 10240, "unli": 0
}

PRICE_MAP = {
    "1gb": 5000, "2gb": 10000, "4gb": 20000,
    "8gb": 35000, "unli": 50000
}

# ============================================================
# HELPER
# ============================================================
def log_user(user):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                   (user.id, user.username))
    conn.commit()

def is_owner(user_id):
    return user_id == OWNER_ID

# ============================================================
# START
# ============================================================
@bot.message_handler(commands=['start'])
def start(message):
    log_user(message.from_user)
    uid = message.from_user.id

    caption = (
        "『 \U0001f451 XINN PANEL STORE \U0001f451 』\n\n"
        "\u26a1 Panel murah \u2022 Fast create \u2022 Auto setup\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        "Silakan pilih menu di bawah ini:"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("\U0001f50d CEK ID", callback_data="cek_id")
    btn2 = types.InlineKeyboardButton("\U0001f6d2 BELI PANEL", callback_data="beli_panel")
    btn3 = types.InlineKeyboardButton("\u26a1 CREATE PANEL", callback_data="create_panel")
    btn4 = types.InlineKeyboardButton("\U0001f451 OWNER MENU", callback_data="owner_menu")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    bot.send_message(message.chat.id, caption, reply_markup=markup)

# ============================================================
# MENU
# ============================================================
@bot.message_handler(commands=['menu'])
def menu(message):
    start(message)

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    bot.send_message(message.chat.id, f"Admin: {ADMIN_USERNAME}\nDANA: {DANA_NUMBER}")

# ============================================================
# CALLBACK HANDLER
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    data = call.data

    if data == "cek_id":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"\U0001f194 ID Telegram kamu: `{uid}`", parse_mode="Markdown")

    elif data == "beli_panel":
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup(row_width=2)
        for pkg, price in PRICE_MAP.items():
            markup.add(types.InlineKeyboardButton(f"\U0001f4e6 {pkg.upper()} \u2014 Rp{price:,}", callback_data=f"order_{pkg}"))
        markup.add(types.InlineKeyboardButton("\u2b05\ufe0f Kembali", callback_data="back_menu"))
        bot.send_message(call.message.chat.id, "\U0001f6d2 *PILIH PAKET:*", parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("order_"):
        pkg = data.split("_")[1]
        price = PRICE_MAP[pkg]
        bot.answer_callback_query(call.id)

        cursor.execute("INSERT INTO orders (user_id, package, status) VALUES (?, ?, 'pending_payment')", (uid, pkg))
        conn.commit()

        text = (
            "\U0001f9fe *INVOICE*\n"
            f"Paket: {pkg.upper()}\n"
            f"Harga: Rp{price:,}\n"
            f"DANA: `{DANA_NUMBER}`\n"
            "Status: \u23f3 *Menunggu Pembayaran*\n\n"
            "Kirim bukti transfer ke sini."
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif data == "create_panel":
        bot.answer_callback_query(call.id)
        if is_owner(uid):
            bot.send_message(call.message.chat.id, "Kirim command:\n`1gb username,idtele`", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "\u26d4 Hanya owner yang bisa create panel gratis.\nSilakan \U0001f6d2 BELI PANEL dulu.")

    elif data == "owner_menu":
        bot.answer_callback_query(call.id)
        if is_owner(uid):
            markup = types.InlineKeyboardMarkup()
            cursor.execute("SELECT * FROM orders WHERE status='pending_payment' OR status='waiting_admin'")
            pending = cursor.fetchall()
            if pending:
                for o in pending:
                    markup.add(types.InlineKeyboardButton(f"ID:{o[0]} | {o[3]} | {o[6]}", callback_data=f"review_{o[0]}"))
                bot.send_message(call.message.chat.id, "\U0001f451 *OWNER MENU \u2014 Order Pending:*", parse_mode="Markdown", reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, "Tidak ada order pending.")
        else:
            bot.send_message(call.message.chat.id, "\u26d4 Akses ditolak.")

    elif data.startswith("review_"):
        oid = int(data.split("_")[1])
        cursor.execute("SELECT * FROM orders WHERE id=?", (oid,))
        order = cursor.fetchone()
        if order:
            text = f"Order #{order[0]}\nUser ID: {order[1]}\nPaket: {order[3]}\nStatus: {order[6]}"
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("\u2705 Approve", callback_data=f"approve_{oid}"),
                types.InlineKeyboardButton("\u274c Tolak", callback_data=f"reject_{oid}")
            )
            bot.send_message(call.message.chat.id, text, reply_markup=markup)

    elif data.startswith("approve_"):
        oid = int(data.split("_")[1])
        cursor.execute("UPDATE orders SET status='approved' WHERE id=?", (oid,))
        conn.commit()
        cursor.execute("SELECT user_id, package FROM orders WHERE id=?", (oid,))
        o = cursor.fetchone()
        bot.send_message(o[0], "Pembayaran diterima \u2705\nSilakan kirim:\n`username_panel password_panel`", parse_mode="Markdown")
        bot.send_message(call.message.chat.id, f"Order #{oid} di-approve.")

    elif data.startswith("reject_"):
        oid = int(data.split("_")[1])
        cursor.execute("UPDATE orders SET status='rejected' WHERE id=?", (oid,))
        conn.commit()
        cursor.execute("SELECT user_id FROM orders WHERE id=?", (oid,))
        o = cursor.fetchone()
        bot.send_message(o[0], "Pembayaran tidak valid \u274c")
        bot.send_message(call.message.chat.id, f"Order #{oid} ditolak.")

    elif data == "back_menu":
        bot.answer_callback_query(call.id)
        start(call.message)

# ============================================================
# HANDLE MESSAGE
# ============================================================
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    uid = message.from_user.id
    log_user(message.from_user)
    text = message.text.strip()

    # Bukti transfer (foto)
    if message.photo:
        cursor.execute("SELECT id FROM orders WHERE user_id=? AND (status='pending_payment' OR status='waiting_admin') ORDER BY id DESC LIMIT 1", (uid,))
        order = cursor.fetchone()
        if order:
            cursor.execute("UPDATE orders SET status='waiting_admin' WHERE id=?", (order[0],))
            conn.commit()
            bot.send_message(OWNER_ID, f"\U0001f4e9 Bukti dari `{uid}` (@{message.from_user.username})\nOrder #{order[0]}", parse_mode="Markdown")
            bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "\u23f3 Bukti dikirim ke admin. Tunggu verifikasi.")
        else:
            bot.send_message(message.chat.id, "Tidak ada order pending.")
        return

    # Username password setelah approve
    parts = text.split()
    if len(parts) == 2:
        cursor.execute("SELECT id, package FROM orders WHERE user_id=? AND status='approved' ORDER BY id DESC LIMIT 1", (uid,))
        order = cursor.fetchone()
        if order:
            username = parts[0]
            password = parts[1]
            pkg = order[1]
            ram = PACKAGE_MAP.get(pkg, 1024)

            msg = bot.send_message(message.chat.id, "\u23f3 *Processing...*", parse_mode="Markdown")

            email = f"{username}@xinn.store"
            res_user = ptero_create_user(email, username, password, username, "XINN")

            if "attributes" not in res_user:
                bot.edit_message_text("\u274c Gagal create user panel.", message.chat.id, msg.message_id)
                return

            ptero_uid = res_user["attributes"]["id"]
            res_server = ptero_create_server(f"XINN-{username}", ptero_uid, ram)

            if "attributes" not in res_server:
                bot.edit_message_text("\u274c Gagal create server.", message.chat.id, msg.message_id)
                return

            identifier = res_server["attributes"]["identifier"]

            cursor.execute("UPDATE orders SET panel_user=?, panel_pass=?, status='completed' WHERE id=?", (username, password, order[0]))
            conn.commit()

            result = (
                "\u2705 *Panel Berhasil Dibuat!*\n\n"
                f"\U0001f4e6 Paket: {pkg.upper()}\n"
                f"\U0001f464 Username: `{username}`\n"
                f"\U0001f511 Password: `{password}`\n"
                f"\U0001f194 Server: `{identifier}`\n"
                f"\U0001f517 Panel: {PTERO_URL}\n\n"
                f"Admin: {ADMIN_USERNAME}"
            )
            bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode="Markdown")
            return

    # Command cepat owner
    parts = text.split()
    if len(parts) == 2:
        pkg_cmd = parts[0].lower()
        user_part = parts[1]

        if pkg_cmd in PACKAGE_MAP:
            if not is_owner(uid):
                bot.send_message(message.chat.id, "\u26d4 Hanya owner yang bisa menggunakan command cepat. Silakan \U0001f6d2 BELI PANEL.")
                return

            if "," not in user_part:
                bot.send_message(message.chat.id, "Format salah. Gunakan: `1gb username,idtele`", parse_mode="Markdown")
                return

            username, idtele = user_part.split(",", 1)
            password = "xinn123"
            ram = PACKAGE_MAP[pkg_cmd]

            msg = bot.send_message(message.chat.id, "\u23f3 *Processing...*", parse_mode="Markdown")

            email = f"{username}@xinn.store"
            res_user = ptero_create_user(email, username, password, username, "XINN")

            if "attributes" not in res_user:
                bot.edit_message_text("\u274c Gagal create user panel.", message.chat.id, msg.message_id)
                return

            ptero_uid = res_user["attributes"]["id"]
            res_server = ptero_create_server(f"XINN-{username}", ptero_uid, ram)

            if "attributes" not in res_server:
                bot.edit_message_text("\u274c Gagal create server.", message.chat.id, msg.message_id)
                return

            identifier = res_server["attributes"]["identifier"]

            cursor.execute("INSERT INTO orders (user_id, username, package, panel_user, panel_pass, status) VALUES (?, ?, ?, ?, ?, 'owner_free_completed')",
                           (uid, idtele, pkg_cmd, username, password))
            conn.commit()

            result = (
                "\u2705 *Panel Berhasil Dibuat!*\n\n"
                f"\U0001f4e6 Paket: {pkg_cmd.upper()}\n"
                f"\U0001f464 Username: `{username}`\n"
                f"\U0001f511 Password: `{password}`\n"
                f"\U0001f194 Server: `{identifier}`\n"
                f"\U0001f517 Panel: {PTERO_URL}\n"
                f"\U0001f451 Mode: Owner Free"
            )
            bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode="Markdown")
            return

    # Fallback
    bot.send_message(message.chat.id, "Gunakan /start untuk melihat menu.")

# ============================================================
# RUN
# ============================================================
print("\u26a1 XINN PANEL BOT running...")
print(f"\U0001f451 Owner ID: {OWNER_ID}")
bot.polling(none_stop=True)