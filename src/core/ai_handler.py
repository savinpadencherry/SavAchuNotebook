"""
AI and language model handling for SAVIN AI application.
Manages LLM interactions, conversation chains, and response generation.
"""
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.schema import Document

from src.config.settings import AIConfig
from .exceptions import AIProcessingError
from langchain.schema import Document

from ..config.settings import AIConfig
from .exceptions import AIProcessingError
from ..utils.performance import get_cached_llm_model


# Configure logging
logger = logging.getLogger(__name__)


class AIHandler:
    """
    Handles AI model interactions and response generation.
    Manages conversation chains and provides consistent AI responses.
    """
    
    def __init__(self):
        self.config = AIConfig()
        self.llm = self._get_cached_llm()
        self.conversation_template = self._create_conversation_template()
    
    def _get_cached_llm(self) -> Ollama:
        """Get cached LLM instance for better performance"""
        try:
            # Use cached LLM model
            cached_llm = get_cached_llm_model()
            logger.info(f"Using cached LLM with model: {self.config.AI_MODEL}")
            return cached_llm
        except Exception as e:
            logger.warning(f"Failed to get cached LLM, creating new instance: {e}")
            return self._initialize_llm()
    
    def _initialize_llm(self) -> Ollama:
        """Initialize and configure the LLM (fallback)"""
        try:
            llm = Ollama(
                model=self.config.AI_MODEL,
                temperature=self.config.AI_TEMPERATURE,
                num_ctx=8192,  # Increased context window
                num_predict=1024,  # Allow longer responses
                top_k=10,
                top_p=0.8,
                repeat_penalty=1.2,
                num_thread=self.config.NUM_THREADS
            )
            
            logger.info(f"Initialized LLM with model: {self.config.AI_MODEL}")
            return llm
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise AIProcessingError(f"LLM initialization failed: {str(e)}")
    
    def _create_conversation_template(self) -> PromptTemplate:
        """Create the conversation prompt template"""
        template = """You are SAVIN AI, a warm and friendly intelligent assistant! 😊 I ALWAYS provide helpful responses in bullet points with emojis to make information easy to understand and engaging.

CONTEXT INFORMATION:
{context}

USER QUESTION: {question}

MY RESPONSE REQUIREMENTS (MANDATORY):
- ALWAYS respond ONLY with bullet points for maximum clarity 📝
- Use relevant emojis in EVERY response to be engaging and warm 😊
- Be warm, friendly, and conversational like talking to a dear friend 💭
- Structure responses with clear sections when needed 📋
- Keep language simple, clean, and user-friendly 🚀
- Make every interaction feel welcoming and supportive 🤗

MANDATORY RESPONSE FORMAT (Use EXACTLY this structure with bullet points and emojis):

🎯 **Quick Answer:**
• [Direct, friendly answer with relevant emoji]
• [Additional key point with emoji if needed]

📋 **Key Details:**
• [Important detail with emoji] 
• [Another important point with emoji]
• [Additional helpful information with emoji]

💡 **Helpful Insights:**
• [Useful insight or context with emoji]
• [Additional valuable information with emoji]

✨ **Summary:**
• [Main takeaway with emoji]
• [Encouraging closing thought with emoji]

IMPORTANT: Never deviate from bullet point format. Always be warm, supportive, and use emojis throughout. Keep language simple and friendly."""

        return PromptTemplate(
            template=template, 
            input_variables=['context', 'question']
        )
    
    def create_conversation_chain(self, vector_store) -> RetrievalQA:
        """
        Create a conversation chain with the provided vector store.
        
        Args:
            vector_store: Vector store for document retrieval
            
        Returns:
            Configured RetrievalQA chain
        """
        try:
            # Create optimized retriever
            retriever = vector_store.as_retriever(
                search_type=self.config.SEARCH_TYPE,
                search_kwargs={
                    "k": self.config.SEARCH_K,
                    "fetch_k": self.config.SEARCH_FETCH_K,
                    "lambda_mult": self.config.SEARCH_LAMBDA
                }
            )
            
            # Create conversation chain
            conversation_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": self.conversation_template},
                return_source_documents=True
            )
            
            logger.info("Created conversation chain successfully")
            return conversation_chain
            
        except Exception as e:
            logger.error(f"Failed to create conversation chain: {e}")
            raise AIProcessingError(f"Conversation chain creation failed: {str(e)}")
    
    def generate_response(self, conversation_chain: RetrievalQA, question: str) -> Tuple[str, List[Document]]:
        """
        Generate AI response for a given question using the conversation chain.
        
        Args:
            conversation_chain: The conversation chain to use
            question: User's question
            
        Returns:
            Tuple of (answer, source_documents)
        """
        try:
            logger.info(f"Generating response for question: {question[:100]}...")
            
            # Generate response
            response = conversation_chain({"question": question})
            
            answer = response.get('result', '')
            source_docs = response.get('source_documents', [])
            
            logger.info(f"Generated response with {len(source_docs)} source documents")
            return answer, source_docs
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise AIProcessingError(f"Failed to generate AI response: {str(e)}")
    
    def generate_chat_title(self, first_message: str) -> str:
        """
        Generate a smart chat title based on the first message.
        
        Args:
            first_message: First message in the chat
            
        Returns:
            Generated chat title
        """
        try:
            # Extract key words and create a meaningful title
            words = first_message.lower().split()
            
            # Remove common words
            stop_words = {
                'what', 'is', 'the', 'how', 'can', 'you', 'tell', 'me', 'about', 
                'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                'of', 'with', 'by', 'please', 'help', 'explain'
            }
            
            important_words = [
                word for word in words 
                if word not in stop_words and len(word) > 2 and word.isalpha()
            ]
            
            if len(important_words) >= 2:
                title = ' '.join(important_words[:3]).title()
            elif len(important_words) == 1:
                title = important_words[0].title() + " Discussion"
            else:
                from datetime import datetime
                title = f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
            
            # Limit title length
            return title[:50]
            
        except Exception as e:
            logger.warning(f"Failed to generate chat title: {e}")
            from datetime import datetime
            return f"Chat {datetime.now().strftime('%m/%d %H:%M')}"
    
    def test_model_availability(self) -> bool:
        """
        Test if the AI model is available and responding.
        
        Returns:
            True if model is available, False otherwise
        """
        try:
            test_response = self.llm("Hello")
            return bool(test_response and test_response.strip())
            
        except Exception as e:
            logger.error(f"Model availability test failed: {e}")
            return False


class ThinkingProcessor:
    """
    Handles AI thinking process visualization and step-by-step processing.
    """
    
    @staticmethod
    def show_thinking_process(container, steps: List[str], total_steps: int = 5):
        """
        Show AI thinking process with animated steps.
        
        Args:
            container: Streamlit container for display
            steps: List of thinking steps
            total_steps: Total number of steps to show
            
        Returns:
            Tuple of (progress_bar, status_container)
        """
        thinking_steps = [
            "🧠 Understanding your question...",
            "📚 Searching through document...",
            "🔍 Finding relevant information...",
            "💭 Analyzing context...",
            "✨ Crafting response..."
        ]
        
        # Use provided steps or default ones
        display_steps = steps if steps else thinking_steps[:total_steps]
        
        progress_bar = container.progress(0)
        status_container = container.empty()
        
        for i, step in enumerate(display_steps):
            status_container.markdown(
                f"""<div style='
                    text-align: center; 
                    padding: 10px; 
                    background: rgba(255,255,255,0.1); 
                    border-radius: 10px; 
                    margin: 5px 0;
                '>{step}</div>""", 
                unsafe_allow_html=True
            )
            progress_bar.progress((i + 1) / len(display_steps))
            time.sleep(0.8)  # Simulate thinking time
        
        return progress_bar, status_container
    
    @staticmethod
    def simulate_typing_effect(text: str, container):
        """
        Simulate typing effect by gradually revealing text.
        
        Args:
            text: Text to display with typing effect
            container: Streamlit container for display
        """
        words = text.split()
        displayed_text = ""
        
        for i, word in enumerate(words):
            displayed_text += word + " "
            container.markdown(displayed_text + "▌")
            if i % 5 == 0:  # Update every 5 words for performance
                time.sleep(0.1)
        
        # Final display without cursor
        container.markdown(text)


class ResponseFormatter:
    """
    Handles formatting and structuring of AI responses.
    """
    
    @staticmethod
    def format_error_response(error_type: str, error_message: str) -> str:
        """
        Format error messages in a user-friendly way.
        
        Args:
            error_type: Type of error
            error_message: Error message details
            
        Returns:
            Formatted error response
        """
        return f"""😅 **Oops! Something went wrong**

🎯 **What happened:**
• {error_type} error occurred
• Technical details: {error_message}

💡 **What you can try:**
• Check your internet connection 🌐
• Try rephrasing your question 🔄
• Upload a different document if needed 📄
• Restart the application if problems persist 🔄

🤗 **Don't worry!** I'm still here to help you. Let's try again! 💪"""

    @staticmethod
    def format_guidance_response(user_input: str, has_document: bool = False) -> str:
        """
        Format guidance response when no document is available.
        
        Args:
            user_input: User's input
            has_document: Whether a document is available
            
        Returns:
            Formatted guidance response
        """
        if has_document:
            return f"""🤗 **Thanks for your question: "{user_input}"**

📄 **Great news!** I have your document loaded and ready.

💭 **I can help you with:**
• Detailed analysis of your document content 📊
• Specific questions about the information 🔍
• Summaries and key insights 💡
• Creative ideas based on the content ✨

🚀 **Just ask me anything about your document!**"""
        else:
            return f"""🤗 **Hi there!** I'd love to help you with: "{user_input}"

Since you haven't uploaded a document yet, here's how I can assist:

• **📤 Upload a document** → I'll analyze it and give you detailed, context-aware answers
• **📖 Use Wikipedia search** → Click the 📖 button to search Wikipedia 
• **🌐 Use web search** → Click the 🌐 button to search the internet

Just upload a document or use the search buttons next to the text field! 😊✨"""


# Factory functions
def create_ai_handler() -> AIHandler:
    """Create a new AI handler instance"""
    return AIHandler()


def create_thinking_processor() -> ThinkingProcessor:
    """Create a new thinking processor instance"""
    return ThinkingProcessor()


def create_response_formatter() -> ResponseFormatter:
    """Create a new response formatter instance"""
    return ResponseFormatter()


# Backward compatibility functions
def get_conversation_chain(vector_store):
    """Create conversation chain (backward compatibility)"""
    handler = create_ai_handler()
    return handler.create_conversation_chain(vector_store)


def show_thinking_process(container, steps, total_steps=5):
    """Show thinking process (backward compatibility)"""
    processor = create_thinking_processor()
    return processor.show_thinking_process(container, steps, total_steps)


def generate_chat_title(first_message: str) -> str:
    """Generate chat title (backward compatibility)"""
    handler = create_ai_handler()
    return handler.generate_chat_title(first_message)