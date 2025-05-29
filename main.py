import torch
import torch.nn as nn
from torchvision import transforms
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from models.adain import decoder, vgg, Net, style_transfer
from utils.image_io import load_image
import json

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

decoder = decoder
vgg = vgg

decoder.eval()
vgg.eval()

decoder.load_state_dict(torch.load('models_weights/decoder.pth'))
vgg.load_state_dict(torch.load('models_weights/vgg_normalised.pth'))
vgg = nn.Sequential(*list(vgg.children())[:31])

vgg.to(device)
decoder.to(device)

net = Net(vgg, decoder).to(device).eval()

# хранение изображений по chat_id
user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Welcome message
    welcome_text = (
        "👋 Добро пожаловать в бот для переноса стиля!\n\n"
        "Выберите один из вариантов генерации изображений:"
    )
    
    # Create a keyboard with two options
    reply_keyboard = [["Перенос стиля", "Другая генерация"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Перенос стиля":
        await update.message.reply_text(
            "Отправьте сначала *контентное* изображение, затем *стилевое*.",
            parse_mode="Markdown"
        )
    elif text == "Другая генерация":
        await update.message.reply_text("Извините! Эта функция ещё не реализована.")
    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user has selected style transfer option
    if update.message.text != "Перенос стиля" and "content" not in user_images.get(update.message.chat_id, {}):
        await update.message.reply_text("Пожалуйста, сначала выберите 'Перенос стиля' из меню.")
        return
    
    user_id = update.message.chat_id
    photo = await update.message.photo[-1].get_file()
    byte_img = await photo.download_as_bytearray()
    img_tensor = load_image(byte_img)

    if user_id not in user_images or "content" not in user_images[user_id]:
        user_images[user_id] = {"content": img_tensor}
        await update.message.reply_text("Контентное изображение получено. Теперь отправьте стилевое.")
    else:
        user_images[user_id]["style"] = img_tensor
        await update.message.reply_text("Стилевое изображение получено. Выполняю перенос стиля...")
        content = user_images[user_id]["content"]
        style = user_images[user_id]["style"]
        with torch.no_grad():
            output = style_transfer(net.encode, decoder, content, style, alpha=1.0)
        buf = BytesIO()
        output = output.clamp(0, 1)
        transforms.ToPILImage()(output.squeeze(0).cpu()).save(buf, format="JPEG")
        buf.seek(0)
        await update.message.reply_photo(photo=buf, caption="Готово!")
        user_images[user_id] = {}  # сброс

def main():
    
    with open('config.json') as config_file:
        config = json.load(config_file)
    app = ApplicationBuilder().token(config['telegram_token']).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    app.run_polling()

if __name__ == '__main__':
    main()