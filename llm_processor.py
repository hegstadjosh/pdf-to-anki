from typing import List, Tuple, Optional, Dict
import logging
from utils.llm_utils import get_llm_completion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, model: str = "gpt-4o"):
        """Initialize LLM processor with specified model."""
        self.model = model
        self._initialize_prompts()
        self.default_prompt = self.prompts["standard"]

    def _initialize_prompts(self):
        """Initialize different types of prompts for flashcard generation."""
        self.prompts = {
            "standard": """
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
            """,
            
            "concept_definition": """
            Create flashcards focusing on key concepts and their definitions from the following text.
            Each card should follow this format:
            Q: What is [concept]?
            A: [Clear, concise definition with key characteristics]
            
            Guidelines:
            1. Focus on important terms and concepts
            2. Keep definitions clear and precise
            3. Include examples where relevant
            4. Break complex definitions into multiple cards
            
            Text:
            {text}
            """,
            
            "compare_contrast": """
            Create flashcards that focus on comparing and contrasting related concepts from the text.
            Format each card as:
            Q: Compare and contrast [concept A] and [concept B].
            A: [Similarities and differences, organized clearly]
            
            Guidelines:
            1. Identify related concepts that can be meaningfully compared
            2. Structure answers with clear "Similarities:" and "Differences:" sections
            3. Focus on key distinguishing features
            4. Use bullet points for clarity
            
            Text:
            {text}
            """,
            
            "example_application": """
            Create flashcards focusing on real-world examples and applications of concepts.
            Format as:
            Q: Give an example of [concept] in action. OR How is [concept] applied in practice?
            A: [Detailed example with explanation of how it demonstrates the concept]
            
            Guidelines:
            1. Focus on practical applications
            2. Include both the example and why it's relevant
            3. Use real-world scenarios
            4. Connect theory to practice
            
            Text:
            {text}
            """,
            
            "process_steps": """
            Create flashcards that break down processes and procedures into steps.
            Format as:
            Q: What are the steps in [process]? OR How do you [accomplish task]?
            A: [Numbered steps with clear sequence]
            
            Guidelines:
            1. Break complex processes into clear steps
            2. Number steps sequentially
            3. Include important cautions or notes
            4. Explain the purpose of key steps
            
            Text:
            {text}
            """,
            
            "cause_effect": """
            Create flashcards focusing on cause-and-effect relationships.
            Format as:
            Q: What are the effects of [cause]? OR What leads to [effect]?
            A: [Clear explanation of causal relationship]
            
            Guidelines:
            1. Identify clear cause-effect relationships
            2. Explain the mechanism of causation
            3. Include multiple effects where relevant
            4. Note any important conditions or exceptions
            
            Text:
            {text}
            """
        }

    def get_available_prompt_types(self) -> Dict[str, str]:
        """
        Get available prompt types with their descriptions.
        
        Returns:
            Dictionary mapping prompt type names to brief descriptions
        """
        descriptions = {
            "standard": "Basic Q&A format covering general understanding",
            "concept_definition": "Focus on defining key terms and concepts",
            "compare_contrast": "Compare and contrast related concepts",
            "example_application": "Real-world examples and applications",
            "process_steps": "Break down processes into steps",
            "cause_effect": "Cause and effect relationships"
        }
        return descriptions

    def get_prompt_template(self, prompt_type: str) -> str:
        """
        Get the template for a specific prompt type.
        
        Args:
            prompt_type: The type of prompt to retrieve
            
        Returns:
            The prompt template string
        """
        return self.prompts.get(prompt_type, self.prompts["standard"])

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
        
        Guidelines:
        1. Use EXACTLY this format with DOUBLE curly braces: {{c1::text}} for the first cloze in each sentence
        2. Use {{c2::text}} for the second cloze, {{c3::text}} for the third, etc.
        3. Create meaningful deletions that test understanding
        4. Include helpful extra information after each card
        5. Format each card exactly as:
        
        Text: [Sentence with cloze deletions]
        Extra: [Additional helpful information]
        
        Example:
        Text: {{c1::Python}} was created by {{c2::Guido van Rossum}} in {{c3::1991}}.
        Extra: Python is now one of the most popular programming languages.
        
        IMPORTANT: 
        - Use DOUBLE curly braces {{ }} not single ones { }
        - Each card MUST have both Text: and Extra: lines
        - Create at least 3-5 cloze cards from the text
        - Make sure each cloze deletion tests important concepts
        
        Text:
        {text}
        """
        
        try:
            # Validate input text
            if not text or not text.strip():
                logger.error("Empty input text provided")
                return []
                
            prompt = custom_prompt if custom_prompt else default_cloze_prompt
            formatted_prompt = prompt.format(text=text)
            
            logger.info("Requesting cloze cards from LLM...")
            success, response = get_llm_completion(formatted_prompt, self.model)
            
            if not success:
                logger.error(f"Error getting LLM completion for cloze cards: {response}")
                return []
                
            if not response or not response.strip():
                logger.error("Received empty response from LLM")
                return []
                
            logger.info("Processing LLM response...")
            
            # Parse response into cloze cards
            cloze_items = []
            current_text = None
            current_extra = []
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Text:'):
                    # Save previous cloze item if exists
                    if current_text and current_extra:
                        cloze_items.append((
                            current_text,
                            '\n'.join(current_extra).strip()
                        ))
                    # Start new cloze item
                    current_text = line[5:].strip()
                    current_extra = []
                elif line.startswith('Extra:'):
                    current_extra = [line[6:].strip()]
                elif current_extra is not None:
                    current_extra.append(line)
            
            # Add last cloze item
            if current_text and current_extra:
                cloze_items.append((
                    current_text,
                    '\n'.join(current_extra).strip()
                ))
            
            if not cloze_items:
                logger.error("No valid cloze items found in LLM response")
                logger.debug(f"Raw response: {response}")
                return []
                
            logger.info(f"Found {len(cloze_items)} potential cloze items")
            
            # Fix and validate cloze syntax
            validated_items = []
            for text, extra in cloze_items:
                # Try to fix single curly brace syntax
                fixed_text = text
                if '{c' in text and '::' in text and '}' in text and '{{' not in text:
                    # Replace single braces with double braces
                    fixed_text = text.replace('{c', '{{c').replace('}', '}}')
                    logger.info(f"Fixed single braces in: {text[:50]}...")
                
                if '{{c' in fixed_text and '::' in fixed_text and '}}' in fixed_text:
                    validated_items.append((fixed_text, extra))
                    logger.info(f"Valid cloze card: {fixed_text[:50]}...")
                else:
                    logger.warning(f"Invalid cloze syntax in: {text[:50]}...")
            
            logger.info(f"Successfully created {len(validated_items)} cloze cards")
            return validated_items
            
        except Exception as e:
            logger.error(f"Error processing text for cloze cards: {str(e)}")
            logger.exception("Full traceback:")
            return [] 