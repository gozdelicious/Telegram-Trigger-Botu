import os
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
        'text': '👋 Merhaba! Nasılsın?',
        'audio': 'merhaba',
        'image': None
    },
    'günaydın': {
        'text': '🌅 Günaydın! Harika bir gün seninle başlasın!',
        'audio': 'günaydın',
        'image': None
    },
    'selam': {
        'text': '✨ Selam! Hoş geldin!',
        'audio': None,
        'image': None
    },
    'yardım': {
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
        'audio': None
        'image': None
        },
    'İyi geceler': {
        'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!',
        'audio': 'zabaha',
        'image': None
        },
    'seks': {
        'text': 'Şşşş,🤫🤫 bunu MZ'de konuşuyoruz. 🙂‍↔️',
        'audio': None,
        'image': None
        }
}

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot çalışıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
