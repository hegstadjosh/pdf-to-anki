# PDFToAnki

A powerful tool to convert PDF documents into Anki flashcards using AI-powered text processing.

## Features

- **PDF Text Extraction**: Support for both simple and complex PDF layouts
- **AI-Powered Processing**: Uses advanced language models (GPT-4, Claude, Perplexity) to generate high-quality flashcards
- **Multiple Card Types**: 
  - Basic question and answer cards
  - Cloze deletion cards
- **Customizable Prompts**: Modify how the AI processes your content
- **Modern GUI**: Built with customtkinter for a clean, modern interface
- **Multi-Model Support**: Choose between different LLM providers

## Installation

### Install with pip

1. Install from GitHub:
```bash
pip install git+https://github.com/yourusername/pdftoanki.git
```

Or clone and install in development mode:
```bash
git clone https://github.com/yourusername/pdftoanki.git
cd pdftoanki
pip install -e .
```

2. Install spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Environment Setup

Before running the application, you need to set up your API keys:

1. Create a `.env` file with your API keys (you need at least one):
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PERPLEXITY_API_KEY=your_perplexity_key
```

## Usage

Run the application:
```bash
pdftoanki
```

### Using the GUI:
1. Click "Browse" to select a PDF file
2. Choose your preferred LLM model
3. Customize the prompt if desired
4. Select additional options (PDFPlumber, Cloze cards)
5. Click "Process PDF" to generate your Anki deck

The generated `.apkg` file can be imported directly into Anki.

## Customizing Prompts

The default prompt can be modified in the GUI. Here's the structure:
```
Given the following text from a PDF, create high-quality flashcards in a question and answer format.
Follow these guidelines:
1. Create clear, concise questions that test understanding
2. Ensure answers are comprehensive but focused
3. Break complex concepts into multiple cards
4. Use proper terminology
5. Format output as:
Q: [Question]
A: [Answer]

Text:
{text}
```

## Development

### Running Tests
```bash
pytest test_pdftoanki.py
```

### Project Structure
- `app.py`: Main GUI application
- `pdf_processor.py`: PDF text extraction and processing
- `anki_generator.py`: Anki deck generation
- `llm_processor.py`: LLM integration
- `utils/llm_utils.py`: LLM API utilities
- `test_pdftoanki.py`: Test suite

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- API keys for chosen LLM providers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Uses [genanki](https://github.com/kerrickstaley/genanki) for Anki deck generation
- Powered by various LLM providers (OpenAI, Anthropic, Perplexity)

## For Developers

### Building the Executable
If you want to build the executable yourself:

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/yourusername/pdftoanki.git
cd pdftoanki
pip install -r requirements.txt
```

2. Run the build script:
```bash
python build_exe.py
```

The executable will be created in the `dist` directory. 