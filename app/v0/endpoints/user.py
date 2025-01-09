from fastapi import APIRouter


router = APIRouter(tags=["User"], prefix="/user")

@router.get("/test/")
async def test():
    return {
        "status": "success",
        "data": {
            "id": 1,
            "name": test
        },
        "message": "completed"
    }