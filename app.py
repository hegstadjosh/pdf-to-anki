import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pdf_processor import PDFProcessor
from anki_generator import AnkiDeckGenerator
from llm_processor import LLMProcessor
from typing import Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFToAnkiApp:
    def __init__(self):
        """Initialize the PDFToAnki application."""
        self.window = ctk.CTk()
        self.window.title("PDFToAnki")
        self.window.geometry("1000x800")  # Increased window size
        
        # Initialize processors
        self.pdf_processor = PDFProcessor()
        self.anki_generator = AnkiDeckGenerator()
        self.llm_processor = LLMProcessor()
        
        # Track current state
        self.current_pdf: Optional[str] = None
        self.output_path: str = os.path.expanduser("~")
        self.extracted_text: str = ""
        
        self._create_gui()
        
    def _create_gui(self):
        """Create the GUI elements."""
        # Create main container with two columns
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column for PDF processing
        self.left_column = ctk.CTkFrame(self.main_container)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right column for deck generation
        self.right_column = ctk.CTkFrame(self.main_container)
        self.right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === Left Column (PDF Processing) ===
        # File selection
        self.file_frame = ctk.CTkFrame(self.left_column)
        self.file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_label = ctk.CTkLabel(self.file_frame, text="PDF File:")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        self.file_path = ctk.CTkEntry(self.file_frame, width=300)
        self.file_path.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_btn = ctk.CTkButton(
            self.file_frame, 
            text="Browse", 
            command=self._browse_pdf
        )
        self.browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # PDF Options
        self.pdf_options_frame = ctk.CTkFrame(self.left_column)
        self.pdf_options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Page Range Frame
        self.page_range_frame = ctk.CTkFrame(self.pdf_options_frame)
        self.page_range_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.page_range_label = ctk.CTkLabel(self.page_range_frame, text="Page Range:")
        self.page_range_label.pack(side=tk.LEFT, padx=5)
        
        self.start_page = ctk.CTkEntry(self.page_range_frame, width=60, placeholder_text="Start")
        self.start_page.pack(side=tk.LEFT, padx=2)
        
        self.page_range_to = ctk.CTkLabel(self.page_range_frame, text="to")
        self.page_range_to.pack(side=tk.LEFT, padx=2)
        
        self.end_page = ctk.CTkEntry(self.page_range_frame, width=60, placeholder_text="End")
        self.end_page.pack(side=tk.LEFT, padx=2)
        
        self.total_pages_label = ctk.CTkLabel(self.page_range_frame, text="")
        self.total_pages_label.pack(side=tk.LEFT, padx=5)
        
        # PDF Options (continued)
        self.use_plumber_var = tk.BooleanVar(value=False)
        self.use_plumber_cb = ctk.CTkCheckBox(
            self.pdf_options_frame,
            text="Use PDFPlumber",
            variable=self.use_plumber_var
        )
        self.use_plumber_cb.pack(side=tk.LEFT, padx=5)
        
        self.process_pdf_btn = ctk.CTkButton(
            self.pdf_options_frame,
            text="Process PDF",
            command=self._process_pdf
        )
        self.process_pdf_btn.pack(side=tk.RIGHT, padx=5)
        
        # Text Preview
        self.preview_label = ctk.CTkLabel(self.left_column, text="Extracted Text Preview:")
        self.preview_label.pack(padx=5, pady=(10,2), anchor=tk.W)
        
        self.text_preview = ctk.CTkTextbox(self.left_column, height=400)
        self.text_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === Right Column (Deck Generation) ===
        # LLM Model selection
        self.model_frame = ctk.CTkFrame(self.right_column)
        self.model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.model_label = ctk.CTkLabel(self.model_frame, text="LLM Model:")
        self.model_label.pack(side=tk.LEFT, padx=5)
        
        self.model_var = tk.StringVar(value="gpt-4o")
        self.model_menu = ctk.CTkOptionMenu(
            self.model_frame,
            values=["gpt-4o", "claude-3-sonnet-20240229", "sonar-pro"],
            variable=self.model_var,
            command=self._on_model_change
        )
        self.model_menu.pack(side=tk.LEFT, padx=5)
        
        # Prompt customization
        self.prompt_label = ctk.CTkLabel(self.right_column, text="Custom Prompt:")
        self.prompt_label.pack(padx=5, pady=2, anchor=tk.W)
        
        # Add prompt buttons frame
        self.prompt_buttons_frame = ctk.CTkFrame(self.right_column)
        self.prompt_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.insert_text_btn = ctk.CTkButton(
            self.prompt_buttons_frame,
            text="Insert Extracted Text",
            command=self._insert_extracted_text
        )
        self.insert_text_btn.pack(side=tk.LEFT, padx=5)
        
        self.prompt_text = ctk.CTkTextbox(self.right_column, height=200)
        self.prompt_text.pack(fill=tk.X, padx=5, pady=2)
        self.prompt_text.insert("1.0", self.llm_processor.default_prompt)
        
        # Deck Options
        self.deck_options_frame = ctk.CTkFrame(self.right_column)
        self.deck_options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Deck Name Frame
        self.deck_name_frame = ctk.CTkFrame(self.deck_options_frame)
        self.deck_name_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.deck_name_label = ctk.CTkLabel(self.deck_name_frame, text="Deck Name:")
        self.deck_name_label.pack(side=tk.LEFT, padx=5)
        
        self.deck_name_entry = ctk.CTkEntry(self.deck_name_frame, width=200)
        self.deck_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Cloze Option
        self.create_cloze_var = tk.BooleanVar(value=False)
        self.create_cloze_cb = ctk.CTkCheckBox(
            self.deck_options_frame,
            text="Create Cloze Cards",
            variable=self.create_cloze_var
        )
        self.create_cloze_cb.pack(side=tk.LEFT, padx=5)
        
        # Progress and status
        self.status_label = ctk.CTkLabel(self.right_column, text="")
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        self.progress_bar = ctk.CTkProgressBar(self.right_column)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=2)
        self.progress_bar.set(0)
        
        # Action buttons
        self.button_frame = ctk.CTkFrame(self.right_column)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.generate_btn = ctk.CTkButton(
            self.button_frame,
            text="Generate Deck",
            command=self._generate_deck
        )
        self.generate_btn.pack(side=tk.RIGHT, padx=5)
        
        self.output_btn = ctk.CTkButton(
            self.button_frame,
            text="Set Output Directory",
            command=self._set_output_dir
        )
        self.output_btn.pack(side=tk.RIGHT, padx=5)
        
    def _browse_pdf(self):
        """Open file dialog to select PDF."""
        filename = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.current_pdf = filename
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, filename)
            
            # Update total pages
            total_pages = self.pdf_processor.get_page_count(filename)
            if total_pages > 0:
                self.total_pages_label.configure(text=f"(Total: {total_pages})")
                # Set default end page to total pages
                self.end_page.delete(0, tk.END)
                self.end_page.insert(0, str(total_pages))
                # Set default deck name
                default_name = Path(filename).stem
                self.deck_name_entry.delete(0, tk.END)
                self.deck_name_entry.insert(0, default_name)
            else:
                self.total_pages_label.configure(text="")
            
    def _set_output_dir(self):
        """Open directory dialog to set output location."""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )
        if directory:
            self.output_path = directory
            
    def _on_model_change(self, choice):
        """Handle model selection change."""
        self.llm_processor = LLMProcessor(model=choice)
        # Update default prompt
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", self.llm_processor.default_prompt)
        
    def _update_status(self, message: str, progress: float = None):
        """Update status message and progress bar."""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.window.update()
        
    def _process_pdf(self):
        """Process the selected PDF file."""
        if not self.current_pdf:
            messagebox.showerror("Error", "Please select a PDF file first.")
            return
            
        try:
            # Get page range
            start_page = None
            end_page = None
            
            start_text = self.start_page.get().strip()
            end_text = self.end_page.get().strip()
            
            if start_text:
                try:
                    start_page = int(start_text)
                    if start_page < 1:
                        raise ValueError("Start page must be at least 1")
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid start page: {str(e)}")
                    return
            
            if end_text:
                try:
                    end_page = int(end_text)
                    total_pages = self.pdf_processor.get_page_count(self.current_pdf)
                    if end_page > total_pages:
                        raise ValueError(f"End page cannot exceed total pages ({total_pages})")
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid end page: {str(e)}")
                    return
            
            # Disable the process button while working
            self.process_pdf_btn.configure(state="disabled")
            self._update_status("Starting PDF processing...", 0.1)
            self.window.update()
            
            # Clear previous text
            self.text_preview.delete("1.0", tk.END)
            self.extracted_text = ""
            
            logger.info(f"Processing PDF: {self.current_pdf} (pages {start_page or 1} to {end_page or 'end'})")
            self._update_status("Extracting text from PDF...", 0.3)
            self.window.update()
            
            # Extract text with progress updates
            if self.use_plumber_var.get():
                logger.info("Using PDFPlumber for extraction")
                self._update_status("Extracting text with PDFPlumber...", 0.4)
            else:
                logger.info("Using PyPDF2 for extraction")
                self._update_status("Extracting text with PyPDF2...", 0.4)
            
            self.window.update()
            
            # Extract text
            self.extracted_text = self.pdf_processor.extract_text(
                self.current_pdf,
                use_plumber=self.use_plumber_var.get(),
                start_page=start_page,
                end_page=end_page
            )
            
            # Log the result
            if self.extracted_text:
                text_length = len(self.extracted_text)
                logger.info(f"Successfully extracted {text_length} characters")
                
                # Update preview with chunks to handle large texts
                self._update_status("Updating preview...", 0.7)
                self.window.update()
                
                # Insert text in chunks to handle large documents
                chunk_size = 1000
                for i in range(0, len(self.extracted_text), chunk_size):
                    chunk = self.extracted_text[i:i + chunk_size]
                    self.text_preview.insert(tk.END, chunk)
                    self.window.update()
                
                page_range_text = f" (pages {start_page or 1} to {end_page or 'end'})"
                self._update_status(f"PDF processed successfully! ({text_length} characters extracted){page_range_text}", 1.0)
            else:
                logger.error("No text was extracted from the PDF")
                messagebox.showerror("Error", "No text could be extracted from the PDF. The file might be empty, corrupted, or contain only images.")
                self._update_status("Extraction failed", 0)
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            messagebox.showerror("Error", f"An error occurred while processing the PDF:\n{str(e)}")
            self._update_status("Error occurred", 0)
        
        finally:
            # Re-enable the process button
            self.process_pdf_btn.configure(state="normal")
            self.window.update()
    
    def _generate_deck(self):
        """Generate Anki deck from the current text."""
        try:
            # Get text (either from PDF or manual input)
            text = self.extracted_text if self.extracted_text else self.text_preview.get("1.0", tk.END)
            if not text.strip():
                messagebox.showerror("Error", "No text to process. Please load a PDF or enter text manually.")
                return
            
            # Update status
            self._update_status("Processing text with LLM...", 0.3)
            
            # Get custom prompt
            custom_prompt = self.prompt_text.get("1.0", tk.END).strip()
            if not custom_prompt:
                custom_prompt = None
            
            # Generate Q&A pairs
            qa_pairs = self.llm_processor.process_text(text, custom_prompt)
            
            if not qa_pairs:
                messagebox.showerror("Error", "No flashcards could be generated.")
                return
            
            # Get deck name from input or use default
            deck_name = self.deck_name_entry.get().strip()
            if not deck_name:
                # Use default name if entry is empty
                source_name = Path(self.current_pdf).stem if self.current_pdf else "manual_input"
                deck_name = f"{source_name}_deck"
                # Update the entry with default name
                self.deck_name_entry.delete(0, tk.END)
                self.deck_name_entry.insert(0, deck_name)
            
            # Create Anki deck
            self._update_status("Creating Anki deck...", 0.7)
            output_file = self.anki_generator.create_deck(
                qa_pairs,
                deck_name,
                source=deck_name  # Use deck name as source for better organization
            )
            
            # Create cloze cards if requested
            if self.create_cloze_var.get():
                self._update_status("Creating cloze cards...", 0.9)
                cloze_items = self.llm_processor.create_cloze_deletions(text)
                if cloze_items:
                    self.anki_generator.create_cloze_deck(
                        cloze_items,
                        deck_name,
                        source=deck_name  # Use deck name as source for better organization
                    )
            
            self._update_status("Done!", 1.0)
            messagebox.showinfo(
                "Success",
                f"Anki deck created successfully!\nOutput: {output_file}"
            )
            
        except Exception as e:
            logger.error(f"Error generating deck: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self._update_status("Error occurred", 0)
            
    def _insert_extracted_text(self):
        """Insert the extracted text into the prompt at the correct position."""
        if not self.extracted_text and not self.text_preview.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "No text available to insert. Please process a PDF first.")
            return
            
        try:
            # Get the current prompt text
            prompt_text = self.prompt_text.get("1.0", tk.END)
            
            # Find the position of "Text:" in the prompt
            text_marker = "Text:"
            text_pos = prompt_text.find(text_marker)
            
            if text_pos == -1:
                # If "Text:" not found, append it
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", prompt_text.strip() + "\n\nText:\n")
                text_pos = self.prompt_text.get("1.0", tk.END).find(text_marker)
            
            # Get the text to insert
            text_to_insert = self.extracted_text if self.extracted_text else self.text_preview.get("1.0", tk.END).strip()
            
            # Find the position after "Text:"
            prompt_content = self.prompt_text.get("1.0", tk.END)
            insert_pos = text_pos + len(text_marker)
            
            # Delete any existing text after "Text:"
            self.prompt_text.delete(f"1.0 + {insert_pos}c", tk.END)
            
            # Insert the new text with proper formatting
            self.prompt_text.insert(tk.END, f"\n{text_to_insert}")
            
            # Show success message
            self.status_label.configure(text="Text inserted into prompt")
            
        except Exception as e:
            logger.error(f"Error inserting text into prompt: {e}")
            messagebox.showerror("Error", f"Failed to insert text: {str(e)}")
            
    def run(self):
        """Start the application."""
        self.window.mainloop()

if __name__ == "__main__":
    app = PDFToAnkiApp()
    app.run() 