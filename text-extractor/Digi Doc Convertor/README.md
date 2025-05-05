# 📄 Document Digitizer

A powerful Streamlit-based web app for extracting and digitizing text from scanned documents and handwritten images using multiple OCR engines: **Tesseract**, **EasyOCR**, and **OCR.Space**. Includes intelligent layout detection (paragraphs, bullets, tables) and export options in DOCX, PDF, and TXT formats.

---

## 🚀 Features

- 🔍 **Multiple OCR Engines**
  - Tesseract OCR (local)
  - EasyOCR (deep learning based)
  - OCR.Space API (cloud-based)
- 🧠 **Smart Layout Detection**
  - Paragraphs
  - Bullet points
  - Simple tables
- 📝 **Editable Extracted Text**
- 💾 **Export Options**
  - DOCX
  - PDF
  - TXT

---

## 🛠️ Requirements

Install dependencies via pip:

```bash
pip install -r requirements.txt
```

Ensure [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) is installed and update its path in the script:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 📦 Dependencies

- `streamlit`
- `pytesseract`
- `opencv-python`
- `numpy`
- `Pillow`
- `python-docx`
- `fpdf`
- `requests`
- `easyocr` (optional, installed dynamically)

---

## 🚧 Usage

1. Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

2. Upload a document image (`.jpg`, `.jpeg`, `.png`, `.bmp`).
3. Select your preferred OCR engine.
4. View, edit, and export the extracted text.

---

## 🔐 OCR.Space API

OCR.Space requires an API key. A demo key is prefilled in the script, but for production use, get your own key from [ocr.space](https://ocr.space/OCRAPI).

---

## 📎 Notes

- EasyOCR requires `torch`. It's loaded conditionally to avoid conflicts.
- The layout detection is basic and intended for quick insights, not full document structure parsing.

---

## 📃 License

MIT License. Free to use, modify, and distribute.
