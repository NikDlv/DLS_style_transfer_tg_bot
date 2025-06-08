import json
import os
from datetime import datetime
from io import BytesIO

USER_DATA_FILE = "user_data/user_preferences.json"
USER_DATA_DIR = 'user_data'

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_settings(user_data, user_id):
    return user_data.get(str(user_id), {})

def update_user_settings(user_data, user_id, updates: dict):
    uid = str(user_id)
    if uid not in user_data:
        user_data[uid] = {}
    user_data[uid].update(updates)
    save_user_data(user_data)


def save_user_images(user_id: str, content: bytes, style: bytes, output: BytesIO):
    """
    Saves content, style, and output images in a user-specific timestamped folder.
    """
    # Create user directory and timestamped subfolder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    user_dir = os.path.join(USER_DATA_DIR, user_id, f"result_{timestamp}")
    os.makedirs(user_dir, exist_ok=True)

    # Save content image
    with open(os.path.join(user_dir, "content.jpg"), "wb") as f:
        f.write(content)

    # Save style image
    with open(os.path.join(user_dir, "style.jpg"), "wb") as f:
        f.write(style)

    # Save output image
    output_path = os.path.join(user_dir, "output.jpg")
    with open(output_path, "wb") as f:
        f.write(output.getbuffer())

    print(f"Saved images for user {user_id} in {user_dir}")