# utils/error_handling.py
from fastapi import HTTPException
from functools import wraps
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("dreamteller")

def handle_api_errors(func):
    """
    Decorator for route handlers to catch and handle errors gracefully.
    
    Args:
        func: The route handler function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise FastAPI HTTP exceptions directly
            raise
        except Exception as e:
            # Log the full exception traceback
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Convert to appropriate HTTP exception
            if "api key" in str(e).lower():
                # Authentication error
                raise HTTPException(status_code=401, detail="API authentication failed")
            elif "rate limit" in str(e).lower():
                # Rate limiting
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
            elif "not found" in str(e).lower():
                # Not found error
                raise HTTPException(status_code=404, detail=str(e))
            elif "invalid" in str(e).lower():
                # Validation error
                raise HTTPException(status_code=400, detail=str(e))
            else:
                # Generic server error
                raise HTTPException(
                    status_code=500, 
                    detail=f"An unexpected error occurred: {str(e)}"
                )
    
    return wrapper