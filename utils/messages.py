MESSAGES = {
    "en": {
        "welcome": """
👋 Welcome to the Fast Style Transfer Bot!

✨ Choose one of the image generation options:

1️⃣  **Style Transfer** 🎨
Apply a style from any image to your content photo while keeping the original composition.

2️⃣  **Color-Preserving** 🌈
Keep your original photo's colors while applying the style's textures and patterns.

3️⃣  **Select a Style** 🖼️
Select a famous painting style (Van Gogh, Monet, Picasso) and apply it to your photo.

⚙️ You can also adjust the strength of the style transfer using the **"Set alpha"** command.
Choose a value between 0 and 1 — higher values mean stronger stylization.

🌐 To change the bot's language, use the **"Language"** command and select your preferred language.
""",
        "standard_instructions": """
📌 Please follow these steps:

1️⃣ Send the *content* image first
2️⃣ Then send the *style* image

💡 You can also send both images in one message!
""",
        "content_received": "✅ Content image received! Now send the style image.",
        "style_received": "✅ Style image received! Starting style transfer...",
        "processing": "🔄 Performing style transfer...",
        "success": "🎨 Style transfer complete!",
        "error": "⚠️ An error occurred during processing. Please try again.",
        "mode_not_selected": "❌ Please first select a style transfer mode from the menu.",
        "invalid_option": "❌ Please choose one of the available options.",
        "alpha_prompt": "🔧 Please enter a value for alpha (between 0 and 1):",
        "alpha_set": "✅ Alpha set to {alpha}.",
        "alpha_invalid": "❌ Invalid value. Please enter a number between 0 and 1.",
        "language_prompt": "🌍 Please choose your language:",
        "language_set": "✅ Language set to English.",
        "language_invalid": "❌ Invalid choice, please select a language from the keyboard.",
        "choose_style_prompt": "🖼️ Please select a style from the list below:",
        "style_selected": "🎨 Style {style} selected! Now please send the content image.",
        "choose_option": "📋 Please select an option from the menu."
    },

    "ru": {
        "welcome": """
👋 Добро пожаловать в бота для переноса стиля!

✨ Выберите один из вариантов:

1️⃣  **Перенос стиля** 🎨
Примените стиль из любого изображения к вашему фото, сохранив оригинальную композицию.

2️⃣  **Сохранение цветов** 🌈
Сохраните оригинальные цвета вашего фото, применяя только текстуры и паттерны стиля.

3️⃣  **Выбрать готовый стиль** 🖼️
Выберите стиль известного художника (Ван Гог, Моне, Пикассо) и примените его к своей фотографии.

⚙️ Вы также можете настроить силу переноса стиля с помощью команды **"Установить alpha"**.
Укажите значение от 0 до 1 — чем больше значение, тем сильнее эффект стилизации.

🌐 Чтобы изменить язык бота, используйте команду **"Язык"** и выберите предпочитаемый язык.
""",
        "standard_instructions": """
📌 Инструкция:

1️⃣ Сначала отправьте *контентное* изображение
2️⃣ Затем отправьте *стилевое* изображение

💡 Можно отправить оба изображения одним сообщением!
""",
        "content_received": "✅ Контентное изображение получено! Теперь отправьте стилевое.",
        "style_received": "✅ Стилевое изображение получено! Начинаю перенос стиля...",
        "processing": "🔄 Выполняю перенос стиля...",
        "success": "🎨 Готово! Перенос стиля выполнен.",
        "error": "⚠️ Произошла ошибка при обработке. Пожалуйста, попробуйте ещё раз.",
        "mode_not_selected": "❌ Сначала выберите режим переноса стиля.",
        "invalid_option": "❌ Пожалуйста, выберите один из доступных вариантов.",
        "alpha_prompt": "🔧 Пожалуйста, введите значение alpha (от 0 до 1):",
        "alpha_set": "✅ Значение alpha установлено на {alpha}.",
        "alpha_invalid": "❌ Неверное значение. Введите число от 0 до 1.",
        "language_prompt": "🌍 Пожалуйста, выберите язык:",
        "language_set": "✅ Язык установлен на русский.",
        "language_invalid": "❌ Неверный выбор, пожалуйста, выберите язык с клавиатуры.",
        "choose_style_prompt": "🖼️ Пожалуйста, выберите стиль из списка ниже:",
        "style_selected": "🎨 Стиль {style} выбран! Теперь отправьте фото для переноса стиля.",
        "choose_option": "📋 Выберите опцию из списка."
    }
}


def get_message(key, lang='en'):
    """Retrieve a localized message by key and language code."""
    return MESSAGES.get(lang, {}).get(key, MESSAGES['en'].get(key, ""))
