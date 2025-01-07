from fastapi import FastAPI, status

import uvicorn


app = FastAPI()

@app.get("/test")
async def test_endpoint(name: str = "World"):
    return {
        "message": f"Hello, {name}!",
        "status": status.HTTP_200_OK
    }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)