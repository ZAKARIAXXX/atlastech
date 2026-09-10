from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def api_health():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "atlastech-api",
    }
