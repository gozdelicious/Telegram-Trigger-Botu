import os
import logging
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Logging ayarları ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Bot token ---
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'BURAYA_BOT_TOKEN_YAZIŞTIRIN')

# --- Ses dosyaları ---
AUDIO_FILES = {
    'zabaha': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg',
    'zabah': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg',
    'iyi geceler': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg',
    'ne zaman bitecek': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg',
}

# --- Görsel dosyaları ---
IMAGE_FILES = {
    'resim': 'https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main/resimler/ornek.jpg',
}

# --- Otomatik yanıt kuralları ---
AUTO_RESPONSES = {
    'merhaba': {
        'text': '👋 Merhaba! Nasılsın?',
        'audio': 'merhaba',
        'image': None
    },
    'günaydın': {
        'text': '🌅 Günaydın! İyi günler dilerim!',
        'audio': 'günaydın',
        'image': None
    },
    'selam': {
        'text': '✨ Selam! Hoş geldin!',
        'audio': None,
        'image': None
    },
    'ay imdat': {
        'text': 'AY NOLDU NOLDU!!!',
        'audio': None,
        'image': 'resim'
    },
    'zabaha': {
        'text': None,
        'audio': 'zabaha',
        'image': 'resim'
    },
    'zabah': {
        'text': None,
        'audio': 'zabah',
        'image': 'resim'
    }
}

# --- Mesaj işleyici ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    message_text = update.message.text.lower().strip()
    
    for trigger, response in AUTO_RESPONSES.items():
        if trigger in message_text:
            try:
                # Metin gönder
                if response['text']:
                    await update.message.reply_text(response['text'])
                
                # Görsel gönder
                if response['image'] and response['image'] in IMAGE_FILES:
                    image_url = IMAGE_FILES[response['image']]
                    await update.message.reply_photo(photo=image_url)
                
                # Ses gönder
                if response['audio'] and response['audio'] in AUDIO_FILES:
                    audio_url = AUDIO_FILES[response['audio']]
                    try:
                        # Ses dosyasını indir
                        response_data = requests.get(audio_url)
                        response_data.raise_for_status()

                        # BytesIO ile Telegram'a gönder
                        audio_file = BytesIO(response_data.content)
                        audio_file.name = "ses.ogg"
                        await update.message.reply_voice(voice=audio_file)

                    except Exception as e:
                        logger.error(f"Ses gönderiminde hata: {e}")
                
                logger.info(f"'{trigger}' tetikleyicisine yanıt verildi")
                break
                
            except Exception as e:
                logger.error(f"Yanıt gönderilirken hata: {e}")

# --- Hata yakalayıcı ---
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Hata oluştu: {context.error}")

# --- Ana fonksiyon ---
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    logger.info("Bot başlatılıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
