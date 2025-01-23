from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from v0 import router as router_v0
from core.settings import settings

import uvicorn


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    custom_response = {
        "detail": errors[0]['msg'],
    }

    return JSONResponse(
        status_code=422,
        content=custom_response
    )

app.include_router(router_v0, prefix=settings.api.prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)