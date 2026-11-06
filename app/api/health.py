from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "service": "medical-writing-ai",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }