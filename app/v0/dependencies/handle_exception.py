from fastapi import status, HTTPException
import httpx

from .exceptions import (
    CustomHTTPException, HTTP405Exception, HTTP404Exception, 
    HTTP500Exception, HTTP403Exception, HTTP401Exception,
    RepositoryException, HTTP400Exception
)
from core.settings import settings


def handle_exception(e: Exception):
    EXCEPTION_MAP = {
        HTTP400Exception: status.HTTP_400_BAD_REQUEST,
        HTTP401Exception: status.HTTP_401_UNAUTHORIZED,
        HTTP403Exception: status.HTTP_403_FORBIDDEN,
        HTTP404Exception: status.HTTP_404_NOT_FOUND,
        HTTP405Exception: status.HTTP_405_METHOD_NOT_ALLOWED,
        HTTP500Exception: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    error_code = EXCEPTION_MAP.get(type(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    message = str(e)
    if error_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        message = "Internal Server Error"
    raise HTTPException(status_code=error_code, detail=message)

def handle_http_client_exception(e: Exception):
    EXCEPTION_MAP = {
        httpx.TimeoutException: "Request timeout",
        httpx.HTTPStatusError: f"Http code: {e.response.status_code}",
        httpx.Request: f"Error while request sending",
    }

    settings.statberry_logger.get_loger().error(e)
    error_message = EXCEPTION_MAP.get(type(e), "Internal Server Error")
    raise CustomHTTPException(error_message)