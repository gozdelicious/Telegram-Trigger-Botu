import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token'ınızı buraya yazın (veya environment variable olarak kullanın)
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'BURAYA_BOT_TOKEN_YAZIŞTIRIN')

# Ses dosyalarınızın GitHub raw URL'lerini buraya ekleyin
AUDIO_FILES = {
    'zabaha': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg',
    'zabah': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg',
    # Daha fazla ses dosyası ekleyebilirsiniz
}

# Görsel dosyalarınızın URL'lerini buraya ekleyin
IMAGE_FILES = {
    'resim': 'https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main/resimler/ornek.jpg',
}

# Otomatik yanıt kuralları
AUTO_RESPONSES = {
    'merhaba': {
        'text': '👋 Merhaba! Nasılsın?',
        'audio': 'merhaba',  # AUDIO_FILES'daki key
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
        'image': 'resim'  # IMAGE_FILES'daki key
    },
    'zabaha': {
        'text': None,
        'audio': 'zabaha', 
        'image': None,
    },
     'zabah': {
        'text': None,
        'audio': 'zabah',
        'image': None,
    }
    # Daha fazla tetikleyici kelime ekleyebilirsiniz
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gelen mesajları kontrol et ve otomatik yanıt ver"""
    
    # Mesaj yoksa veya gruplarda değilse çık
    if not update.message or not update.message.text:
        return
    
    message_text = update.message.text.lower().strip()
    
    # Her tetikleyici kelimeyi kontrol et
    for trigger, response in AUTO_RESPONSES.items():
        if trigger in message_text:
            try:
                # Metin yanıtı gönder
                if response['text']:
                    await update.message.reply_text(response['text'])
                
                # Görsel gönder
                if response['image'] and response['image'] in IMAGE_FILES:
                    image_url = IMAGE_FILES[response['image']]
                    await update.message.reply_photo(photo=image_url)
                
                # Ses kaydı gönder
                if response['audio'] and response['audio'] in AUDIO_FILES:
                    audio_url = AUDIO_FILES[response['audio']]
                    await update.message.reply_voice(voice=audio_url)
                
                logger.info(f"'{trigger}' tetikleyicisine yanıt verildi")
                break  # İlk eşleşmeden sonra dur
                
            except Exception as e:
                logger.error(f"Yanıt gönderilirken hata: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hataları yakala ve logla"""
    logger.error(f"Hata oluştu: {context.error}")

def main():
    """Bot'u başlat"""
    
    # Application oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Mesaj handler'ı ekle (tüm metin mesajlarını dinle)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    
    # Hata handler'ı ekle
    application.add_error_handler(error_handler)
    
    logger.info("Bot başlatılıyor...")
    
    # Bot'u başlat
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
