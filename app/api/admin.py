from fastapi import APIRouter, Depends

from app.core.dependencies import require_roles

from app.models.user import User


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


@router.get(
    "/dashboard",
    description="Requires an authenticated user with the ADMIN role.",
)
def admin_dashboard(
    current_user: User = Depends(
        require_roles("ADMIN")
    ),
):

    return {
        "message": "Welcome to admin dashboard",
        "user": current_user.email,
        "role": current_user.role,
    }


@router.get(
    "/users",
    description="Requires an authenticated user with the ADMIN role.",
)
def manage_users(
    current_user: User = Depends(
        require_roles("ADMIN")
    ),
):

    return {
        "message": "Admin user management access granted"
    }