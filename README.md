# Google Search API

A simple FastAPI service for performing Google searches with optional proxy support.

## Features

- Simple Google search functionality
- Optional proxy support (user can provide their own proxy)
- Support for both desktop and mobile search results
- Configurable search parameters (language, location, number of pages)
- Docker containerized

## API Endpoints

### POST /search

Perform a Google search with optional parameters.

**Request Body:**
```json
{
  "query": "your search query",
  "language": "vi",
  "location": "VN", 
  "num_pages": 1,
  "device": "desktop",
  "proxy": "ip:port" // optional
}
```

**Parameters:**
- `query` (required): Search query string
- `language` (optional): Language code (default: "vi")
- `location` (optional): Location code (default: "VN")
- `num_pages` (optional): Number of pages to fetch 1-10 (default: 1)
- `device` (optional): Device type "desktop" or "mobile" (default: "desktop")
- `proxy` (optional): Proxy in format "ip:port" or "user:pass@ip:port"

**Response:**
```json
{
  "status": "200",
  "message": "Search completed successfully",
  "success": true,
  "data": {
    "query": "your search query",
    "total_results": 10,
    "results": [
      {
        "url": "https://example.com",
        "title": "Page Title",
        "display_url": "example.com",
        "description": "Page description..."
      }
    ]
  }
}
```

## Usage Examples

### Basic Search (No Proxy)
```bash
curl -X POST "http://localhost:8386/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming"
  }'
```

### Search with Custom Proxy
```bash
curl -X POST "http://localhost:8386/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming",
    "proxy": "192.168.1.100:8080"
  }'
```

### Search with All Parameters
```bash
curl -X POST "http://localhost:8386/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming",
    "language": "en",
    "location": "US",
    "num_pages": 2,
    "device": "desktop",
    "proxy": "user:pass@proxy.example.com:8080"
  }'
```

## Running with Docker

1. Build the image:
```bash
docker build -t google-search-api .
```

2. Run the container:
```bash
docker run -p 8386:8386 google-search-api
```

3. Access the API at `http://localhost:8386`

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install firefox
```

3. Run the development server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8386 --reload
```

## Notes

- The service will automatically fall back to requests-based scraping if browser automation fails
- If no proxy is provided, the service will make direct requests to Google
- The service includes basic anti-detection measures for web scraping
- Results are extracted from Google's search result pages and may change if Google updates their HTML structure