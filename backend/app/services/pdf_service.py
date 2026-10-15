"""PDF text extraction, question segmentation, and checksum computation."""

import os
import re
import hashlib
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF


def compute_file_checksum(file_path: str) -> str:
    """Compute SHA-256 checksum of a file to detect exact duplicates."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
    """
    Extract text per page from a PDF using PyMuPDF.
    Returns metadata and structured text per page.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    doc = fitz.open(file_path)
    pages_text = []
    total_words = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        words = len(text.split())
        total_words += words
        pages_text.append({
            "page_number": page_num + 1,
            "text": text,
            "word_count": words
        })

    is_scanned = total_words < (len(doc) * 15)  # If very few words per page, likely scanned image

    return {
        "page_count": len(doc),
        "total_words": total_words,
        "is_scanned": is_scanned,
        "pages": pages_text,
        "full_text": "\n\n".join(p["text"] for p in pages_text)
    }


def parse_and_segment_questions(full_text: str, default_marks: int = 7) -> List[Dict[str, Any]]:
    """
    Segment questions and sub-questions from extracted text using regex patterns.
    Recognizes typical RGPV formats like:
      - Q.1 (a) ... [7]
      - 1. (a) ... (7 Marks)
      - Question 2: ...
    """
    questions = []
    lines = full_text.splitlines()
    current_q_num = 1
    current_sub = "a"
    current_buffer = []
    current_page = 1
    current_marks = default_marks

    # Regular expressions for question headers
    q_pattern = re.compile(r"^(?:Q(?:uestion)?\.?\s*(\d+)|\b(\d+)\.\s*(?:\(([a-d]|[ivx]+)\))?)", re.IGNORECASE)
    sub_pattern = re.compile(r"^\(([a-d]|[ivx]+)\)\s*", re.IGNORECASE)
    marks_pattern = re.compile(r"\[(\d+)\s*(?:marks?)?\]|\((\d+)\s*(?:marks?)?\)", re.IGNORECASE)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for page indicator if any
        if "Page " in stripped or "--- Page" in stripped:
            page_match = re.search(r"Page\s*(\d+)", stripped, re.IGNORECASE)
            if page_match:
                current_page = int(page_match.group(1))

        # Check for marks on the line
        m_match = marks_pattern.search(stripped)
        detected_marks = None
        if m_match:
            marks_str = m_match.group(1) or m_match.group(2)
            if marks_str and marks_str.isdigit():
                detected_marks = int(marks_str)

        # Check for new main question or sub-question
        q_match = q_pattern.match(stripped)
        sub_match = sub_pattern.match(stripped)

        if q_match:
            # Save previous question if exists
            if current_buffer:
                questions.append({
                    "question_number": current_q_num,
                    "sub_question": current_sub,
                    "question_text": " ".join(current_buffer).strip(),
                    "marks": current_marks,
                    "page_number": current_page,
                    "confidence_score": 0.90,
                })
                current_buffer = []

            matched_q = q_match.group(1) or q_match.group(2)
            if matched_q:
                current_q_num = int(matched_q)
            current_sub = q_match.group(3) or "a"
            current_marks = detected_marks or default_marks
            cleaned_line = q_pattern.sub("", stripped).strip()
            if cleaned_line:
                current_buffer.append(cleaned_line)
        elif sub_match:
            if current_buffer:
                questions.append({
                    "question_number": current_q_num,
                    "sub_question": current_sub,
                    "question_text": " ".join(current_buffer).strip(),
                    "marks": current_marks,
                    "page_number": current_page,
                    "confidence_score": 0.92,
                })
                current_buffer = []
            current_sub = sub_match.group(1)
            current_marks = detected_marks or default_marks
            cleaned_line = sub_pattern.sub("", stripped).strip()
            if cleaned_line:
                current_buffer.append(cleaned_line)
        else:
            if detected_marks:
                current_marks = detected_marks
            current_buffer.append(stripped)

    # Flush last question
    if current_buffer:
        questions.append({
            "question_number": current_q_num,
            "sub_question": current_sub,
            "question_text": " ".join(current_buffer).strip(),
            "marks": current_marks,
            "page_number": current_page,
            "confidence_score": 0.85,
        })

    return questions
