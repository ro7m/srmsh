import dataiku
from dataiku.customrecipe import get_recipe_config, get_input_names, get_output_names
from PIL import Image
import pytesseract
import pandas as pd
from io import BytesIO
import fitz  # PyMuPDF
import pdf2image

def list_files_in_s3(bucket_name, prefix):
    s3_client = dataiku.core.s3.S3Client(bucket=bucket_name)
    files = s3_client.list_keys(prefix=prefix)
    return files

def download_file_from_s3(bucket_name, file_key):
    s3_client = dataiku.core.s3.S3Client(bucket=bucket_name)
    file_data = s3_client.read_bytes(file_key)
    return file_data

def perform_ocr_on_image(image):
    text = pytesseract.image_to_string(image)
    return text

def perform_ocr_on_pdf(file_data):
    pdf_document = fitz.open(stream=file_data, filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def perform_ocr(file_data, file_type):
    if file_type == "image":
        image = Image.open(BytesIO(file_data))
        return perform_ocr_on_image(image)
    elif file_type == "pdf":
        return perform_ocr_on_pdf(file_data)
    else:
        raise ValueError("Unsupported file type")

def extract_information(text, prompt):
    llm_client = dataiku.apinode.dss_plugin_llm.LLMClient()
    response = llm_client.extract(text, prompt)
    return response

def main(bucket_name, prefix, file_type, prompt):
    files = list_files_in_s3(bucket_name, prefix)
    text_accumulator = ""
    
    for file_key in files:
        if (file_type == "all" or
            (file_type == "image" and file_key.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))) or
            (file_type == "pdf" and file_key.lower().endswith('.pdf'))):
            file_data = download_file_from_s3(bucket_name, file_key)
            text_accumulator += perform_ocr(file_data, file_type)
    
    extracted_info = extract_information(text_accumulator, prompt)
    return extracted_info
