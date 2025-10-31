import os
import json
import requests
import logging
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

# --- LOG AYARLARI ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- ENV DEĞİŞKENLERİ ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY", "").strip()
JSONBIN_BIN_ID = os.getenv("JSONBIN_BIN_ID", "").strip()

# Başlangıçta kontrol et
if not all([BOT_TOKEN, JSONBIN_API_KEY, JSONBIN_BIN_ID]):
    logger.error("❌ HATALI YAPILANDIRMA!")
    logger.error(f"BOT_TOKEN: {'✅ Var' if BOT_TOKEN else '❌ Yok'}")
    logger.error(f"JSONBIN_API_KEY: {'✅ Var' if JSONBIN_API_KEY else '❌ Yok'}")
    logger.error(f"JSONBIN_BIN_ID: {'✅ Var' if JSONBIN_BIN_ID else '❌ Yok'}")
    exit(1)

logger.info(f"✅ API Key başlangıcı: {JSONBIN_API_KEY[:10]}...")
logger.info(f"✅ Bin ID: {JSONBIN_BIN_ID}")

# --- JSONBIN AYARLARI ---
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_API_KEY
}


# --- VERİ YÜKLEME (GELİŞTİRİLMİŞ) ---
def load_data():
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        logger.info(f"JSONBin yanıt kodu: {res.status_code}")
        
        if res.status_code == 200:
            try:
                full_response = res.json()
                logger.info(f"Gelen yanıt: {full_response}")
                
                data = full_response.get("record", [])
                
                # Eğer record bir liste değilse (örneğin dict ise), boş liste döndür
                if not isinstance(data, list):
                    logger.warning(f"Record bir liste değil, tip: {type(data)}")
                    return []
                
                logger.info(f"{len(data)} kayıt yüklendi ✅")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse hatası: {e}")
                logger.error(f"Yanıt içeriği: {res.text}")
                return []
        else:
            logger.warning(f"JSONBin veri okunamadı: {res.status_code}")
            logger.warning(f"Yanıt: {res.text}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"İstek hatası: {e}")
        return []


# --- VERİ KAYDETME ---
def save_data(data):
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
    res = requests.put(url, headers=HEADERS, json=data)
    if res.status_code == 200:
        logger.info("Veri başarıyla kaydedildi ✅")
    else:
        logger.error(f"JSONBin kaydetme hatası: {res.status_code} - {res.text}")


# --- MULTİMEDYA KAYNAKLARI ---
AUDIO_FILES = {
    'merhaba': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/merhaba.ogg',
    'günaydın': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/gunaydin.ogg',
    'zabaha': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/sesler/zabaha-kadar.ogg'
}

IMAGE_FILES = {
    'kader': 'https://raw.githubusercontent.com/gozdelicious/Telegram-Trigger-Botu/main/resimler/Belgin_Sarılmışer.jpg'
}


# --- OTOMATİK CEVAPLAR ---
AUTO_RESPONSES = {
    'merhaba': {'text': '👋 MERHABA! Ay heyecanlandım. İlk merhaba diyen ben olmalıyım. HER ZAMAN!', 'audio': None, 'image': None},
    'günaydın': {'text': '🌅 Günaydın! Güzel bir gün olsun!', 'audio': None, 'image': None},
    'selam': {'text': '✨ Selam cnms! Hoş geldin!', 'audio': None, 'image': None},
    'imdat': {'text': 'AY NOLUYO NOLUYOOO 😱😱😱', 'audio': None, 'image': 'resim'},
    'zabah': {'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!', 'audio': 'zabaha', 'image': None},
    'iyi geceler': {'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!', 'audio': None, 'image': None},
    'seks': {'text': 'Şşşş,🤫🤫 bunu MZ\'de konuşuyoruz. 🙂‍↔️', 'audio': None, 'image': None},
    'kader': {'text': 'Kader diyemezsin, sen kendin ettin.', 'audio': None, 'image': 'kader'},
    'İyi geceler': {'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!', 'audio': None, 'image': None},
    'görüşürüz': {'text': 'Ciao 👋', 'audio': None, 'image': None},
}


# --- KOMUTLAR ---
async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Environment ve API bağlantısını test et"""
    msg = "🔍 **Sistem Kontrolü:**\n\n"
    msg += f"✅ Bot Token: {'Var' if BOT_TOKEN else '❌ YOK'}\n"
    msg += f"✅ API Key: {'Var' if JSONBIN_API_KEY else '❌ YOK'}\n"
    msg += f"✅ Bin ID: {'Var' if JSONBIN_BIN_ID else '❌ YOK'}\n\n"
    
    # JSONBin bağlantı testi
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        msg += f"📡 JSONBin Yanıt: {res.status_code}\n"
        if res.status_code == 401:
            msg += "❌ API Key geçersiz!\n"
        elif res.status_code == 200:
            msg += "✅ Bağlantı başarılı!\n"
    except Exception as e:
        msg += f"❌ Bağlantı hatası: {e}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Kaydedilecek bir yazı girmelisin. Örnek:\n/save Kırmızı Pazartesi - Gabriel García Márquez")
        return

    data = load_data()
    data.append(text)
    save_data(data)
    await update.message.reply_text(f"✅ Kitap kaydedildi!\n📝 {text}")


async def kitaplar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info("kitaplar_command çağrıldı")
        data = load_data()
        
        logger.info(f"Yüklenen veri: {data}")
        logger.info(f"Veri tipi: {type(data)}")
        logger.info(f"Veri uzunluğu: {len(data) if isinstance(data, list) else 'Liste değil'}")
        
        if not data:
            await update.message.reply_text("📭 Henüz kayıtlı kitap yok veya veri alınamadı.")
            return
            
        message = "\n".join([f"{i+1}. {item}" for i, item in enumerate(data)])
        await update.message.reply_text(f"📚 Kayıtlı Kitaplar:\n\n{message}")
    except Exception as e:
        logger.exception("kitaplar_command hata")
        await update.message.reply_text(f"❌ Bir hata oluştu: {e}")


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


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("Henüz kayıtlı kitap yok 📭")
        return
    
    temp_path = "/tmp/kitaplar.json"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    await update.message.reply_document(
        document=InputFile(temp_path, filename="kitaplar.json"),
        caption="📦 Kayıtlı kitaplar dosyası gönderildi!"
    )


async def edit_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❗Kullanım: /edit <id> <yeni_yazı>")
        return

    try:
        entry_id = int(args[0]) - 1
    except ValueError:
        await update.message.reply_text("⚠️ Geçerli bir sayı gir lütfen. (örnek: /edit 2 Yeni metin)")
        return

    new_text = " ".join(args[1:])
    data = load_data()

    if 0 <= entry_id < len(data):
        old_text = data[entry_id]
        data[entry_id] = new_text
        save_data(data)
        await update.message.reply_text(
            f"✏️ **Düzenlendi:**\n\nEski: {old_text}\nYeni: {new_text}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Bu numarada bir kayıt bulunamadı.")


# --- MESAJ İŞLEYİCİ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    print(f"Gelen mesaj: {text}")

    # 🔍 Mesajdaki tüm trigger'ların pozisyonlarını bul
    trigger_positions = {
        trigger: text.find(trigger)
        for trigger in AUTO_RESPONSES.keys()
        if trigger in text
    }

    # Hiç trigger yoksa çık
    if not trigger_positions:
        return

    # 🎯 En önce geçen trigger'ı bul
    triggered = min(trigger_positions, key=trigger_positions.get)
    response = AUTO_RESPONSES[triggered]

    caption = response.get('text')

    # --- FOTOĞRAF + (CAPTION + OPSİYONEL SES) ---
    if response.get('image'):
        image_url = IMAGE_FILES.get(response['image'])
        if image_url:
            await update.message.reply_photo(photo=image_url, caption=caption)

            # Ek olarak ses varsa gönder
            if response.get('audio'):
                audio_url = AUDIO_FILES.get(response['audio'])
                if audio_url:
                    resp = requests.get(audio_url)
                    if resp.status_code == 200:
                        await update.message.reply_audio(
                            audio=InputFile(BytesIO(resp.content), filename=f"{response['audio']}.mp3"),
                            caption=caption
                        )
        return  # işlem tamam, çık

    # --- SADECE SES (CAPTION'LA BİRLİKTE) ---
    if response.get('audio') and not response.get('image'):
        audio_url = AUDIO_FILES.get(response['audio'])
        if audio_url:
            resp = requests.get(audio_url)
            if resp.status_code == 200:
                await update.message.reply_audio(
                    audio=InputFile(BytesIO(resp.content), filename=f"{response['audio']}.mp3"),
                    caption=caption
                )
        return

    # --- SADECE METİN ---
    if response.get('text') and not response.get('image') and not response.get('audio'):
        await update.message.reply_text(response['text'])


# --- ANA FONKSİYON ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("save", save_command))
    app.add_handler(CommandHandler("kitaplar", kitaplar_command))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(CommandHandler("find", find_command))
    app.add_handler(CommandHandler("export", export_command))
    app.add_handler(CommandHandler("edit", edit_entry))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("test", test_command))

    logger.info("🤖 Bot çalışıyor...")
    app.run_polling()


if __name__ == "__main__":
    main()
