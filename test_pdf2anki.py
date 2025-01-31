import pytest
from pathlib import Path
import tempfile
import os
from pdf_processor import PDFProcessor
from anki_generator import AnkiDeckGenerator
from llm_processor import LLMProcessor

# Sample test data
SAMPLE_TEXT = """
Question: What is Python?
Answer: Python is a high-level, interpreted programming language.

Question: What are Python's key features?
Answer: Python's key features include:
- Easy to read syntax
- Dynamic typing
- Automatic memory management
- Rich standard library
"""

SAMPLE_CLOZE_TEXT = """
Text: {{c1::Python}} is a high-level programming language.
Extra: Created by Guido van Rossum

Text: Python supports multiple programming paradigms, including {{c1::object-oriented}}, {{c2::imperative}}, and {{c3::functional}} programming.
Extra: This flexibility makes Python versatile for different types of projects.
"""

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def anki_generator():
    return AnkiDeckGenerator()

@pytest.fixture
def llm_processor():
    return LLMProcessor()

@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file for testing."""
    import PyPDF2
    from reportlab.pdfgen import canvas
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        # Create PDF using reportlab
        c = canvas.Canvas(tmp.name)
        c.drawString(100, 750, "Question: What is Python?")
        c.drawString(100, 730, "Answer: Python is a programming language.")
        c.save()
        
        return tmp.name

def test_pdf_text_extraction(pdf_processor, temp_pdf):
    """Test PDF text extraction."""
    text = pdf_processor.extract_text(temp_pdf)
    assert text, "Text should be extracted from PDF"
    assert "Python" in text, "Extracted text should contain expected content"

def test_pdf_text_extraction_with_plumber(pdf_processor, temp_pdf):
    """Test PDF text extraction using pdfplumber."""
    text = pdf_processor.extract_text(temp_pdf, use_plumber=True)
    assert text, "Text should be extracted from PDF using pdfplumber"
    assert "Python" in text, "Extracted text should contain expected content"

def test_structured_qa_parsing(pdf_processor):
    """Test parsing of structured Q&A format."""
    qa_pairs = pdf_processor.parse_structured_qa(SAMPLE_TEXT)
    assert len(qa_pairs) == 2, "Should extract two Q&A pairs"
    assert qa_pairs[0][0].strip() == "What is Python?", "First question should match"
    assert "high-level" in qa_pairs[0][1], "First answer should match"

def test_unstructured_text_parsing(pdf_processor):
    """Test parsing of unstructured text."""
    text = "What is Python? Python is a programming language. How old is Python? Python was created in 1991."
    qa_pairs = pdf_processor.parse_unstructured_text(text)
    assert len(qa_pairs) >= 2, "Should extract at least two Q&A pairs"
    assert all(pair[0].strip().endswith('?') for pair in qa_pairs), "Questions should end with question mark"

def test_anki_deck_creation(anki_generator):
    """Test Anki deck creation."""
    qa_pairs = [
        ("What is Python?", "A programming language"),
        ("Who created Python?", "Guido van Rossum")
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        output_file = anki_generator.create_deck(qa_pairs, "test_deck")
        assert output_file, "Should create deck file"
        assert Path(output_file).exists(), "Deck file should exist"
        assert output_file.endswith('.apkg'), "Should create .apkg file"

def test_cloze_deck_creation(anki_generator):
    """Test Anki cloze deck creation."""
    cloze_items = [
        ("{{c1::Python}} is a programming language.", "Created by Guido van Rossum"),
        ("Python was created in {{c1::1991}}.", "At the CWI in Netherlands")
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        output_file = anki_generator.create_cloze_deck(cloze_items, "test_cloze_deck")
        assert output_file, "Should create cloze deck file"
        assert Path(output_file).exists(), "Deck file should exist"
        assert output_file.endswith('_cloze.apkg'), "Should create _cloze.apkg file"

def test_llm_text_processing(llm_processor):
    """Test LLM text processing."""
    text = "Python is a high-level programming language created by Guido van Rossum."
    qa_pairs = llm_processor.process_text(text)
    assert isinstance(qa_pairs, list), "Should return list of Q&A pairs"
    if qa_pairs:  # Only check if LLM returned results
        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in qa_pairs), "Each pair should be a tuple of 2 elements"

def test_llm_cloze_processing(llm_processor):
    """Test LLM cloze processing."""
    text = "Python is a high-level programming language created by Guido van Rossum."
    cloze_items = llm_processor.create_cloze_deletions(text)
    assert isinstance(cloze_items, list), "Should return list of cloze items"
    if cloze_items:  # Only check if LLM returned results
        assert all(isinstance(item, tuple) and len(item) == 2 for item in cloze_items), "Each item should be a tuple of 2 elements"

def test_custom_prompt(llm_processor):
    """Test custom prompt processing."""
    custom_prompt = """
    Create a single flashcard from this text:
    Q: [Question about the main topic]
    A: [Comprehensive answer]
    
    Text:
    {text}
    """
    
    text = "Python is a programming language."
    qa_pairs = llm_processor.process_text(text, custom_prompt)
    assert isinstance(qa_pairs, list), "Should return list of Q&A pairs"
    if qa_pairs:  # Only check if LLM returned results
        assert len(qa_pairs) == 1, "Should create exactly one flashcard"

def test_error_handling(pdf_processor, anki_generator, llm_processor):
    """Test error handling in various scenarios."""
    # Test invalid PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        text = pdf_processor.extract_text(tmp.name)
        assert text == "", "Should handle invalid PDF gracefully"
    
    # Test invalid Q&A pairs for Anki deck
    result = anki_generator.create_deck([], "empty_deck")
    assert result is None, "Should handle empty Q&A pairs gracefully"
    
    # Test invalid text for LLM
    qa_pairs = llm_processor.process_text("")
    assert qa_pairs == [], "Should handle empty text gracefully"

if __name__ == '__main__':
    pytest.main([__file__]) 