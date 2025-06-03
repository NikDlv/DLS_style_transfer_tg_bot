import torch
import torch.nn as nn
from torchvision import transforms
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from models.adain import adain_init, style_transfer
from models.functional import coral
from utils.image_io import load_image
import json

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear previous user state
    context.user_data.clear()
    
    welcome_text = (
        "👋 Welcome to the Fast Style Transfer bot!\n\n"
        "Choose one of the image generation options:"
    )
    
    reply_keyboard = [["Style transfer", "Color-preserving style transfer"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Style transfer":
        context.user_data['mode'] = 'style_transfer_standard'
        await update.message.reply_text(
             "Please send the *content* image first, then the *style* image.",
            parse_mode="Markdown"
        )
    elif text == "Color-preserving style transfer":
        context.user_data['mode'] = 'style_transfer_color_preserveng'
        await update.message.reply_text(
             "Please send the *content* image first, then the *style* image.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Please choose one of the available options.")

async def perform_style_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    net = context.bot_data['net']
    decoder = context.bot_data['decoder']
    try:
        # Perform style transfer
        content = load_image(context.user_data['content_image'])
        style= load_image(context.user_data['style_image'])
        if context.user_data.get('mode') == 'style_transfer_color_preserveng':
            style = coral(style, content)
        style = style.to('cuda').unsqueeze(0) 
        content = content.to('cuda').unsqueeze(0)
        with torch.no_grad():
            output = style_transfer(net.encode, decoder, content, style, alpha=1.0)
        
        # Prepare and send result
        buf = BytesIO()
        output = output.clamp(0, 1)
        transforms.ToPILImage()(output.squeeze(0).cpu()).save(buf, format="JPEG")
        buf.seek(0)
        await update.message.reply_photo(photo=buf, caption="Successful!")
    except Exception as e:
        print(f"Error during style transfer: {e}")
        await update.message.reply_text("⚠️ An error occurred while processing the images. Please try again.")
    finally:
        # Reset image state but keep mode
        context.user_data.pop('content_image', None)
        context.user_data.pop('style_image', None)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user has selected style transfer mode
    style_transfer_modes = ['style_transfer_standard', 'style_transfer_color_preserveng']
    if context.user_data.get('mode') not in style_transfer_modes:
        await update.message.reply_text("Please first select 'Style transfer' from the menu.")
        return

    # Download the image (always get the highest quality)
    photo = await update.message.photo[-1].get_file()
    byte_img = await photo.download_as_bytearray()
    
    # Store images in context.user_data
    if 'content_image' not in context.user_data:
        # First image - store as content
        context.user_data['content_image'] = byte_img
        context.user_data['media_group_id'] = update.message.media_group_id
        
        # Don't send response yet if this is part of an album
        if update.message.media_group_id is None:
            await update.message.reply_text("Content image received. Now please send the style image.")
    else:
        # Second image - store as style
        context.user_data['style_image'] = byte_img
        
        # Check if this is part of the same media group (album)
        if (update.message.media_group_id is not None and 
            'media_group_id' in context.user_data and 
            update.message.media_group_id == context.user_data['media_group_id']):
            
            # Album case - send combined message
            await update.message.reply_text("Content and style images received. Performing style transfer...")
            await perform_style_transfer(update, context)
        else:
            # Separate message case
            await update.message.reply_text("Style image received. Performing style transfer...")
            await perform_style_transfer(update, context)


def main():
    print("Initializing AdaIN...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    vgg, decoder, net_adain = adain_init()

    print("Starting the telegram bot...")
    with open('config.json') as config_file:
        config = json.load(config_file)
    app = ApplicationBuilder().token(config['telegram_token']).build()
    
    # Store net in bot_data to make it available to all handlers
    app.bot_data['net'] = net_adain
    app.bot_data['decoder'] = decoder

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Successful! The telegram bot is running.")
    app.run_polling()

if __name__ == '__main__':
    main()