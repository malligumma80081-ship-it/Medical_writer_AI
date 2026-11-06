from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User


def create_user():

    db = SessionLocal()

    try:
        statement = select(User).where(
            User.email == "developer@example.com"
        )

        existing_user = db.scalar(statement)

        if existing_user:
            print("Development user already exists.")
            return

        user = User(
            full_name="Development User",
            email="developer@example.com",
            # Temporary placeholder only.
            # Day 3 replaces this with a securely hashed password.
            hashed_password="TEMPORARY_NOT_FOR_LOGIN",
            role="ADMIN",
        )

        db.add(user)
        db.commit()

        print("Development user created.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_user()