import PyPDF2
import pdfplumber
import re
from typing import List, Tuple, Optional
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor."""
        # No spaCy model loading
        pass

    def get_page_count(self, pdf_path: str) -> int:
        """Get the total number of pages in the PDF."""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            return 0

    def extract_text_pypdf(self, pdf_path: str, start_page: int = None, end_page: int = None) -> str:
        """
        Extract text using PyPDF2.
        
        Args:
            pdf_path: Path to PDF file
            start_page: First page to extract (1-based index)
            end_page: Last page to extract (1-based index)
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                # Convert to 0-based index and handle None values
                start_idx = (start_page - 1) if start_page is not None else 0
                end_idx = min(end_page or total_pages, total_pages)
                
                # Validate page range
                if start_idx < 0 or start_idx >= total_pages:
                    raise ValueError(f"Start page {start_page} is out of range (1-{total_pages})")
                if end_idx <= start_idx:
                    raise ValueError(f"End page must be greater than start page")
                
                text = "\n".join([
                    reader.pages[i].extract_text() 
                    for i in range(start_idx, end_idx)
                ])
                return text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return ""

    def extract_text_pdfplumber(self, pdf_path: str, start_page: int = None, end_page: int = None) -> str:
        """
        Extract text using pdfplumber (better for complex layouts).
        
        Args:
            pdf_path: Path to PDF file
            start_page: First page to extract (1-based index)
            end_page: Last page to extract (1-based index)
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                # Convert to 0-based index and handle None values
                start_idx = (start_page - 1) if start_page is not None else 0
                end_idx = min(end_page or total_pages, total_pages)
                
                # Validate page range
                if start_idx < 0 or start_idx >= total_pages:
                    raise ValueError(f"Start page {start_page} is out of range (1-{total_pages})")
                if end_idx <= start_idx:
                    raise ValueError(f"End page must be greater than start page")
                
                text = "\n".join([
                    pdf.pages[i].extract_text() 
                    for i in range(start_idx, end_idx)
                ])
                return text
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            return ""

    def extract_text(self, pdf_path: str, use_plumber: bool = False, start_page: int = None, end_page: int = None) -> str:
        """
        Extract text from PDF using specified method.
        
        Args:
            pdf_path: Path to PDF file
            use_plumber: Whether to use pdfplumber instead of PyPDF2
            start_page: First page to extract (1-based index)
            end_page: Last page to extract (1-based index)
        """
        if use_plumber:
            return self.extract_text_pdfplumber(pdf_path, start_page, end_page)
        return self.extract_text_pypdf(pdf_path, start_page, end_page)

    def parse_structured_qa(self, text: str) -> List[Tuple[str, str]]:
        """Parse text with explicit Q&A markers."""
        qa_pairs = []
        
        # Try different Q&A patterns
        patterns = [
            r"Q(?:uestion)?[\s:]+(.*?)A(?:nswer)?[\s:]+(.*?)(?=Q(?:uestion)?[\s:]|$)",
            r"###[\s]*Q(?:uestion)?[\s:]*(.*?)###[\s]*A(?:nswer)?[\s:]*(.*?)(?=###[\s]*Q|$)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches:
                qa_pairs.extend([
                    (q.strip(), a.strip()) 
                    for q, a in matches 
                    if q.strip() and a.strip()
                ])
                
        return qa_pairs

    def is_question(self, text: str) -> bool:
        """Determine if a sentence is likely a question using regex patterns."""
        # Check for question marks
        if "?" in text:
            return True
            
        # Check for question words
        question_words = {"what", "why", "how", "when", "where", "which", "who", "whose", "whom"}
        first_word = text.split()[0].lower() if text.split() else ""
        if first_word in question_words:
            return True
            
        # Check for auxiliary verbs at start
        aux_verbs = {"is", "are", "was", "were", "do", "does", "did", "have", "has", "had", "can", "could", "should", "would", "will"}
        if first_word in aux_verbs:
            return True
            
        return False

    def parse_unstructured_text(self, text: str) -> List[Tuple[str, str]]:
        """Parse text without explicit Q&A markers using regex-based sentence splitting."""
        qa_pairs = []
        
        # Split into sentences using regex
        # This pattern looks for sentence boundaries (period, question mark, exclamation point)
        # followed by a space and uppercase letter or end of string
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = [s.strip() for s in re.split(sentence_pattern, text) if s.strip()]
        
        for i, sent in enumerate(sentences[:-1]):
            if self.is_question(sent):
                # Use next sentence as answer
                qa_pairs.append((sent, sentences[i + 1]))
                
        return qa_pairs

    def parse_content(self, text: str) -> List[Tuple[str, str]]:
        """Parse content into Q&A pairs using both structured and unstructured approaches."""
        # First try structured parsing
        qa_pairs = self.parse_structured_qa(text)
        
        # If no structured pairs found, try unstructured parsing
        if not qa_pairs:
            qa_pairs = self.parse_unstructured_text(text)
            
        return qa_pairs

    def process_pdf(self, pdf_path: str, use_plumber: bool = False) -> List[Tuple[str, str]]:
        """Process PDF and return Q&A pairs."""
        text = self.extract_text(pdf_path, use_plumber)
        if not text:
            logger.error("No text extracted from PDF")
            return []
            
        return self.parse_content(text) 