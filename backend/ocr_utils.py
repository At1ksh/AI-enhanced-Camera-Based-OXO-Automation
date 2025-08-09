from paddleocr import PaddleOCR
import cv2
import numpy as np

# ✅ Initialize PaddleOCR globally (loaded only once)
ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    ocr_version='PP-OCRv3'
)

def run_ocr(image_bytes: bytes):
    """
    Takes raw image bytes, runs OCR, and returns all detected texts (list of strings).
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # ✅ Resize for faster inference (optional)
    max_size = 960
    h, w = img.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    results = ocr.predict(img)
    all_texts = []
    for item in results:
        all_texts.extend(item.get("rec_texts", []))
    return all_texts
