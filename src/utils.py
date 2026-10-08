import re
import json


def clean_json_string(raw_str: str) -> str:
    # Regex tìm kiếm ký tự ngoặc mở đầu tiên ({ hoặc [)
    # cho đến ký tự ngoặc đóng cuối cùng (} hoặc ])
    match = re.search(r'([\{\[\(].*[\}\]\)])', raw_str, re.DOTALL)

    if match:
        return match.group(1)
    return raw_str  # Trả về chuỗi gốc nếu không tìm thấy ngoặc nào
