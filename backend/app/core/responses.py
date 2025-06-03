"""
Common response models and utilities for API responses.
"""
from typing import Any, Optional, Dict, List
from pydantic import BaseModel


class ResponseBase(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None


class DataResponse(ResponseBase):
    """Response with data payload."""
    data: Any


class ErrorResponse(ResponseBase):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(ResponseBase):
    """Paginated response model."""
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


def create_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized success response."""
    response = {"success": True, "data": data}
    if message:
        response["message"] = message
    return response


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {"success": False, "message": message}
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    return response
