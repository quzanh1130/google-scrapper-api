from pydantic import BaseModel, Field
from typing import Optional

class GoogleSearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    language: str = Field("vi", description="Language of the search results (default: vi)")
    location: str = Field("VN", description="Geographical location for the search (default: VN)")
    num_pages: int = Field(1, description="Number of search pages to fetch (1-10)", ge=1, le=10)
    device: str = Field("desktop", description="Device type: desktop or mobile")
    proxy: Optional[str] = Field(None, description="Optional proxy in format ip:port or user:pass@ip:port")
