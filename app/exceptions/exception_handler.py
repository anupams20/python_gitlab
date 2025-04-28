import json
import traceback

from fastapi.responses import JSONResponse
from starlette import status

from app.exceptions import ApplicationException, EntityNotFoundException
from app.main import app
from fastapi import Request, Response, HTTPException


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    stacktrace = traceback.format_exception(exc)
    return JSONResponse(status_code=exc.status_code,
                        content={"message": exc.detail, "stacktrace": json.dumps(stacktrace)})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> Response:
    stacktrace = traceback.format_exception(exc)
    return JSONResponse(status_code=400,
                        content={"message": f"Invalid value: {str(exc)}", "stacktrace": json.dumps(stacktrace)})


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> Response:
    stacktrace = traceback.format_exception(exc)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"message": "Internal Error!", "stacktrace": json.dumps(stacktrace)})

@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc:ApplicationException) -> Response:
    stacktrace = traceback.format_exception(exc)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(exc), "stacktrace": json.dumps(stacktrace)})

@app.exception_handler(EntityNotFoundException)
async def entity_not_found_exception_handler(request: Request, exc:EntityNotFoundException) -> Response:
    stacktrace = traceback.format_exception(exc)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc), "stacktrace": json.dumps(stacktrace)})
