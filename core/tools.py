from langchain_core.tools import Tool

# Try to import TavilySearchResults, but make it optional
try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    search_tool = TavilySearchResults(
        max_results=2,
        description="Use this for searching the internet for current events or facts."
    )
    HAS_TAVILY = True
except ImportError:
    HAS_TAVILY = False
    print("⚠️ TavilySearchResults not available. Web search tool will be disabled.")

def create_tutor_tools(vectorstore):
    """Create tools for the tutor agent."""
    retriever = vectorstore.as_retriever()
    
    # Create a custom retriever tool using Tool class
    def pdf_search(query: str) -> str:
        """Search for information inside the uploaded PDF notes.
        
        Args:
            query: The search query to find relevant information in the PDF.
            
        Returns:
            A string containing the relevant information from the PDF.
        """
        try:
            docs = retriever.invoke(query)
            if not docs:
                return "No relevant information found in the PDF notes."
            
            # Combine all retrieved documents
            results = []
            for doc in docs:
                content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                results.append(content)
            
            return "\n\n".join(results[:2])  # Return top 3 results
        except Exception as e:
            return f"Error searching PDF: {str(e)}"
    
    retriever_tool = Tool(
        name="PDF_Search",
        description="Search for information inside the uploaded PDF notes. Use this tool to answer questions based on the study material.",
        func=pdf_search
    )
    
    # Return tools (only include search_tool if available)
    tools = [retriever_tool]
    if HAS_TAVILY:
        tools.append(search_tool)
    
    return tools