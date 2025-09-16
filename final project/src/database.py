import json
import os

DATA_DIR = '../data'
if not os.path.exists(DATA_DIR):
    print("icant fins")
    os.makedirs(DATA_DIR)

def get_file_path(filename):
    return os.path.join(DATA_DIR, filename)

def load_data(filename):
    """داده‌ها را از یک فایل JSON می‌خواند."""
    filepath = get_file_path(filename)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(filename, data):
    """داده‌ها را در یک فایل JSON ذخیره می‌کند."""
    filepath = get_file_path(filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)