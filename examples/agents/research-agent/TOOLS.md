# Tools

## web_search

Search the web for information.

**When to use:** When you need current information, facts, or data that you don't have in your training.

**Parameters:**
- `query` (string, required): The search query

**Example:**
```json
{
  "tool": "web_search",
  "query": "electric vehicle market trends 2026"
}
```

## web_fetch

Fetch and read content from a URL.

**When to use:** When you have a specific URL and need to read its content.

**Parameters:**
- `url` (string, required): The URL to fetch

**Example:**
```json
{
  "tool": "web_fetch",
  "url": "https://example.com/article"
}
```

## Notes

- Use web_search first to find relevant URLs
- Use web_fetch to read specific pages in detail
- Always cite the sources you use
- If a tool fails, try alternative queries
