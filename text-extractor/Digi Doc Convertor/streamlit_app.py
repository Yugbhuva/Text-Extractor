import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import os
import tempfile
from docx import Document
from fpdf import FPDF
import re
import requests

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Import EasyOCR conditionally to avoid torch conflicts
st.set_page_config(
    page_title="Document Digitizer",
    page_icon="📄",
    layout="wide"
)

# Initialize EasyOCR reader (lazy loading - with safe import)
@st.cache_resource
def load_easyocr_reader():
    try:
        import easyocr
        return easyocr.Reader(['en'])
    except Exception as e:
        st.error(f"Error loading EasyOCR: {str(e)}")
        return None

# Function to extract text using pytesseract
def extract_text_with_tesseract(image):
    return pytesseract.image_to_string(image)

# Function to extract text using EasyOCR
def extract_text_with_easyocr(image, reader):
    results = reader.readtext(np.array(image))
    text = " ".join([result[1] for result in results])
    return text

# Function to extract text using OCR.Space
def extract_text_with_ocr_space(image_file, api_key):
    url_api = "https://api.ocr.space/parse/image"
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': 'eng',
        'OCREngine': 2
    }

    with image_file as f:
        response = requests.post(url_api, files={"filename": f}, data=payload)

    try:
        result = response.json()
        return result["ParsedResults"][0]["ParsedText"]
    except:
        return "Error: Unable to extract text."

# Function to detect layout elements
def detect_layout(extracted_text):
    # Detect paragraphs
    paragraphs = re.split(r'\n\s*\n', extracted_text)
    
    # Detect bullet points
    bullets = re.findall(r'(?:^|\n)(?:\s*[-•*]\s+.+(?:\n\s+.+)*)+', extracted_text)
    
    # Simple table detection (consecutive lines with similar column counts)
    possible_tables = []
    lines = extracted_text.split('\n')
    for i in range(len(lines)-2):
        if '|' in lines[i] and '|' in lines[i+1] and '|' in lines[i+2]:
            pipe_count_i = lines[i].count('|')
            pipe_count_i1 = lines[i+1].count('|')
            pipe_count_i2 = lines[i+2].count('|')
            if abs(pipe_count_i - pipe_count_i1) <= 1 and abs(pipe_count_i1 - pipe_count_i2) <= 1:
                table_text = '\n'.join(lines[i:i+3])
                possible_tables.append(table_text)
    
    return {
        "paragraphs": paragraphs,
        "bullets": bullets,
        "tables": possible_tables
    }

# Function to save as DOCX
def save_as_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    
    # Save to a BytesIO object
    docx_io = io.BytesIO()
    doc.save(docx_io)
    docx_io.seek(0)
    
    return docx_io

# Function to save as PDF
def save_as_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split text into lines to handle newlines
    lines = text.split('\n')
    for line in lines:
        # Encode the line for PDF compatibility
        pdf.cell(0, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
    
    # Save to a BytesIO object
    pdf_io = io.BytesIO()
    pdf.output(pdf_io)
    pdf_io.seek(0)
    
    return pdf_io

# Function to save as TXT
def save_as_txt(text):
    txt_io = io.BytesIO()
    txt_io.write(text.encode())
    txt_io.seek(0)
    
    return txt_io

# Main application
def main():
    st.title("📄 Document Digitizer")
    st.write("Convert scanned documents and handwritten text to digital format.")
    
    # Sidebar for options
    st.sidebar.title("Options")
    ocr_engine = st.sidebar.radio(
        "Select OCR Engine",
        ["Tesseract OCR", "EasyOCR", "OCR.Space"]
    )
    
    ocr_space_api_key = ""
    if ocr_engine == "OCR.Space":
        ocr_space_api_key = "e56a0d6b2d88957" #use your own API free key for free api key read readme.MD in the file i explain how to get new free api key
    
    # File uploader
    uploaded_file = st.file_uploader("Upload document image", type=["jpg", "jpeg", "png", "bmp"])
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        st.subheader("Original Document")
        st.image(image, width=600)
        
        # Extract text based on selected OCR engine
        with st.spinner("Extracting text..."):
            if ocr_engine == "Tesseract OCR":
                extracted_text = extract_text_with_tesseract(image)
            elif ocr_engine == "EasyOCR":
                reader = load_easyocr_reader()
                if reader is None:
                    st.error("EasyOCR failed to load. Please try Tesseract OCR instead.")
                    extracted_text = extract_text_with_tesseract(image)
                else:
                    extracted_text = extract_text_with_easyocr(image, reader)
            else:  # OCR.Space
                if not ocr_space_api_key:
                    st.error("Please enter your OCR.Space API key in the sidebar.")
                    return
                # Need to reset file pointer for OCR.Space
                uploaded_file.seek(0)
                extracted_text = extract_text_with_ocr_space(uploaded_file, ocr_space_api_key)
        
        # Detect layout
        layout_info = detect_layout(extracted_text)
        
        # Display extracted text in an editable text area
        st.subheader("Extracted Text")
        st.write("Review and edit the text if needed:")
        
        # Show detected layout elements if any
        if layout_info["tables"]:
            st.write("Detected possible tables:")
            for table in layout_info["tables"][:2]:  # Show just first few for UI clarity
                st.code(table)
        
        if layout_info["bullets"]:
            st.write("Detected bullet points:")
            for bullet in layout_info["bullets"][:2]:  # Show just first few for UI clarity
                st.code(bullet)
        
        # Editable text area
        edited_text = st.text_area("Edit text if needed:", extracted_text, height=300)
        
        # Export options
        st.subheader("Export Options")
        export_format = st.radio("Select Export Format:", ["DOCX", "PDF", "TXT"])
        
        if st.button("Export Document"):
            if edited_text:
                st.success(f"Document ready for export as {export_format}!")
                
                if export_format == "DOCX":
                    docx_data = save_as_docx(edited_text)
                    st.download_button(
                        label="⬇️ Download DOCX",
                        data=docx_data,
                        file_name="document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                elif export_format == "PDF":
                    pdf_data = save_as_pdf(edited_text)
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_data,
                        file_name="document.pdf",
                        mime="application/pdf"
                    )
                else:  # TXT
                    txt_data = save_as_txt(edited_text)
                    st.download_button(
                        label="⬇️ Download TXT",
                        data=txt_data,
                        file_name="document.txt",
                        mime="text/plain"
                    )
            else:
                st.error("No text to export. Please try again with a different image.")

if __name__ == "__main__":
    main()