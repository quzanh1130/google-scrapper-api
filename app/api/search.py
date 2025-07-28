import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core import google_search, GoogleSearchRequest, logger

router = APIRouter()

@router.post("/")
async def search_google(request: GoogleSearchRequest):
    """
    API endpoint for Google search.
    Accepts search query and optional proxy parameter.
    """
    try:
        logger.info(f"Received search request for: {request.query}")
        logger.info(f"Request parameters: {request.dict()}")
        
        # Call the simplified google search function
        results = await google_search(
            query=request.query,
            device=request.device,
            language=request.language,
            location=request.location,
            num_pages=request.num_pages,
            user_proxy=request.proxy
        )
        
        if results is None:
            logger.error("Search function returned None - check logs above for detailed error information")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "400",
                    "message": "Failed to fetch search results from Google. Check server logs for details.",
                    "success": False,
                    "data": None
                }
            )
        
        logger.info(f"Search completed successfully with {len(results)} results")
        return JSONResponse(
            status_code=200,
            content={
                "status": "200",
                "message": "Search completed successfully",
                "success": True,
                "data": {
                    "query": request.query,
                    "total_results": len(results),
                    "results": results
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error in search_google API: {type(e).__name__}: {str(e)}")
        logger.error(f"Full exception details:", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "500", 
                "message": f"Internal server error: {str(e)}", 
                "success": False,
                "data": None
            }
        )