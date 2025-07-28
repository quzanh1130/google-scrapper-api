from fastapi import FastAPI
from app.api import search

app = FastAPI(title="Google Search API", description="Simple Google Search API with optional proxy support")

# Include routers
app.include_router(search.router, prefix="/api/search", tags=["Google Search"])

@app.get("/")
async def root():
    return {
        "status": "200", 
        "message": "Welcome to the Google Search API!", 
        "data": {
            "endpoints": [
                "POST /search - Perform Google search with optional proxy",
                "GET /search/test - Test if the service is running",
                "POST /search/debug - Debug endpoint with detailed logging"
            ]
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "200",
        "message": "OK"
    }