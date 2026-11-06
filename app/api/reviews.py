from fastapi import APIRouter, Depends

from app.core.dependencies import require_roles

from app.models.user import User


router = APIRouter(
    prefix="/reviews",
    tags=["Medical Reviews"],
)


@router.get(
    "/pending",
    description="Requires an authenticated user with the ADMIN or REVIEWER role.",
)
def pending_reviews(
    current_user: User = Depends(
        require_roles("ADMIN", "REVIEWER")
    ),
):

    return {
        "message": "Review access granted",
        "reviewer": current_user.email,
    }