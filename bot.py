from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests

BOT_TOKEN = '7749680839:AAEqXGBPbfw8ZSAtD3ANByXvNHvXqjRnjfo'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirimkan 6 digit BIN (contoh: 457173) untuk mendapatkan info kartu.")

async def lookup_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = update.message.text.strip()
    if not bin_number.isdigit() or len(bin_number) != 6:
        await update.message.reply_text("Masukkan 6 digit angka BIN yang valid.")
        return

    url = f"https://data.handyapi.com/bin/{bin_number}"
    headers = {'Accept-Version': '3'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        result = f"""
🔎 Info BIN {bin_number}:
• Scheme: {data.get('Scheme', 'N/A')}
• Type: {data.get('Type', 'N/A')}
• CardTier: {data.get('CardTier', 'N/A')}
• Bank: {data.get('Issuer', 'N/A')}
• Negara: {data.get('Country', {}).get('Name', 'N/A')}
        """.strip()
    else:
        result = "BIN tidak ditemukan atau API error."

    await update.message.reply_text(result)

# Set up bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_bin))

app.run_polling()
