from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User


ALLOWED_ROLES = ("ADMIN", "MEDICAL_WRITER", "REVIEWER")


def set_user_role() -> None:
    email = input("Enter registered user email: ").strip().lower()
    print(f"Available roles: {', '.join(ALLOWED_ROLES)}")
    role = input("Enter new role: ").strip().upper()

    if role not in ALLOWED_ROLES:
        raise ValueError(f"Role must be one of: {', '.join(ALLOWED_ROLES)}")

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            raise ValueError("No user is registered with that email.")

        user.role = role
        db.commit()
        print(f"Updated role for {email} to {role}.")


if __name__ == "__main__":
    set_user_role()
