"""
Web search utilities for SAVIN AI application.
Provides Wikipedia and DuckDuckGo search integration with error handling and result formatting.
"""

import logging
from typing import List, Dict, Any, Optional
import wikipedia
from ddgs import DDGS

from ..config.settings import SearchConfig
from ..data.models import SearchResult
from .exceptions import SearchError


# Configure logging
logger = logging.getLogger(__name__)


class WikipediaSearcher:
    """
    Handles Wikipedia search operations with error handling and result formatting.
    """
    
    def __init__(self):
        self.config = SearchConfig()
        # Configure Wikipedia settings
        wikipedia.set_lang("en")
        wikipedia.set_rate_limiting(True)
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Search Wikipedia for relevant articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        Raises:
            SearchError: If search fails
        """
        max_results = max_results or self.config.MAX_SEARCH_RESULTS
        
        try:
            logger.info(f"Searching Wikipedia for: {query}")
            
            # Search for pages
            search_results = wikipedia.search(query, results=max_results * 2)  # Get more to filter
            results = []
            
            for title in search_results[:max_results]:
                try:
                    page = wikipedia.page(title, auto_suggest=self.config.WIKIPEDIA_AUTO_SUGGEST)
                    
                    # Get summary with sentence limit
                    summary = wikipedia.summary(
                        title, 
                        sentences=self.config.WIKIPEDIA_SENTENCES,
                        auto_suggest=self.config.WIKIPEDIA_AUTO_SUGGEST
                    )
                    
                    # Limit summary length
                    if len(summary) > 500:
                        summary = summary[:497] + "..."
                    
                    result = SearchResult(
                        title=page.title,
                        url=page.url,
                        summary=summary,
                        source="Wikipedia"
                    )
                    
                    results.append(result)
                    
                    if len(results) >= max_results:
                        break
                        
                except wikipedia.exceptions.DisambiguationError as e:
                    # Handle disambiguation by taking the first option
                    try:
                        page = wikipedia.page(e.options[0])
                        summary = wikipedia.summary(e.options[0], sentences=self.config.WIKIPEDIA_SENTENCES)
                        
                        if len(summary) > 500:
                            summary = summary[:497] + "..."
                        
                        result = SearchResult(
                            title=page.title,
                            url=page.url,
                            summary=summary,
                            source="Wikipedia"
                        )
                        
                        results.append(result)
                        
                    except Exception as inner_e:
                        logger.warning(f"Failed to resolve disambiguation for {title}: {inner_e}")
                        continue
                        
                except wikipedia.exceptions.PageError:
                    logger.warning(f"Wikipedia page not found: {title}")
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error processing Wikipedia page {title}: {e}")
                    continue
            
            logger.info(f"Found {len(results)} Wikipedia results")
            return results
            
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            raise SearchError(f"Wikipedia search failed: {str(e)}", "WIKIPEDIA_ERROR")


class DuckDuckGoSearcher:
    """
    Handles DuckDuckGo web search operations with error handling and result formatting.
    """
    
    def __init__(self):
        self.config = SearchConfig()
        self.ddgs = DDGS(
            timeout=self.config.SEARCH_TIMEOUT
        )
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Search DuckDuckGo for web results.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
            
        Raises:
            SearchError: If search fails
        """
        max_results = max_results or self.config.MAX_SEARCH_RESULTS
        
        try:
            logger.info(f"Searching DuckDuckGo for: {query}")
            
            search_results = self.ddgs.text(
                query, 
                region=self.config.DUCKDUCKGO_REGION,
                safesearch=self.config.DUCKDUCKGO_SAFE_SEARCH,
                max_results=max_results
            )
            
            results = []
            
            for result in search_results:
                title = result.get("title", "").strip()
                url = result.get("href", "").strip()
                body = result.get("body", "").strip()
                
                # Skip results with missing essential information
                if not title or not url:
                    continue
                
                # Limit body length
                if len(body) > 500:
                    body = body[:497] + "..."
                
                search_result = SearchResult(
                    title=title,
                    url=url,
                    summary=body,
                    source="DuckDuckGo"
                )
                
                results.append(search_result)
                
                if len(results) >= max_results:
                    break
            
            logger.info(f"Found {len(results)} DuckDuckGo results")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise SearchError(f"DuckDuckGo search failed: {str(e)}", "DUCKDUCKGO_ERROR")


class WebSearchManager:
    """
    Main web search manager that coordinates Wikipedia and DuckDuckGo searches.
    """
    
    def __init__(self):
        self.wikipedia_searcher = WikipediaSearcher()
        self.duckduckgo_searcher = DuckDuckGoSearcher()
        self.config = SearchConfig()
    
    def search_wikipedia(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search Wikipedia and return results as dictionaries (backward compatibility).
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of result dictionaries
        """
        try:
            results = self.wikipedia_searcher.search(query, max_results)
            return [result.to_dict() for result in results]
        except SearchError:
            logger.error(f"Wikipedia search failed for query: {query}")
            return []
    
    def search_duckduckgo(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo and return results as dictionaries (backward compatibility).
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of result dictionaries
        """
        try:
            results = self.duckduckgo_searcher.search(query, max_results)
            return [result.to_dict() for result in results]
        except SearchError:
            logger.error(f"DuckDuckGo search failed for query: {query}")
            return []
    
    def combined_search(self, query: str, include_wikipedia: bool = True, 
                       include_web: bool = True, max_results_per_source: int = 2) -> List[SearchResult]:
        """
        Perform combined search across Wikipedia and DuckDuckGo.
        
        Args:
            query: Search query
            include_wikipedia: Whether to include Wikipedia results
            include_web: Whether to include web search results
            max_results_per_source: Maximum results per search source
            
        Returns:
            Combined list of SearchResult objects
        """
        all_results = []
        
        if include_wikipedia:
            try:
                wiki_results = self.wikipedia_searcher.search(query, max_results_per_source)
                all_results.extend(wiki_results)
            except SearchError as e:
                logger.warning(f"Wikipedia search failed: {e}")
        
        if include_web:
            try:
                web_results = self.duckduckgo_searcher.search(query, max_results_per_source)
                all_results.extend(web_results)
            except SearchError as e:
                logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def format_search_results(self, results: List[SearchResult]) -> str:
        """
        Format search results for display with friendly emojis and bullet points.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Formatted results string
        """
        if not results:
            return "No search results found."
        
        formatted = ""
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result.title} 🌟**\n"
            formatted += f"• **Source:** {result.source} 📚\n"
            formatted += f"• **Summary:** {result.summary}\n"
            formatted += f"• **Link:** [Visit here 🔗]({result.url})\n\n"
        
        return formatted
    
    def create_search_context(self, results: List[SearchResult]) -> str:
        """
        Create context string for AI processing.
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            Context string for AI processing
        """
        if not results:
            return ""
        
        context = "Web search results:\n\n"
        
        for result in results:
            context += f"Title: {result.title}\n"
            context += f"Source: {result.source}\n"
            context += f"Content: {result.summary}\n\n"
        
        return context


class SearchResultFormatter:
    """
    Handles formatting of search results for different display contexts.
    """
    
    @staticmethod
    def format_for_chat(results: List[SearchResult], query: str) -> str:
        """Format search results for chat display"""
        if not results:
            return f"""😅 **No Results Found!**

🎯 **What happened:**
• No results found for "{query}" 🔍
• The search might be too specific or unusual

💡 **Let's try these alternatives:**
• **Rephrase your search** with different keywords 🔄
• **Use more general terms** or try specific phrases 🎯  
• **Try the other search button** for different results! 🔄

✨ **I'm here to help!** Let's find the information you need together! 😊🚀"""
        
        response = f"""🌟 **Search Results for: "{query}"**

🎯 **Quick Summary:**
• Found {len(results)} relevant results 🌍
• Fresh information ready for analysis! ✨

📋 **Results:**"""
        
        for i, result in enumerate(results, 1):
            response += f"\n• **{result.title}** - {result.summary[:100]}... 🌟"
            response += f"\n  🔗 [Visit {result.source.lower()}]({result.url})"
        
        response += "\n\n💡 **Pro Tip:**\n• You can ask me to combine these findings with your document content! 📄✨"
        
        return response
    
    @staticmethod
    def format_error_response(error_type: str, query: str) -> str:
        """Format error response for search failures"""
        return f"""😅 **Search Issue!**

🎯 **What happened:**
• Technical issue with {error_type} search 🛠️
• Query: "{query}"

💡 **Quick solutions:**
• **Try a different search term** 🔄
• **Use the other search button** instead! 🔄  
• **Check your internet connection** 📡

✨ **Don't worry!** I'm still here to help you find what you need! 😊💪"""


# Factory functions
def create_web_search_manager() -> WebSearchManager:
    """Create a new web search manager instance"""
    return WebSearchManager()


def create_wikipedia_searcher() -> WikipediaSearcher:
    """Create a new Wikipedia searcher instance"""
    return WikipediaSearcher()


def create_duckduckgo_searcher() -> DuckDuckGoSearcher:
    """Create a new DuckDuckGo searcher instance"""
    return DuckDuckGoSearcher()


def create_search_result_formatter() -> SearchResultFormatter:
    """Create a new search result formatter instance"""
    return SearchResultFormatter()


# Suggested prompts for quick access
SUGGESTED_PROMPTS = [
    "📝 Summarize this document",
    "🔍 Explain key concepts", 
    "💡 Answer my questions"
]