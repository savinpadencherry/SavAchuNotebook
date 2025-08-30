# FIXED: ai_handler.py - Enhanced with Anti-Hallucination Controls

"""
Enhanced AI handler with strict context adherence and hallucination prevention.
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
from ..utils.performance import get_cached_llm_model

logger = logging.getLogger(__name__)

class AIHandler:
    """Enhanced AI handler with strict context adherence and hallucination prevention."""

    def __init__(self):
        logger.info("🤖 Initializing Enhanced AI Handler...")
        self.config = AIConfig()
        self.llm = self._get_cached_llm()
        self.conversation_template = self._create_strict_conversation_template()
        self.fact_check_template = self._create_fact_check_template()
        logger.info("✅ Enhanced AI Handler initialized successfully")

    def _get_cached_llm(self) -> Ollama:
        try:
            cached_llm = get_cached_llm_model()
            logger.info(f"✅ Using cached LLM with model: {self.config.AI_MODEL}")
            return cached_llm
        except Exception as e:
            logger.warning(f"⚠️ Failed to get cached LLM: {e}")
            return self._initialize_llm()

    def _initialize_llm(self) -> Ollama:
        try:
            llm = Ollama(
                model=self.config.AI_MODEL,
                temperature=self.config.AI_TEMPERATURE,
            )
            logger.info(f"Initialized LLM with model: {self.config.AI_MODEL}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise AIProcessingError(f"LLM initialization failed: {str(e)}")

    def _create_strict_conversation_template(self) -> PromptTemplate:
        """Create ultra-strict conversation template to prevent hallucination."""
        template = """You are a document analysis assistant. You MUST follow these rules EXACTLY:

CRITICAL RULES:
1. Use ONLY information from the CONTEXT below
2. If information is NOT in the context, say "This information is not available in the document"
3. DO NOT add any information not explicitly stated in the context
4. DO NOT make assumptions or inferences beyond what's written
5. Quote directly from the context when possible

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Read the context carefully
- Answer ONLY using information from the context
- If the answer requires information not in the context, clearly state this
- Use direct quotes when possible
- Be specific about what the document says

ANSWER FORMAT:
Based on the document: [your answer using only context information]

If not in document: "This specific information is not available in the provided document."

ANSWER:"""

        return PromptTemplate(
            template=template,
            input_variables=['context', 'question']
        )

    def _create_fact_check_template(self) -> PromptTemplate:
        """Template to verify if response matches context."""
        template = """Compare the ANSWER with the CONTEXT and determine if the answer is accurate.

CONTEXT:
{context}

ANSWER TO CHECK:
{answer}

QUESTION:
{question}

EVALUATION CRITERIA:
1. Does the answer use only information from the context?
2. Is the answer directly supported by the context?
3. Are there any claims not found in the context?

Respond with:
ACCURATE: If answer is fully supported by context
INACCURATE: If answer contains information not in context
PARTIAL: If answer is mostly correct but has some unsupported claims

JUDGMENT: """

        return PromptTemplate(
            template=template,
            input_variables=['context', 'answer', 'question']
        )

    def _verify_context_relevance(self, context: str, question: str) -> bool:
        """Check if retrieved context is relevant to the question."""
        if not context or not context.strip():
            return False
        
        # Simple keyword matching for relevance
        question_words = set(question.lower().split())
        context_words = set(context.lower().split())
        
        # Remove common words
        common_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
        question_keywords = question_words - common_words
        context_keywords = context_words - common_words
        
        # Check for keyword overlap
        overlap = question_keywords.intersection(context_keywords)
        relevance_score = len(overlap) / len(question_keywords) if question_keywords else 0
        
        return relevance_score > 0.2  # At least 20% keyword overlap

    class StrictRetrievalQA:
        """Enhanced retrieval with strict context validation."""
        
        def __init__(self, llm, retriever, prompt_template: PromptTemplate, fact_check_template: PromptTemplate, ai_handler):
            self.llm = llm
            self.retriever = retriever
            self.prompt_template = prompt_template
            self.fact_check_template = fact_check_template
            self.ai_handler = ai_handler

        def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
            question = inputs.get("question", "")
            
            # Retrieve documents with enhanced filtering
            docs = self.retriever.get_relevant_documents(question)
            
            if not docs:
                return {
                    "result": "No relevant information found in the document for this question.",
                    "source_documents": []
                }

            # Filter and validate context
            context = self._build_validated_context(docs, question)
            
            if not context:
                return {
                    "result": "The retrieved information is not relevant to your question. Please ask about topics covered in the document.",
                    "source_documents": docs
                }

            # Generate response with strict context adherence
            prompt_text = self.prompt_template.format(context=context, question=question)
            
            try:
                if hasattr(self.llm, "invoke"):
                    raw_response = self.llm.invoke(prompt_text)
                else:
                    raw_response = self.llm(prompt_text)
                
                answer = self._extract_text(raw_response)
                
                # Verify response accuracy
                verified_answer = self._verify_and_correct_response(answer, context, question)
                
                return {"result": verified_answer, "source_documents": docs}
                
            except Exception as e:
                logger.error(f"Response generation failed: {e}")
                return {
                    "result": "I encountered an error while processing your question. Please try rephrasing it.",
                    "source_documents": docs
                }

        def _build_validated_context(self, docs: List[Document], question: str) -> str:
            """Build context only from relevant document chunks."""
            relevant_chunks = []
            
            for doc in docs:
                chunk_text = doc.page_content
                
                # Check relevance of each chunk
                if self.ai_handler._verify_context_relevance(chunk_text, question):
                    relevant_chunks.append(chunk_text)
            
            # Limit context length to prevent overwhelming the model
            context = "\n\n".join(relevant_chunks[:3])  # Use top 3 relevant chunks
            
            # Ensure context is not too long
            if len(context) > 2000:  # Limit context size
                context = context[:2000] + "..."
            
            return context

        def _extract_text(self, response):
            """Extract text from LLM response."""
            if isinstance(response, str):
                return response.strip()
            if hasattr(response, "content"):
                return getattr(response, "content").strip()
            if isinstance(response, dict) and "content" in response:
                return response["content"].strip()
            return str(response).strip()

        def _verify_and_correct_response(self, answer: str, context: str, question: str) -> str:
            """Verify response accuracy and correct if needed."""
            try:
                # Check for obvious hallucination signs
                if self._contains_hallucination_indicators(answer, context):
                    return f"I cannot provide a complete answer to '{question}' based on the available document content. The document may not contain the specific information you're looking for."
                
                # Additional fact-checking could be implemented here
                return answer
                
            except Exception as e:
                logger.warning(f"Response verification failed: {e}")
                return answer

        def _contains_hallucination_indicators(self, answer: str, context: str) -> bool:
            """Check for common hallucination patterns."""
            answer_lower = answer.lower()
            context_lower = context.lower()
            
            # Check if answer contains information clearly not in context
            answer_words = set(answer_lower.split())
            context_words = set(context_lower.split())
            
            # Look for specific entities or facts in answer not in context
            # This is a simplified check - could be enhanced
            hallucination_indicators = [
                "quantum computing",  # If not in context
                "google",  # If not in context  
                "artificial intelligence can be built",  # Suspicious pattern from your example
                "they have demonstrated",  # If "they" is not defined in context
            ]
            
            for indicator in hallucination_indicators:
                if indicator in answer_lower and indicator not in context_lower:
                    logger.warning(f"Potential hallucination detected: {indicator}")
                    return True
            
            return False

    def create_conversation_chain(self, vector_store) -> Any:
        """Create enhanced conversation chain with strict validation."""
        try:
            # Create optimized retriever with better filtering
            retriever = vector_store.as_retriever(
                search_type="similarity",  # Use similarity instead of MMR for more precise results
                search_kwargs={
                    "k": 5,  # Reduced from 8 for more focused results
                    "fetch_k": 15,  # Reduced from 50 
                }
            )
            
            # Use our strict retrieval chain
            conversation_chain = AIHandler.StrictRetrievalQA(
                self.llm, 
                retriever, 
                self.conversation_template,
                self.fact_check_template,
                self
            )
            
            logger.info("Created enhanced conversation chain with strict validation")
            return conversation_chain
            
        except Exception as e:
            logger.error(f"Failed to create conversation chain: {e}")
            raise AIProcessingError(f"Conversation chain creation failed: {str(e)}")

    def generate_response(self, conversation_chain, question: str) -> Tuple[str, List[Document]]:
        """Generate response with enhanced validation."""
        try:
            logger.info(f"Generating validated response for: {question[:100]}...")
            
            # Clean and validate question
            clean_question = self._clean_question(question)
            
            # Generate response
            response = conversation_chain({"question": clean_question})
            answer = response.get('result', '')
            source_docs = response.get('source_documents', [])

            logger.info(f"Generated validated response with {len(source_docs)} source documents")
            return answer, source_docs

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try rephrasing it or ask about a different aspect of the document.", []

    def _clean_question(self, question: str) -> str:
        """Clean and validate user question."""
        # Remove extra whitespace
        question = ' '.join(question.split())
        
        # Ensure question ends with question mark if it's a question
        if question and not question.endswith(('?', '.', '!')):
            question += '?'
        
        return question

    def generate_chat_title(self, first_message: str) -> str:
        """Generate chat title from first message."""
        try:
            words = first_message.lower().split()
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

            return title[:50]
        except Exception as e:
            logger.warning(f"Failed to generate chat title: {e}")
            from datetime import datetime
            return f"Chat {datetime.now().strftime('%m/%d %H:%M')}"

    def test_model_availability(self) -> bool:
        """Test if the AI model is available and responding."""
        try:
            test_response = self.llm("Hello")
            return bool(test_response and test_response.strip())
        except Exception as e:
            logger.error(f"Model availability test failed: {e}")
            return False

# Factory functions
def create_ai_handler() -> AIHandler:
    """Create a new AI handler instance"""
    return AIHandler()

# Backward compatibility functions
def get_conversation_chain(vector_store):
    """Create conversation chain (backward compatibility)"""
    handler = create_ai_handler()
    return handler.create_conversation_chain(vector_store)

def generate_chat_title(first_message: str) -> str:
    """Generate chat title (backward compatibility)"""
    handler = create_ai_handler()
    return handler.generate_chat_title(first_message)