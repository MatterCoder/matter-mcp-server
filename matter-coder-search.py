from typing import Any, List, Dict
import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import quote, unquote
import asyncio
import re

# Initialize FastMCP server
mcp = FastMCP("matter-coder-search")

@mcp.tool()
async def search_matter_docs(query: str) -> List[Dict[str, str]]:
    """Search Matter protocol documentation on mattercoder.com
    
    Args:
        query: Search query related to Matter protocol (e.g., 'chip-tool', 'commissioning', 'clusters')
    
    Returns:
        List of dictionaries containing search results with titles and URLs
    """
    # Construct the DuckDuckGo search URL with site:mattercoder.com
    encoded_query = quote(f"site:mattercoder.com {query}")
    search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, follow_redirects=True)
        content = response.text
        
        results = []
        
        # Find all result blocks
        result_blocks = re.finditer(r'<div class="result results_links results_links_deep web-result[^"]*">(.*?)</div>', content, re.DOTALL)
        
        for block in result_blocks:
            block_content = block.group(1)
            
            # Extract title and URL
            title_match = re.search(r'<h2 class="result__title">\s*<a[^>]*class="result__a"[^>]*>(.*?)</a>', block_content, re.DOTALL)
            url_match = re.search(r'<a class="result__url"[^>]*href="//duckduckgo.com/l/\?uddg=(.*?)&', block_content)
            
            if title_match and url_match:
                title = re.sub(r'<.*?>', '', title_match.group(1)).strip()
                encoded_url = url_match.group(1)
                url = unquote(encoded_url)
                
                if url.startswith('https://mattercoder.com'):
                    results.append({
                        'title': title,
                        'url': url
                    })
                    
                    if len(results) >= 5:  # Limit to top 5 results
                        break
        
        return results

async def test_search():
    """Test function to run searches locally"""
    test_queries = [
        "chip-tool commissioning",
        "matter clusters",
        "binding"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: {query}")
        try:
            results = await search_matter_docs(query)
            print(f"Found {len(results)} results:")
            for result in results:
                print(f"- {result['title']}")
                print(f"  {result['url']}\n")
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")

if __name__ == "__main__":
    # If running as script, run the test function
    #asyncio.run(test_search())
    
    # If you still want to run as MCP server, comment out the above line
    # and uncomment the below line
    mcp.run(transport='stdio')
