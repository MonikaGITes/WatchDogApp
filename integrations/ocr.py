# integrations/ocr.py

import pytesseract
from PIL import Image
from integrations.parser_vision import parse_vision


def extract_from_image(image_path: str) -> dict:
    text = pytesseract.image_to_string(
        Image.open(image_path),
        lang="pol"
    )

    return parse_vision(text)