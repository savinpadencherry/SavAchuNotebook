"""
Enhanced RAG Agent for SAVIN AI with LangChain integration.
Combines document content with web search results for comprehensive responses.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.agents.react.base import ReActDocstoreAgent
    from langchain.tools import Tool, BaseTool
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.schema import Document
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback when LangChain is not available
    LANGCHAIN_AVAILABLE = False
    Tool = object
    BaseTool = object
    Document = object

from src.config.settings import AIConfig
from .exceptions import AIProcessingError
from ..utils.performance import get_cached_llm_model

logger = logging.getLogger(__name__)


class EnhancedRAGAgent:
    """
    Advanced RAG agent that combines document retrieval with web search for comprehensive responses.
    
    This agent uses LangChain's ReAct framework to intelligently:
    1. Analyze user queries
    2. Retrieve relevant document content 
    3. Search web/Wikipedia for additional context
    4. Synthesize comprehensive responses
    """
    
    def __init__(self, vector_store=None, web_search_manager=None):
        """Initialize the enhanced RAG agent with tools and LLM."""
        self.config = AIConfig()
        self.vector_store = vector_store
        self.web_search_manager = web_search_manager
        
        # Initialize LLM with caching if available
        try:
            self.llm = get_cached_llm_model()
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}")
            self.llm = None
        
        # Initialize components only if LangChain is available
        if LANGCHAIN_AVAILABLE:
            try:
                # Initialize memory for conversation context
                self.memory = ConversationBufferWindowMemory(
                    k=5,  # Remember last 5 exchanges
                    return_messages=True,
                    memory_key="chat_history"
                )
                
                # Create agent tools
                self.tools = self._create_agent_tools()
                
                # Create enhanced RAG prompt
                self.agent_prompt = self._create_agent_prompt()
                
                # Initialize agent
                self.agent = self._create_agent()
            except Exception as e:
                logger.warning(f"Failed to initialize LangChain components: {e}")
                self.agent = None
                self.tools = []
        else:
            logger.warning("LangChain not available, using fallback mode")
            self.agent = None
            self.tools = []
            self.memory = None
    
    def _create_agent_tools(self) -> List:
        """Create tools for the agent to use."""
        if not LANGCHAIN_AVAILABLE:
            return []
            
        tools = []
        
        # Document search tool
        if self.vector_store:
            try:
                document_tool = Tool(
                    name="document_search",
                    description="Search the uploaded document for relevant information. Use this for questions about the document content.",
                    func=self._search_document
                )
                tools.append(document_tool)
            except Exception as e:
                logger.warning(f"Failed to create document tool: {e}")
        
        # Wikipedia search tool
        if self.web_search_manager:
            try:
                wikipedia_tool = Tool(
                    name="wikipedia_search", 
                    description="Search Wikipedia for factual information and background context. Use this for general knowledge questions.",
                    func=self._search_wikipedia
                )
                tools.append(wikipedia_tool)
                
                # Web search tool
                web_search_tool = Tool(
                    name="web_search",
                    description="Search the web using DuckDuckGo for current information and diverse perspectives. Use this for recent events or broad topics.",
                    func=self._search_web
                )
                tools.append(web_search_tool)
            except Exception as e:
                logger.warning(f"Failed to create web search tools: {e}")
        
        return tools
    
    def _search_document(self, query: str) -> str:
        """Search the document vector store."""
        try:
            if not self.vector_store:
                return "No document is currently loaded."
            
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(query, k=3)
            
            if not docs:
                return "No relevant information found in the document."
            
            # Format results
            context = "\n\n".join([doc.page_content for doc in docs])
            return f"Document content:\n{context}"
            
        except Exception as e:
            logger.error(f"Document search error: {e}")
            return f"Error searching document: {str(e)}"
    
    def _search_wikipedia(self, query: str) -> str:
        """Search Wikipedia for information."""
        try:
            results = self.web_search_manager.search_wikipedia(query, max_results=2)
            
            if not results:
                return "No Wikipedia results found for this query."
            
            # Format results
            context = ""
            for result in results:
                context += f"Title: {result['title']}\n"
                context += f"Summary: {result['summary'][:300]}...\n"
                context += f"Source: {result['url']}\n\n"
            
            return f"Wikipedia results:\n{context}"
            
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return f"Error searching Wikipedia: {str(e)}"
    
    def _search_web(self, query: str) -> str:
        """Search the web using DuckDuckGo."""
        try:
            results = self.web_search_manager.search_duckduckgo(query, max_results=3)
            
            if not results:
                return "No web search results found for this query."
            
            # Format results
            context = ""
            for result in results:
                context += f"Title: {result['title']}\n"
                context += f"Summary: {result['summary'][:200]}...\n"
                context += f"URL: {result['url']}\n\n"
            
            return f"Web search results:\n{context}"
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Error searching web: {str(e)}"
    
    def _create_agent_prompt(self):
        """Create the enhanced prompt template for the RAG agent."""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        try:
            template = """You are SAVIN AI, an intelligent assistant that can access multiple information sources.

Available Tools:
{tools}

Tool Names: {tool_names}

INSTRUCTIONS:
1. Analyze the user's question carefully
2. Determine which tools would be most helpful
3. Use document_search for questions about uploaded documents
4. Use wikipedia_search for factual/background information  
5. Use web_search for current events or diverse perspectives
6. Combine information from multiple sources for comprehensive answers
7. Always cite your sources and be clear about where information comes from

Question: {input}

Thought: I need to determine which tools will help me answer this question comprehensively.

{agent_scratchpad}"""
            
            return PromptTemplate(
                template=template,
                input_variables=["input", "tools", "tool_names", "agent_scratchpad"]
            )
        except Exception as e:
            logger.warning(f"Failed to create agent prompt: {e}")
            return None
    
    def _create_agent(self):
        """Create the ReAct agent with tools."""
        try:
            # Create a simple agent that can use tools
            return create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.agent_prompt
            )
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            # Fallback to basic LLM chain
            return None
    
    def generate_response(self, query: str) -> Tuple[str, Optional[List[Document]]]:
        """
        Generate a comprehensive response using the RAG agent.
        
        Args:
            query: User's question
            
        Returns:
            Tuple of (response, source_documents)
        """
        try:
            if self.agent and self.tools:
                # Use agent with tools
                agent_executor = AgentExecutor(
                    agent=self.agent,
                    tools=self.tools,
                    memory=self.memory,
                    verbose=True,
                    max_iterations=3,
                    handle_parsing_errors=True
                )
                
                result = agent_executor.invoke({"input": query})
                response = result.get("output", "I couldn't generate a response.")
                
            else:
                # Fallback to basic response
                response = self._generate_basic_response(query)
            
            return response, None
            
        except Exception as e:
            logger.error(f"RAG agent error: {e}")
            return f"I encountered an error while processing your question: {str(e)}", None
    
    def _generate_basic_response(self, query: str) -> str:
        """Generate a basic response when agent is not available."""
        try:
            # Simple prompt for basic response
            prompt = PromptTemplate(
                template="""You are SAVIN AI, a helpful assistant. Answer the following question:

Question: {question}

Answer: """,
                input_variables=["question"]
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(question=query)
            
        except Exception as e:
            logger.error(f"Basic response generation error: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def generate_enhanced_rag_response(self, query: str, has_document: bool = False) -> str:
        """
        Generate enhanced RAG response by combining document and web search results.
        
        This method implements the core RAG functionality by:
        1. Searching document content if available
        2. Searching Wikipedia for factual context  
        3. Searching web for current information
        4. Synthesizing all information into a comprehensive response
        """
        try:
            # Collect context from all available sources
            contexts = []
            sources = []
            
            # 1. Search document if available
            if has_document and self.vector_store:
                doc_results = self._search_document(query)
                if "No relevant information" not in doc_results and "Error" not in doc_results:
                    contexts.append(f"📄 **Document Content:**\n{doc_results}")
                    sources.append("Document")
            
            # 2. Search Wikipedia for factual context
            if self.web_search_manager:
                wiki_results = self._search_wikipedia(query)
                if "No Wikipedia results" not in wiki_results and "Error" not in wiki_results:
                    contexts.append(f"📚 **Wikipedia Context:**\n{wiki_results}")
                    sources.append("Wikipedia")
                
                # 3. Search web for additional perspectives
                web_results = self._search_web(query)
                if "No web search results" not in web_results and "Error" not in web_results:
                    contexts.append(f"🌐 **Web Search Results:**\n{web_results}")
                    sources.append("Web Search")
            
            # 4. Synthesize comprehensive response
            if contexts:
                combined_context = "\n\n".join(contexts)
                
                synthesis_prompt = f"""Based on the following information sources, provide a comprehensive and well-structured answer to: {query}

AVAILABLE INFORMATION:
{combined_context}

Please provide a response that:
1. Directly answers the user's question
2. Combines insights from multiple sources when relevant
3. Is well-organized with clear sections
4. Cites the sources used (Document, Wikipedia, Web)
5. Is engaging and easy to understand

Response:"""
                
                response = self.llm.invoke(synthesis_prompt)
                
                # Add source attribution
                source_text = f"\n\n**Sources used:** {', '.join(sources)}"
                return f"{response}{source_text}"
            
            else:
                return "I couldn't find relevant information to answer your question. Please try rephrasing or ask about something else."
                
        except Exception as e:
            logger.error(f"Enhanced RAG response error: {e}")
            return f"I encountered an error while researching your question: {str(e)}"


def create_rag_agent(vector_store=None, web_search_manager=None) -> EnhancedRAGAgent:
    """Factory function to create an enhanced RAG agent."""
    return EnhancedRAGAgent(vector_store=vector_store, web_search_manager=web_search_manager)