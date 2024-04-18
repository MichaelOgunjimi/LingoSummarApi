import os
import random

import fitz  # PyMuPDF
from docx import Document

try:
    from comtypes.client import CreateObject
except ImportError:
    # comtypes might not be available or needed on non-Windows systems
    pass


def allowed_file(filename, allowed_extensions=None):
    """
    Check if a given file name has an allowed extension.

    Args:
        filename (str): The name of the file to check.
        allowed_extensions (set, optional): A set of allowed file extensions. Defaults to {'txt', 'pdf', 'docx'}.

    Returns:
        bool: True if the file name has an allowed extension, False otherwise.
    """
    if allowed_extensions is None:
        allowed_extensions = {'txt', 'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def convert_doc_to_docx(doc_path):
    """
    Converts a .doc file to .docx using comtypes (Windows only).

    Args:
        doc_path (str): The path to the .doc file.

    Returns:
        str: The path to the converted .docx file.
    """
    word = CreateObject("Word.Application")
    doc = word.Documents.Open(doc_path)
    doc_path_new = doc_path + "x"
    doc.SaveAs2(doc_path_new, FileFormat=16)  # FileFormat=16 for docx
    doc.Close()
    word.Quit()
    return doc_path_new


def read_text_from_file(file_path):
    """
    Read the text content from a file.

    Supported file types:
    - .txt: Read the file directly.
    - .pdf: Extract the text using the PyMuPDF library.
    - .doc: Attempt to convert to .docx using the convert_doc_to_docx function, then read the .docx file.
    - .docx: Read the text using the python-docx library.

    Args:
        file_path (str): The path to the file.

    Returns:
        str or None: The text content of the file, or None if an error occurs or the file type is unsupported.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text_content = None

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()

    elif ext == '.pdf':
        with fitz.open(file_path) as doc:
            text_content = "".join(page.get_text() for page in doc)

    elif ext == '.doc':
        # Attempt to convert .doc to .docx for reading; Windows only
        try:
            docx_path = convert_doc_to_docx(file_path)
            text_content = read_text_from_file(docx_path)
            os.remove(docx_path)  # Clean up the converted file
        except Exception as e:
            print(f"Error converting .doc to .docx: {e}")
            return None

    elif ext == '.docx':
        doc = Document(file_path)
        text_content = "\n".join(para.text for para in doc.paragraphs)

    else:
        print("Unsupported file type.")
        return None

    return text_content


def get_or_generate_percentage(percentage):
    """
    Returns the input percentage if not None, otherwise generates a random percentage between 30 and 80.

    Parameters:
    - percentage (int or None): The input percentage.

    Returns:
    - int: The original percentage or a randomly generated percentage between 30 and 80.
    """
    if percentage is None or percentage == 0:
        return random.randint(30, 80)
    return percentage
