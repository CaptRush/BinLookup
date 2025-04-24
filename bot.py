import logging
import time
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔧 Logging untuk debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🔐 Ambil token dari environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🕒 Dictionary untuk menyimpan waktu terakhir user melakukan lookup
user_last_lookup = {}

# 🟢 /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/start command from user: {update.effective_user.id}")
    await update.message.reply_text("Halo! Kirimkan 6 digit BIN (contoh: 457173) untuk mendapatkan info kartu.")

# 🔎 Handler untuk lookup BIN dengan rate limiting
async def lookup_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()
    cooldown = 10  # waktu tunggu dalam detik

    # ⏳ Cek apakah user harus tunggu dulu
    last_lookup = user_last_lookup.get(user_id, 0)
    if now - last_lookup < cooldown:
        remaining = int(cooldown - (now - last_lookup))
        await update.message.reply_text(f"⏳ Tunggu {remaining} detik sebelum lookup lagi.")
        return

    # ✅ Update waktu lookup terakhir user
    user_last_lookup[user_id] = now

    bin_number = update.message.text.strip()
    logging.info(f"Received BIN: {bin_number} from user: {user_id}")

    if not bin_number.isdigit() or len(bin_number) != 6:
        await update.message.reply_text("Masukkan 6 digit angka BIN yang valid.")
        return

    # 🔗 Panggil API binlist
    url = f"https://data.handyapi.com/bin/{bin_number}"
    headers = {'Accept-Version': '3'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # akan men-trigger exception jika status code != 200
        data = response.json()
        result = f"""
🔎 Info BIN {bin_number}:
• Scheme: {data.get('Scheme', 'N/A')}
• Type: {data.get('Type', 'N/A')}
• CardTier: {data.get('CardTier', 'N/A')}
• Bank: {data.get('Issuer', 'N/A')}
• Negara: {data.get('Country', {}).get('Name', 'N/A')}
        """.strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error saat akses API: {e}")
        result = "❌ Terjadi kesalahan saat mengambil data."

    await update.message.reply_text(result)

# 🚀 Run bot
if __name__ == "__main__":
    logging.info("Starting bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_bin))
    app.run_polling()
