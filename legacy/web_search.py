"""
Web search utilities for SAVIN AI
Integrates Wikipedia and DuckDuckGo search functionality
"""
import wikipedia
from ddgs import DDGS
from langchain.tools import Tool
from langchain.schema import Document
import streamlit as st
from typing import List, Dict, Any

class WebSearchManager:
    def __init__(self):
        self.ddgs = DDGS()
    
    def search_wikipedia(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Search Wikipedia for relevant articles"""
        try:
            # Search for pages
            search_results = wikipedia.search(query, results=max_results)
            results = []
            
            for title in search_results[:max_results]:
                try:
                    page = wikipedia.page(title)
                    # Get summary (first 500 chars)
                    summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
                    
                    results.append({
                        "title": page.title,
                        "url": page.url,
                        "summary": summary,
                        "source": "Wikipedia"
                    })
                except wikipedia.exceptions.DisambiguationError as e:
                    # Handle disambiguation by taking the first option
                    try:
                        page = wikipedia.page(e.options[0])
                        summary = page.summary[:500] + "..." if len(page.summary) > 500 else page.summary
                        results.append({
                            "title": page.title,
                            "url": page.url,
                            "summary": summary,
                            "source": "Wikipedia"
                        })
                    except:
                        continue
                except:
                    continue
            
            return results
            
        except Exception as e:
            st.error(f"Wikipedia search error: {str(e)}")
            return []
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search DuckDuckGo for web results"""
        try:
            results = []
            search_results = self.ddgs.text(query, max_results=max_results)
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "summary": result.get("body", ""),
                    "source": "DuckDuckGo"
                })
            
            return results
            
        except Exception as e:
            st.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def combined_search(self, query: str, include_wikipedia: bool = True, include_web: bool = True) -> List[Dict[str, Any]]:
        """Perform combined search across Wikipedia and DuckDuckGo"""
        all_results = []
        
        if include_wikipedia:
            wiki_results = self.search_wikipedia(query, max_results=2)
            all_results.extend(wiki_results)
        
        if include_web:
            web_results = self.search_duckduckgo(query, max_results=3)
            all_results.extend(web_results)
        
        return all_results
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display with friendly emojis and bullet points"""
        if not results:
            return "No search results found."
        
        formatted = ""
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result['title']} 🌟**\n"
            formatted += f"• **Source:** {result['source']} 📚\n"
            formatted += f"• **Summary:** {result['summary']}\n"
            formatted += f"• **Link:** [Visit here 🔗]({result['url']})\n\n"
        
        return formatted
    
    def create_search_context(self, results: List[Dict[str, Any]]) -> str:
        """Create context string for AI processing"""
        if not results:
            return ""
        
        context = "Web search results:\n\n"
        for result in results:
            context += f"Title: {result['title']}\n"
            context += f"Source: {result['source']}\n"
            context += f"Content: {result['summary']}\n\n"
        
        return context

# Clean, focused prompt suggestions
SUGGESTED_PROMPTS = [
    "� Summarize this document",
    "� Explain key concepts", 
    "� Answer my questions"
]

def get_web_search_tool(web_search_manager: WebSearchManager):
    """Create a LangChain tool for web search"""
    def search_web(query: str) -> str:
        results = web_search_manager.combined_search(query)
        return web_search_manager.create_search_context(results)
    
    return Tool(
        name="web_search",
        description="Search the web using Wikipedia and DuckDuckGo for current information",
        func=search_web
    )
