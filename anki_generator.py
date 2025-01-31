import genanki
import random
from typing import List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnkiDeckGenerator:
    def __init__(self):
        """Initialize the Anki deck generator with default model."""
        # Create a unique model ID
        self.model_id = random.randrange(1 << 30, 1 << 31)
        
        # Default basic model
        self.basic_model = genanki.Model(
            model_id=self.model_id,
            name='PDFToAnki Basic',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'Source'}  # To track which PDF the card came from
            ],
            templates=[{
                'name': 'Card 1',
                'qfmt': '{{Question}}<br><br><div class="source"><em>Source: {{Source}}</em></div>',
                'afmt': '''{{FrontSide}}
                        <hr id="answer">
                        {{Answer}}'''
            }],
            css='''
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    text-align: left;
                    color: black;
                    background-color: white;
                    padding: 20px;
                }
                .source {
                    font-size: 12px;
                    color: #666;
                }
            '''
        )
        
        # Cloze deletion model
        self.cloze_model = genanki.Model(
            model_id=self.model_id + 1,
            name='PDFToAnki Cloze',
            model_type=genanki.Model.CLOZE,
            fields=[
                {'name': 'Text'},
                {'name': 'Back Extra'},
                {'name': 'Source'}
            ],
            templates=[{
                'name': 'Cloze',
                'qfmt': '{{cloze:Text}}<br><br><div class="source"><em>Source: {{Source}}</em></div>',
                'afmt': '''{{cloze:Text}}<br>
                        <hr id="answer">
                        {{Back Extra}}<br><br>
                        <div class="source"><em>Source: {{Source}}</em></div>'''
            }],
            css='''
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    text-align: left;
                    color: black;
                    background-color: white;
                    padding: 20px;
                }
                .cloze {
                    font-weight: bold;
                    color: blue;
                }
                .source {
                    font-size: 12px;
                    color: #666;
                }
            '''
        )

    def create_deck(self, qa_pairs: List[Tuple[str, str]], deck_name: str, source: str = "Unknown") -> Optional[str]:
        """
        Create an Anki deck from Q&A pairs.
        
        Args:
            qa_pairs: List of (question, answer) tuples
            deck_name: Name for the Anki deck
            source: Source identifier (e.g., PDF filename)
            
        Returns:
            str: Path to the generated .apkg file, or None if creation fails
        """
        try:
            if not qa_pairs:
                logger.warning("No Q&A pairs provided")
                return None
                
            # Create a unique deck ID
            deck_id = random.randrange(1 << 30, 1 << 31)
            deck = genanki.Deck(deck_id=deck_id, name=deck_name)
            
            # Add notes to deck
            for question, answer in qa_pairs:
                note = genanki.Note(
                    model=self.basic_model,
                    fields=[question, answer, source]
                )
                deck.add_note(note)
            
            # Generate package
            output_file = f"{deck_name}.apkg"
            package = genanki.Package(deck)
            package.write_to_file(output_file)
            
            logger.info(f"Successfully created Anki deck: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating Anki deck: {e}")
            return None

    def create_cloze_deck(self, cloze_items: List[Tuple[str, str]], deck_name: str, source: str = "Unknown") -> Optional[str]:
        """
        Create an Anki deck with cloze deletions.
        
        Args:
            cloze_items: List of (text with cloze markers, back extra) tuples
            deck_name: Name for the Anki deck
            source: Source identifier
            
        Returns:
            str: Path to the generated .apkg file, or None if creation fails
        """
        try:
            if not cloze_items:
                logger.warning("No cloze items provided")
                return None
                
            deck_id = random.randrange(1 << 30, 1 << 31)
            deck = genanki.Deck(deck_id=deck_id, name=f"{deck_name} (Cloze)")
            
            for text, back_extra in cloze_items:
                # Verify cloze deletion syntax
                if '{{c' not in text or '::' not in text or '}}' not in text:
                    logger.warning(f"Skipping invalid cloze item: {text[:50]}...")
                    continue
                    
                note = genanki.Note(
                    model=self.cloze_model,
                    fields=[text, back_extra, source]
                )
                deck.add_note(note)
            
            if not deck.notes:
                logger.warning("No valid cloze cards were created")
                return None
                
            output_file = f"{deck_name}_cloze.apkg"
            package = genanki.Package(deck)
            package.write_to_file(output_file)
            
            logger.info(f"Successfully created cloze Anki deck: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating cloze Anki deck: {e}")
            return None 