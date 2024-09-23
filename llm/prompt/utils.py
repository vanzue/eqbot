import json


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def safe_json_loads(data, default=None):
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default