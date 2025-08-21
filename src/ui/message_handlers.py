"""
Message processing handlers for SAVIN AI application.
Handles different types of user interactions and message processing.
"""

import streamlit as st
import logging
from typing import Any

from ..core.exceptions import SAVINAIException


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
        """Process regular user message"""
        try:
            # Add user message
            self._add_message("user", user_input)
            
            if has_document and st.session_state.conversation:
                # Generate AI response using document
                with st.spinner("🧠 Analyzing your document..."):
                    answer, source_docs = self.app._get_ai_handler().generate_response(st.session_state.conversation, user_input)
                    
                    # Store context
                    if source_docs:
                        st.session_state.relevant_context = "\n\n".join([doc.page_content for doc in source_docs[:2]])
                    
                    self._add_message("assistant", answer, st.session_state.relevant_context)
            else:
                # No document - provide guidance
                guidance_msg = f"""🤗 **Hi there!** I'd love to help you with: "{user_input}"

Since you haven't uploaded a document yet, here's how I can assist:

• **📤 Upload a document** → I'll analyze it and give you detailed, context-aware answers
• **📖 Use Wikipedia search** → Click the 📖 button to search Wikipedia 
• **🌐 Use web search** → Click the 🌐 button to search the internet with DuckDuckGo

Just click one of the search buttons next to the text field and I'll help you find the information you need! 😊✨"""
                
                self._add_message("assistant", guidance_msg)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            error_msg = self.app.message_formatter.format_error_message("Message Processing", str(e))
            self._add_message("assistant", error_msg)
            st.rerun()
    
    def process_wikipedia_search(self, query: str):
        """Process Wikipedia search"""
        try:
            # Add search query message
            search_msg = self.app.message_formatter.format_search_query(query, "wikipedia")
            self._add_message("user", search_msg)
            
            with st.spinner("📖 Searching Wikipedia..."):
                results = self.app._get_web_search().search_wikipedia(query, max_results=3)
                
                if results:
                    # Format results for display
                    response = f"""📖 **Wikipedia Search Results for: "{query}"**

🎯 **Quick Summary:**
• Found {len(results)} relevant Wikipedia articles 📚
• Great information to explore! ✨

📋 **Key Articles:**"""
                    
                    for i, result in enumerate(results, 1):
                        response += f"\n• **{result['title']}** 🌟\n  📝 {result['summary'][:150]}...\n  🔗 [Read more]({result['url']})"
                    
                    response += "\n\n💡 **Pro Tip:**\n• Upload a document and I can combine this Wikipedia info with your content! 📄✨"
                    
                    # Create context for future use
                    context = "\n\n".join([f"{r['title']}: {r['summary']}" for r in results])
                    self._add_message("assistant", response, context)
                else:
                    no_results_msg = """😅 **No Wikipedia Results Found!**

🎯 **What happened:**
• No Wikipedia articles found for this query 📚
• Wikipedia might not have content on this specific topic 🔍

💡 **Let's try these alternatives:**
• **Rephrase your search** with different keywords 🔄
• **Use more specific terms** or try broader concepts 🎯  
• **Click the 🌐 button** to search the web instead! 🌍

✨ **I'm here to help!** Let's find the information you need together! 😊🚀"""
                    
                    self._add_message("assistant", no_results_msg)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            error_msg = self.app.message_formatter.format_error_message("Wikipedia Search", str(e))
            self._add_message("assistant", error_msg)
            st.rerun()
    
    def process_web_search(self, query: str):
        """Process web search"""
        try:
            # Add search query message
            search_msg = self.app.message_formatter.format_search_query(query, "web")
            self._add_message("user", search_msg)
            
            with st.spinner("🌐 Searching the web..."):
                results = self.app._get_web_search().search_duckduckgo(query, max_results=3)
                
                if results:
                    # Format results for display
                    response = f"""🌐 **Web Search Results for: "{query}"**

🎯 **Quick Summary:**
• Found {len(results)} relevant web pages 🌍
• Current, real-time information! ✨

📋 **Top Results:**"""
                    
                    for i, result in enumerate(results, 1):
                        response += f"\n• **{result['title']}** 🌟\n  📝 {result['summary'][:150]}...\n  🔗 [Visit site]({result['url']})"
                    
                    response += "\n\n💡 **Pro Tip:**\n• Upload a document and I can combine this web info with your content! 📄✨"
                    
                    # Create context for future use
                    context = "\n\n".join([f"{r['title']}: {r['summary']}" for r in results])
                    self._add_message("assistant", response, context)
                else:
                    no_results_msg = """😅 **No Web Results Found!**

🎯 **What happened:**
• No web pages found for this query 🌍
• The search might be too specific or unusual 🔍

💡 **Let's try these alternatives:**
• **Rephrase your search** with different keywords 🔄
• **Use more general terms** or try specific phrases 🎯  
• **Click the 📖 button** to search Wikipedia instead! 📚

✨ **I'm here to help!** Let's find the information you need together! 😊🚀"""
                    
                    self._add_message("assistant", no_results_msg)
            
            st.rerun()
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            error_msg = self.app.message_formatter.format_error_message("Web Search", str(e))
            self._add_message("assistant", error_msg)
            st.rerun()
    
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

• Your document has been successfully cleared 🗑️
• You can now upload a new document 📤
• Web search is still available anytime! 🌐

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