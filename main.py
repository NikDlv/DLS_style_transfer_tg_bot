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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear previous user state
    context.user_data.clear()
    
    welcome_text = (
        "👋 Добро пожаловать в бот для переноса стиля!\n\n"
        "Выберите один из вариантов генерации изображений:"
    )
    
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
        context.user_data['mode'] = 'style_transfer'
        await update.message.reply_text(
            "Отправьте сначала *контентное* изображение, затем *стилевое*.",
            parse_mode="Markdown"
        )
    elif text == "Другая генерация":
        context.user_data['mode'] = 'other'
        await update.message.reply_text("Извините! Эта функция ещё не реализована.")
    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user has selected style transfer mode
    if context.user_data.get('mode') != 'style_transfer':
        await update.message.reply_text("Пожалуйста, сначала выберите 'Перенос стиля' из меню.")
        return
    
    # Download the image
    photo = await update.message.photo[-1].get_file()
    byte_img = await photo.download_as_bytearray()
    img_tensor = load_image(byte_img)

    # Store images in context.user_data
    if 'content_image' not in context.user_data:
        context.user_data['content_image'] = img_tensor
        await update.message.reply_text("Контентное изображение получено. Теперь отправьте стилевое.")
    else:
        context.user_data['style_image'] = img_tensor
        await update.message.reply_text("Стилевое изображение получено. Выполняю перенос стиля...")
        
        try:
            # Perform style transfer
            content = context.user_data['content_image']
            style = context.user_data['style_image']
            with torch.no_grad():
                output = style_transfer(net.encode, decoder, content, style, alpha=1.0)
            
            # Prepare and send result
            buf = BytesIO()
            output = output.clamp(0, 1)
            transforms.ToPILImage()(output.squeeze(0).cpu()).save(buf, format="JPEG")
            buf.seek(0)
            await update.message.reply_photo(photo=buf, caption="Готово!")
        except Exception as e:
            print(f"Error during style transfer: {e}")
            await update.message.reply_text("⚠️ Произошла ошибка при обработке изображений. Попробуйте снова.")
        finally:
            # Reset image state but keep mode
            context.user_data.pop('content_image', None)
            context.user_data.pop('style_image', None)

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