from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import json

from messages import get_message
from style_transfer import init_model, process_images
from user_storage import load_user_data, update_user_settings, get_user_settings, save_user_images

# Preload user data and models
user_data_store = load_user_data()

# Constants
KEYBOARD_OPTIONS = {
    'en': [["Style Transfer", "Color-Preserving", "Select a Style"],
           ["Set alpha", "Language"]],
    'ru': [["Перенос стиля", "Сохранение цветов", "Выбрать готовый стиль"],
           ["Установить alpha", "Язык"]]
}

PRE_SAVED_STYLES = {
    "Van Gogh": "test_images/style/van_gogh.jpg",
    "Monet": "test_images/style/monet.jpg",
    "Picasso": "test_images/style/picasso.jpg"
}


# --- Keyboard Helpers ---

def get_language_keyboard():
    return ReplyKeyboardMarkup([["English", "Русский"]], one_time_keyboard=True, resize_keyboard=True)

def get_styles_keyboard(lang='en'):
    styles = list(PRE_SAVED_STYLES.keys())
    keyboard = [styles[i:i+2] for i in range(0, len(styles), 2)]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

def get_keyboard(lang='en'):
    return ReplyKeyboardMarkup(KEYBOARD_OPTIONS.get(lang, KEYBOARD_OPTIONS['en']),
                                one_time_keyboard=True,
                                resize_keyboard=True)


# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command"""
    user_id = str(update.effective_user.id)
    settings = get_user_settings(user_data_store, user_id)

    lang = settings.get('lang') if settings else (
        'ru' if update.effective_user.language_code == 'ru' else 'en'
    )

    if not settings:
        update_user_settings(user_data_store, user_id, {'lang': lang})

    context.user_data['lang'] = lang

    await update.message.reply_text(
        get_message("welcome", lang),
        reply_markup=get_keyboard(lang),
        parse_mode="Markdown"
    )


# --- Message Handlers ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles all non-command text messages"""
    user_id = str(update.effective_user.id)
    user_data = context.user_data
    lang = user_data.get('lang') or get_user_settings(user_data_store, user_id).get('lang', 'en')
    user_data['lang'] = lang
    text = update.message.text
    keyboard = KEYBOARD_OPTIONS.get(lang, KEYBOARD_OPTIONS['en'])

    # Alpha input mode
    if user_data.get("awaiting_alpha"):
        try:
            alpha = float(text)
            if not (0 <= alpha <= 1):
                raise ValueError
            user_data["awaiting_alpha"] = False
            update_user_settings(user_data_store, user_id, {"alpha": alpha})
            await update.message.reply_text(get_message("alpha_set", lang).format(alpha=alpha))
        except ValueError:
            await update.message.reply_text(get_message("alpha_invalid", lang))
        return

    # Language selection mode
    if user_data.get("awaiting_language"):
        lang_map = {
            "english": "en", "английский": "en", "en": "en",
            "русский": "ru", "russian": "ru", "ru": "ru"
        }
        selected = lang_map.get(text.lower())
        if selected:
            lang = selected
            user_data["awaiting_language"] = False
            user_data["lang"] = lang
            update_user_settings(user_data_store, user_id, {"lang": lang})
            await update.message.reply_text(get_message("language_set", lang), reply_markup=get_keyboard(lang))
        else:
            await update.message.reply_text(get_message("language_invalid", lang), reply_markup=get_language_keyboard())
        return

    # Main keyboard options
    if text == keyboard[0][0]:  # Style Transfer
        user_data['mode'] = 'standard'
        await update.message.reply_text(get_message("standard_instructions", lang), parse_mode="Markdown")
    elif text == keyboard[0][1]:  # Color-Preserving
        user_data['mode'] = 'color_preserving'
        await update.message.reply_text(get_message("standard_instructions", lang), parse_mode="Markdown")
    elif text == keyboard[0][2]:  # Select Style
        await update.message.reply_text(get_message("choose_style_prompt", lang), reply_markup=get_styles_keyboard(lang))
    elif text in PRE_SAVED_STYLES:  # Pre-saved style selected
        user_data['selected_style_path'] = PRE_SAVED_STYLES[text]
        user_data['mode'] = 'selected_style'
        await update.message.reply_text(get_message("style_selected", lang).format(style=text), parse_mode="Markdown")
    elif text == keyboard[1][0]:  # Set alpha
        user_data["awaiting_alpha"] = True
        await update.message.reply_text(get_message("alpha_prompt", lang))
    elif text == keyboard[1][1]:  # Change language
        user_data["awaiting_language"] = True
        await update.message.reply_text(get_message("language_prompt", lang), reply_markup=get_language_keyboard())
    else:
        await update.message.reply_text(get_message("invalid_option", lang))


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming photo messages"""
    user_data = context.user_data
    user_id = str(update.effective_user.id)
    lang = user_data.get('lang') or get_user_settings(user_data_store, user_id).get('lang', 'en')
    user_data['lang'] = lang

    if 'mode' not in user_data:
        await update.message.reply_text(get_message("mode_not_selected", lang))
        return

    photo = await update.message.photo[-1].get_file()
    byte_img = await photo.download_as_bytearray()

    if 'content_image' not in user_data:
        user_data['content_image'] = byte_img
        user_data['media_group_id'] = update.message.media_group_id

        if user_data.get('mode') == 'selected_style':
            try:
                with open(user_data['selected_style_path'], 'rb') as f:
                    user_data['style_image'] = f.read()
                await update.message.reply_text(get_message("processing", lang))
                await perform_style_transfer(update, context)
                await update.message.reply_text(get_message("choose_option", lang), reply_markup=get_keyboard(lang))
            except Exception as e:
                print(f"Error reading style file: {e}")
                await update.message.reply_text(get_message("style_not_selected", lang))
        elif not update.message.media_group_id:
            await update.message.reply_text(get_message("content_received", lang))
    else:
        user_data['style_image'] = byte_img
        await update.message.reply_text(get_message("processing", lang))
        await perform_style_transfer(update, context)
        await update.message.reply_text(get_message("choose_option", lang), reply_markup=get_keyboard(lang))


# --- Style Transfer Core ---

async def perform_style_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Executes style transfer using the selected mode"""
    user_data = context.user_data
    user_id = str(update.effective_user.id)
    lang = user_data.get('lang') or get_user_settings(user_data_store, user_id).get('lang', 'en')
    user_data['lang'] = lang

    try:
        preserve_colors = (user_data.get('mode') == 'color_preserving')
        alpha = get_user_settings(user_data_store, user_id).get("alpha", 1.0)

        result_image = process_images(
            net=context.bot_data['net'],
            content_bytes=user_data['content_image'],
            style_bytes=user_data['style_image'],
            preserve_colors=preserve_colors,
            alpha=alpha
        )

        img_bytes = BytesIO()
        result_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        # Save user images
        save_user_images(
            user_id=user_id,
            content=user_data['content_image'],
            style=user_data['style_image'],
            output=img_bytes
        )
        img_bytes.seek(0)
        await update.message.reply_photo(
            photo=img_bytes,
            caption=get_message("success", lang)
        )
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text(get_message("error", lang))
    finally:
        user_data.pop('content_image', None)
        user_data.pop('style_image', None)


# --- Entry Point ---

def main():
    """Starts the Telegram bot"""
    print("Initializing style transfer model...")
    net = init_model()

    with open('config.json') as f:
        config = json.load(f)

    app = ApplicationBuilder().token(config['telegram_token']).build()
    app.bot_data['net'] = net

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    main()
