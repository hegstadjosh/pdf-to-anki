from typing import List, Tuple, Optional
import logging
from utils.llm_utils import get_llm_completion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, model: str = "gpt-4o"):
        """Initialize LLM processor with specified model."""
        self.model = model
        self.default_prompt = """
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
        """

    def process_text(self, text: str, custom_prompt: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        Process text using LLM to generate Q&A pairs.
        
        Args:
            text: Text to process
            custom_prompt: Optional custom prompt template
            
        Returns:
            List of (question, answer) tuples
        """
        try:
            # Use custom prompt if provided, otherwise use default
            prompt = custom_prompt if custom_prompt else self.default_prompt
            
            # Format prompt with text
            formatted_prompt = prompt.format(text=text)
            
            # Get completion from LLM
            success, response = get_llm_completion(formatted_prompt, self.model)
            
            if not success:
                logger.error(f"Error getting LLM completion: {response}")
                return []
            
            # Parse response into Q&A pairs
            qa_pairs = []
            current_question = None
            current_answer = []
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Q:'):
                    # Save previous Q&A pair if exists
                    if current_question and current_answer:
                        qa_pairs.append((
                            current_question, 
                            '\n'.join(current_answer).strip()
                        ))
                    # Start new question
                    current_question = line[2:].strip()
                    current_answer = []
                elif line.startswith('A:'):
                    current_answer = [line[2:].strip()]
                elif current_answer is not None:
                    current_answer.append(line)
            
            # Add last Q&A pair
            if current_question and current_answer:
                qa_pairs.append((
                    current_question, 
                    '\n'.join(current_answer).strip()
                ))
            
            return qa_pairs
            
        except Exception as e:
            logger.error(f"Error processing text with LLM: {e}")
            return []

    def create_cloze_deletions(self, text: str, custom_prompt: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        Process text using LLM to generate cloze deletions.
        
        Args:
            text: Text to process
            custom_prompt: Optional custom prompt template
            
        Returns:
            List of (cloze_text, back_extra) tuples
        """
        default_cloze_prompt = """
        Create Anki cloze deletion cards from the following text.
        Use {{c1::text}} format for cloze deletions.
        Include relevant extra information after "Extra:" for each card.
        Format each card as:
        
        Text: [text with cloze deletions]
        Extra: [additional information]
        
        Text:
        {text}
        """
        
        try:
            prompt = custom_prompt if custom_prompt else default_cloze_prompt
            formatted_prompt = prompt.format(text=text)
            
            success, response = get_llm_completion(formatted_prompt, self.model)
            
            if not success:
                logger.error(f"Error getting LLM completion for cloze cards: {response}")
                return []
            
            # Parse response into cloze cards
            cloze_items = []
            current_text = None
            current_extra = []
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Text:'):
                    # Save previous card if exists
                    if current_text and current_extra:
                        cloze_items.append((
                            current_text, 
                            '\n'.join(current_extra).strip()
                        ))
                    # Start new card
                    current_text = line[5:].strip()
                    current_extra = []
                elif line.startswith('Extra:'):
                    current_extra = [line[6:].strip()]
                elif current_extra is not None:
                    current_extra.append(line)
            
            # Add last card
            if current_text and current_extra:
                cloze_items.append((
                    current_text, 
                    '\n'.join(current_extra).strip()
                ))
            
            return cloze_items
            
        except Exception as e:
            logger.error(f"Error creating cloze deletions: {e}")
            return [] 