import os
import json
import requests
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- ÇEVRE DEĞİŞKENİNDEN TOKEN ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- SES VE GÖRSEL KAYNAKLARI ---
AUDIO_FILES = {
    'merhaba': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/merhaba.ogg',
    'günaydın': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/gunaydin.ogg',
    'zabaha': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg'
}

IMAGE_FILES = {
    'resim': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/resimler/yardim.jpg'
}

# --- OTOMATİK CEVAPLAR ---
AUTO_RESPONSES = {
    'merhaba': {
        'text': '👋 MERHABA! Ay heyecanlandım. İlk merhaba diyen ben olmalıyım. HER ZAMAN!',
        'audio': None,
        'image': None
    },
    'günaydın': {
        'text': '🌅 Günaydın! Güzel bir gün olsun!',
        'audio': None,
        'image': None
    },
    'selam': {
        'text': '✨ Selam cnms! Hoş geldin!',
        'audio': None,
        'image': None
    },
    'imdat': {
        'text': 'AY NOLUYO NOLUYOOO 😱😱😱',
        'audio': None,
        'image': 'resim'
    },
    'zabah': {
        'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!',
        'audio': 'zabaha',
        'image': None
    },
    'iyi geceler': {
        'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!',
        'audio': None,
        'image': None
        },
    'İyi geceler': {
        'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!',
        'audio': 'zabaha',
        'image': None
    },   
    'seks': {
        'text': 'Şşşş,🤫🤫 bunu MZ\'de konuşuyoruz. 🙂‍↔️',
        'audio': None,
        'image': None
    }
}

# --- DATA DOSYASI ---
DATA_FILE = "kitaplar.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
# --- KOMUTLAR ---
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Kaydedilecek bir yazı girmelisin. Örnek:\n/save Kırmızı Pazartesi - Gabriel García Márquez")
        return
    data = load_data()
    data.append(text)
    save_data(data)
    await update.message.reply_text(f"✅ Yazı kaydedildi!\n📝 {text}")

async def kitaplar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("Henüz kayıtlı yazı yok 📭")
        return
    message = "\n".join([f"{i+1}. {item}" for i, item in enumerate(data)])
    await update.message.reply_text(f"📚 Kayıtlı Yazılar:\n\n{message}")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Silmek istediğin kayıt numaralarını yazmalısın. Örnek:\n/delete 1 3 5")
        return
    data = load_data()
    to_delete = []
    for arg in args:
        if arg.isdigit():
            index = int(arg) - 1
            if 0 <= index < len(data):
                to_delete.append(index)
    if not to_delete:
        await update.message.reply_text("⚠️ Geçerli bir numara bulunamadı.")
        return
    to_delete.sort(reverse=True)
    deleted_items = [data.pop(i) for i in to_delete]
    save_data(data)
    deleted_text = "\n".join([f"- {item}" for item in deleted_items])
    await update.message.reply_text(f"🗑️ Silinen Kayıtlar:\n{deleted_text}")

async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args).strip().lower()
    if not query:
        await update.message.reply_text("Aramak istediğin kelimeyi yazmalısın. Örnek:\n/find aşk")
        return
    data = load_data()
    results = [(i+1, item) for i, item in enumerate(data) if query in item.lower()]
    if not results:
        await update.message.reply_text(f"🔍 '{query}' kelimesini içeren kayıt bulunamadı.")
        return
    message = "\n".join([f"{i}. {item}" for i, item in results])
    await update.message.reply_text(f"🔍 Arama Sonuçları ({query}):\n\n{message}")

# --- MESAJ İŞLEYİCİ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    print(f"Gelen mesaj: {text}")

    for trigger, response in AUTO_RESPONSES.items():
        if trigger in text:
            # Metin gönder
            if response['text']:
                await update.message.reply_text(response['text'])

            # Ses gönder
            if response['audio']:
                audio_url = AUDIO_FILES.get(response['audio'])
                if audio_url:
                    resp = requests.get(audio_url)
                    if resp.status_code == 200:
                        await update.message.reply_voice(
                            voice=InputFile(BytesIO(resp.content), filename=f"{response['audio']}.ogg")
                        )
                    else:
                        await update.message.reply_text("🎧 Ses dosyası indirilemedi.")
            
            # Görsel gönder
            if response['image']:
                image_url = IMAGE_FILES.get(response['image'])
                if image_url:
                    await update.message.reply_photo(photo=image_url)

            break  # ilk eşleşmede çık

# --- ANA FONKSİYON ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("save", save_command))
    app.add_handler(CommandHandler("kitaplar", kitaplar_command))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(CommandHandler("find", find_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot çalışıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
