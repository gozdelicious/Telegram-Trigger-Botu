import os
import json
import requests
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import logging
logging.basicConfig(level=logging.INFO)
...
logging.info("Veri başarıyla kaydedildi ✅")


# --- BOT TOKEN ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- KALICI DOSYA YOLU ---
DATA_FILE = "/mnt/data/kitaplar.json"

# --- VOLUME KLASÖRÜNÜ OLUŞTUR ---
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# --- DOSYA YOKSA BOŞ OLUŞTUR ---
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)


# --- VERİ OKUMA / YAZMA FONKSİYONLARI ---

import requests
import os
import json

JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")
BIN_ID = os.getenv("BIN_ID") # JSONBin'de oluşturduğun bin’in ID'si

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Master-Key": JSONBIN_API_KEY
}
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    """JSONBin'den kayıtları güvenli şekilde çeker. Hata varsa ayrıntılı log yazar."""
    BIN_ID = os.getenv("BIN_ID")
    JSONBIN_API_KEY = os.getenv("JSONBIN_API_KEY")

    if not BIN_ID:
        logger.error("BIN_ID environment variable yok!")
        return []
    if not JSONBIN_API_KEY:
        logger.error("JSONBIN_API_KEY environment variable yok!")
        return []

    url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
    headers = {
        "X-Master-Key": JSONBIN_API_KEY,
        "Accept": "application/json"
    }

    try:
        logger.info(f"JSONBin isteği: {url} (timeout=6s)")
        r = requests.get(url, headers=headers, timeout=6)
        logger.info(f"JSONBin status: {r.status_code}")
        if r.status_code == 200:
            body = r.json()
            # Güvenlik: record yoksa boş liste dön
            record = body.get("record")
            if isinstance(record, list):
                logger.info(f"JSONBin'den {len(record)} kayıt çekildi.")
                return record
            else:
                logger.warning("JSONBin'den gelen 'record' alanı liste değil; döküm: %s", type(record))
                return []
        else:
            logger.error("JSONBin hata: %s", r.text)
            return []
    except requests.exceptions.Timeout:
        logger.exception("JSONBin isteği timeout oldu.")
        return []
    except Exception:
        logger.exception("JSONBin yüklemesi sırasında beklenmeyen hata oluştu.")
        return []


def save_data(data):
    """Kayıtları JSONBin'e kaydeder"""
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        res = requests.put(url, headers=headers, data=json.dumps(data, ensure_ascii=False))
        if res.status_code == 200:
            print("Veri başarıyla kaydedildi ✅")
        else:
            print("Kaydetme hatası:", res.text)
    except Exception as e:
        print("Kaydetme sırasında hata:", e)



# --- MULTİMEDYA KAYNAKLARI ---
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
    'merhaba': {'text': '👋 MERHABA! Ay heyecanlandım. İlk merhaba diyen ben olmalıyım. HER ZAMAN!', 'audio': None, 'image': None},
    'günaydın': {'text': '🌅 Günaydın! Güzel bir gün olsun!', 'audio': None, 'image': None},
    'selam': {'text': '✨ Selam cnms! Hoş geldin!', 'audio': None, 'image': None},
    'imdat': {'text': 'AY NOLUYO NOLUYOOO 😱😱😱', 'audio': None, 'image': 'resim'},
    'zabah': {'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!', 'audio': 'zabaha', 'image': None},
    'iyi geceler': {'text': 'NEREYE? ZABAĞA GADAR BURDAYIZ BUGÜN!', 'audio': None, 'image': None},
    'seks': {'text': 'Şşşş,🤫🤫 bunu MZ\'de konuşuyoruz. 🙂‍↔️', 'audio': None, 'image': None}
}


# --- KOMUTLAR ---
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
        data = load_data()
        if not data:
            await update.message.reply_text("📭 Henüz kayıtlı kitap yok veya veri alınamadı. (Logs'a bakın)")
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
    
    # JSONBin'deki veriyi geçici bir dosyaya yaz
    temp_path = "/tmp/kitaplar.json"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Telegram’a gönder
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

    for trigger, response in AUTO_RESPONSES.items():
        if trigger in text:
            if response['text']:
                await update.message.reply_text(response['text'])
            if response['audio']:
                audio_url = AUDIO_FILES.get(response['audio'])
                if audio_url:
                    resp = requests.get(audio_url)
                    if resp.status_code == 200:
                        await update.message.reply_voice(
                            voice=InputFile(BytesIO(resp.content), filename=f"{response['audio']}.ogg")
                        )
            if response['image']:
                image_url = IMAGE_FILES.get(response['image'])
                if image_url:
                    await update.message.reply_photo(photo=image_url)
            break


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

    print("🤖 Bot çalışıyor...")
    app.run_polling()


if __name__ == "__main__":
    main()
