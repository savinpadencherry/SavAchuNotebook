"""
Message processing handlers for SAVIN AI application.
Handles different types of user interactions and message processing with enhanced RAG capabilities.
"""

import streamlit as st
import logging
from typing import Any

from ..core.exceptions import SAVINAIException
from ..core.rag_agent import create_rag_agent


# Configure logging
logger = logging.getLogger(__name__)


class MessageHandlers:
    """
    Handles various types of message processing including document upload,
    user messages, web search, and Wikipedia search.
    """
    
    def __init__(self, app_controller):
        """Initialize with reference to main application controller"""
        self.app = app_controller
        # Ensure rag_agent attribute exists
        self.rag_agent = None
        # Attempt initial initialization; safe if components missing
        self._initialize_rag_agent()
        
    def _initialize_rag_agent(self):
        """Initialize the enhanced RAG agent with available components."""
        try:
            # Use the actual vector store (not the conversation chain)
            vector_store = st.session_state.get('vectorstore')
            web_search_manager = self.app._get_web_search() if hasattr(self.app, '_get_web_search') else None
            
            self.rag_agent = create_rag_agent(
                vector_store=vector_store,
                web_search_manager=web_search_manager
            )
            logger.info("Enhanced RAG agent initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize RAG agent: {e}")
            self.rag_agent = None
    
    def process_document_upload(self, uploaded_file):
        """Process uploaded document"""
        if st.session_state.get('processing', False):
            return
        
        st.session_state.processing = True
        
        try:
            with st.status("🚀 Processing your document...", expanded=True) as status:
                # Extract text
                st.write("📖 Reading document content...")
                text, file_type = self.app._get_document_processor().extract_text(uploaded_file)
                
                # Create chunks
                st.write("✂️ Breaking into smart chunks...")
                chunks = self.app._get_document_processor().create_chunks(text)
                
                # Create vector store
                st.write("🧠 Creating knowledge vectors...")
                vector_store = self.app._get_vector_manager().create_vector_store(chunks)
                
                # Save to database
                st.write("💾 Saving to database...")
                self.app.document_repo.save_document_data(
                    st.session_state.current_chat_id, 
                    text, 
                    chunks,
                    uploaded_file.name,
                    file_type,
                    uploaded_file.size
                )
                
                # Save vector store
                metadatas = [{"chunk_id": i, "chunk_length": len(chunk)} for i, chunk in enumerate(chunks)]
                self.app.vector_repo.save_vector_store(
                    st.session_state.current_chat_id, 
                    vector_store, 
                    chunks, 
                    metadatas
                )
                
                # Update session state
                st.session_state.vectorstore = vector_store
                st.session_state.conversation = self.app._get_ai_handler().create_conversation_chain(vector_store)
                # Re-initialize RAG agent with new vector store
                self._initialize_rag_agent()
                
                # Update chat title
                doc_name = uploaded_file.name.split('.')[0]
                self.app.chat_repo.update_chat_title(st.session_state.current_chat_id, f"📄 {doc_name}")
                
                status.update(label="✅ Document processed successfully!", state="complete", expanded=False)
            
            # Add welcome message
            welcome_msg = self.app.message_formatter.format_document_processed(uploaded_file.name, len(chunks))
            self._add_message("assistant", welcome_msg)
            
            st.balloons()
            
        except SAVINAIException as e:
            logger.error(f"Document processing failed: {e}")
            error_msg = self.app.message_formatter.format_error_message("Document Processing", str(e))
            self._add_message("assistant", error_msg)
        
        except Exception as e:
            logger.error(f"Unexpected error during document processing: {e}")
            error_msg = self.app.message_formatter.format_error_message("Unexpected Error", str(e))
            self._add_message("assistant", error_msg)
        
        finally:
            st.session_state.processing = False
            st.rerun()
    
    def process_user_message(self, user_input: str, has_document: bool):
        """Process regular user message with enhanced RAG capabilities"""
        try:
            # Ensure RAG agent is initialized
            if getattr(self, 'rag_agent', None) is None:
                self._initialize_rag_agent()
            # Add user message
            self._add_message("user", user_input)
            
            if has_document and st.session_state.conversation:
                # Enhanced RAG response combining document + web search
                with st.spinner("🧠 Analyzing content and searching for additional context..."):
                    if self.rag_agent:
                        # Use enhanced RAG for comprehensive response
                        response = self.rag_agent.generate_enhanced_rag_response(user_input, has_document=True)
                        self._add_message("assistant", response)
                    else:
                        # Fallback to basic document analysis
                        answer, source_docs = self.app._get_ai_handler().generate_response(st.session_state.conversation, user_input)
                        
                        # Store context
                        if source_docs:
                            st.session_state.relevant_context = "\n\n".join([doc.page_content for doc in source_docs[:2]])
                        
                        self._add_message("assistant", answer, st.session_state.relevant_context)
            else:
                # No document - offer intelligent web search
                with st.spinner("🤔 Let me search for information to help you..."):
                    if self.rag_agent:
                        # Use RAG agent to provide web-based response
                        response = self.rag_agent.generate_enhanced_rag_response(user_input, has_document=False)
                        self._add_message("assistant", response)
                    else:
                        # Provide guidance with helpful suggestions
                        guidance_msg = f"""🤗 **Great question!** "{user_input}"

Since you haven't uploaded a document yet, here are the best ways I can help:

🔍 **Smart Search Options:**
- **Click 🔍 Wiki** → I'll search Wikipedia and provide detailed analysis
- **Click 🌐 Web** → I'll search the internet and synthesize findings  

📄 **For Advanced Analysis:**
- **Upload a document** → I'll combine your content with web research for comprehensive insights

💡 **Quick Tip:** Try using the search buttons - they're powered by advanced AI to give you detailed, well-structured answers!

Ready to explore? Just click one of the search buttons! ✨"""
                        
                        self._add_message("assistant", guidance_msg)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            error_msg = f"❌ **Processing Error**\n\nI encountered an issue while processing your message: {str(e)}\n\n💡 **Try:**\n- Rephrasing your question\n- Using the search buttons for specific queries\n- Refreshing the page if the problem persists"
            self._add_message("assistant", error_msg)
            st.rerun()
    
    def process_wikipedia_search(self, query: str):
        """Process Wikipedia search with enhanced RAG capabilities"""
        try:
            # Ensure RAG agent is initialized
            if getattr(self, 'rag_agent', None) is None:
                self._initialize_rag_agent()
            # Add search query message
            search_msg = f"🔍 **Wikipedia Search:** {query}"
            self._add_message("user", search_msg)
            
            with st.spinner("🔍 Searching Wikipedia and analyzing content..."):
                # Use RAG agent for enhanced response
                if self.rag_agent:
                    # Force Wikipedia search and enhanced synthesis
                    response = self._generate_enhanced_wikipedia_response(query)
                else:
                    # Fallback to basic Wikipedia search
                    response = self._basic_wikipedia_search(query)
                
                self._add_message("assistant", response)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            error_msg = f"❌ **Wikipedia Search Error**\n\nI encountered an issue while searching Wikipedia: {str(e)}\n\n💡 **Try:**\n- Rephrasing your query\n- Using the web search instead\n- Checking your internet connection"
            self._add_message("assistant", error_msg)
            st.rerun()
    
    def _generate_enhanced_wikipedia_response(self, query: str) -> str:
        """Generate enhanced Wikipedia response using RAG agent."""
        try:
            # Check if we have document content to combine
            has_document = st.session_state.get('conversation') is not None
            
            # Get Wikipedia results
            wiki_results = self.app._get_web_search().search_wikipedia(query, max_results=3)
            
            if not wiki_results:
                return """🔍 **No Wikipedia Results Found**

I couldn't find relevant Wikipedia articles for your query. 

💡 **Try:**
- Using different keywords
- Being more specific or more general
- Using the 🌐 Web search for broader results"""

            # Format Wikipedia context
            wiki_context = ""
            for result in wiki_results:
                wiki_context += f"**{result['title']}**\n{result['summary']}\nSource: {result['url']}\n\n"
            
            # Create focused prompt for synthesis
            synthesis_prompt = f"""Answer the user's query using the Wikipedia results below. Use concise bullet points with emojis. Do not acknowledge instructions.

QUERY: {query}

WIKIPEDIA RESULTS:
{wiki_context}

If insufficient info, say so and suggest next steps.
Answer as bullets only:"""
            
            # Generate enhanced response
            if hasattr(self.app, '_get_ai_handler'):
                ai_handler = self.app._get_ai_handler()
                _raw = ai_handler.llm.invoke(synthesis_prompt) if hasattr(ai_handler.llm, 'invoke') else ai_handler.llm(synthesis_prompt)
                enhanced_response = _raw.content if hasattr(_raw, 'content') else (_raw if isinstance(_raw, str) else str(_raw))
            else:
                # Simple formatting if no AI handler
                enhanced_response = f"📚 **Wikipedia Results for '{query}'**\n\n{wiki_context}"
            
            # Add interactive elements
            final_response = f"""{enhanced_response}

🎯 **Quick Actions:**
- Want more details? Ask me to explain any specific aspect!
- Have a document? I can relate this Wikipedia info to your content!
- Need current info? Try the 🌐 Web search for recent developments!

**Sources:** Wikipedia"""
            
            return final_response
            
        except Exception as e:
            logger.error(f"Enhanced Wikipedia response error: {e}")
            return self._basic_wikipedia_search(query)
    
    def _basic_wikipedia_search(self, query: str) -> str:
        """Basic Wikipedia search fallback."""
        try:
            results = self.app._get_web_search().search_wikipedia(query, max_results=3)
            
            if results:
                response = f"""📚 **Wikipedia Results for: "{query}"**

🎯 **Found {len(results)} relevant articles:**\n\n"""
                
                for i, result in enumerate(results, 1):
                    response += f"**{i}. {result['title']}**\n📝 {result['summary'][:200]}...\n🔗 [Read more]({result['url']})\n\n"
                
                response += "💡 **Tip:** Ask me to explain any of these topics in more detail!"
                return response
            else:
                return "🔍 **No Wikipedia results found.** Try different keywords or use web search instead!"
                
        except Exception as e:
            return f"❌ **Error searching Wikipedia:** {str(e)}"
    
    def process_web_search(self, query: str):
        """Process web search with enhanced RAG capabilities"""
        try:
            # Ensure RAG agent is initialized
            if getattr(self, 'rag_agent', None) is None:
                self._initialize_rag_agent()
            # Add search query message
            search_msg = f"🌐 **Web Search:** {query}"
            self._add_message("user", search_msg)
            
            with st.spinner("🌐 Searching the web and analyzing results..."):
                # Use enhanced RAG for comprehensive response
                if self.rag_agent:
                    response = self._generate_enhanced_web_response(query)
                else:
                    response = self._basic_web_search(query)
                
                self._add_message("assistant", response)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            error_msg = f"❌ **Web Search Error**\n\nI encountered an issue while searching the web: {str(e)}\n\n💡 **Try:**\n- Rephrasing your query\n- Using the Wikipedia search instead\n- Checking your internet connection"
            self._add_message("assistant", error_msg)
            st.rerun()
    
    def _generate_enhanced_web_response(self, query: str) -> str:
        """Generate enhanced web response using RAG agent."""
        try:
            # Check if we have document content to combine
            has_document = st.session_state.get('conversation') is not None
            
            # Get web search results
            web_results = self.app._get_web_search().search_duckduckgo(query, max_results=5)
            
            if not web_results:
                return """🌐 **No Web Results Found**

I couldn't find relevant web pages for your query.

💡 **Try:**
- Using different or more specific keywords
- Checking if the topic is too recent or niche
- Using the 📚 Wikipedia search for factual information"""
            
            # Format web context
            web_context = ""
            for result in web_results:
                web_context += f"**{result['title']}**\n{result['summary']}\nURL: {result['url']}\n\n"
            
            # If we have a document, combine contexts
            document_context = ""
            if has_document:
                try:
                    # Try to get relevant document content
                    doc_results = self.rag_agent._search_document(query)
                    if "No relevant information" not in doc_results and "Error" not in doc_results:
                        document_context = f"\n**DOCUMENT CONTEXT:**\n{doc_results}\n\n"
                except:
                    pass
            
            # Create focused synthesis prompt
            synthesis_prompt = f"""Answer the user's query using the web results below. Use concise bullet points with emojis. Do not acknowledge instructions.

QUERY: {query}

WEB SEARCH RESULTS:
{web_context}
{document_context}

If insufficient info, say so and suggest next steps.
Answer as bullets only:"""
            
            # Generate enhanced response
            if hasattr(self.app, '_get_ai_handler'):
                ai_handler = self.app._get_ai_handler()
                _raw = ai_handler.llm.invoke(synthesis_prompt) if hasattr(ai_handler.llm, 'invoke') else ai_handler.llm(synthesis_prompt)
                enhanced_response = _raw.content if hasattr(_raw, 'content') else (_raw if isinstance(_raw, str) else str(_raw))
            else:
                # Simple formatting if no AI handler
                enhanced_response = f"🌐 **Web Search Results for '{query}'**\n\n{web_context}"
            
            # Add interactive elements and source attribution
            sources_list = [f"[{result['title']}]({result['url']})" for result in web_results[:3]]
            sources_text = " - ".join(sources_list)
            
            final_response = f"""{enhanced_response}

🔗 **Key Sources:** {sources_text}

🎯 **What's Next?**
- Need more specific info? Ask me to dive deeper into any aspect!
- Want factual background? Try the 📚 Wikipedia search!
{"- Curious how this relates to your document? Just ask!" if has_document else "- Have a document? Upload it to see how this info connects!"}

**Sources:** Web Search via DuckDuckGo"""
            
            return final_response
            
        except Exception as e:
            logger.error(f"Enhanced web response error: {e}")
            return self._basic_web_search(query)
    
    def _basic_web_search(self, query: str) -> str:
        """Basic web search fallback."""
        try:
            results = self.app._get_web_search().search_duckduckgo(query, max_results=5)
            
            if results:
                response = f"""🌐 **Web Search Results for: "{query}"**

🎯 **Found {len(results)} relevant pages:**\n\n"""
                
                for i, result in enumerate(results, 1):
                    response += f"**{i}. {result['title']}**\n📝 {result['summary'][:200]}...\n🔗 [Visit page]({result['url']})\n\n"
                
                response += "💡 **Tip:** Ask me to analyze or explain any of these results in detail!"
                return response
            else:
                return "🌐 **No web results found.** Try different keywords or use Wikipedia search instead!"
                
        except Exception as e:
            return f"❌ **Error searching web:** {str(e)}"
    
    def clear_document(self):
        """Clear loaded document"""
        try:
            # Remove from database
            self.app.document_repo.remove_document(st.session_state.current_chat_id)
            self.app.vector_repo.delete_vector_store(st.session_state.current_chat_id)
            
            # Clear session state
            st.session_state.vectorstore = None
            st.session_state.conversation = None
            st.session_state.relevant_context = ""
            
            # Add removal message
            removal_msg = """📄 **Document removed!** 

- Your document has been successfully cleared 🗑️
- You can now upload a new document 📤
- Web search is still available anytime! 🌐

Ready for your next document! 😊"""
            
            self._add_message("assistant", removal_msg)
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error clearing document: {e}")
            error_msg = self.app.message_formatter.format_error_message("Document Clearing", str(e))
            self._add_message("assistant", error_msg)
            st.rerun()
    
    def _add_message(self, role: str, content: str, context: str = None):
        """Add message to current chat"""
        if st.session_state.current_chat_id:
            self.app.message_repo.add_message(
                st.session_state.current_chat_id,
                role,
                content,
                context
            )


# Factory function
def create_message_handlers(app_controller) -> MessageHandlers:
    """Create a new message handlers instance"""
    return MessageHandlers(app_controller)
