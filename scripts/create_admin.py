import getpass

from sqlalchemy import select

from app.db.session import SessionLocal

from app.models.user import User

from app.core.security import hash_password


def create_admin():

    email = input("Enter admin email: ").strip().lower()

    full_name = input("Enter admin name: ").strip()

    password = getpass.getpass("Enter admin password: ")

    if len(password) < 12:
        raise ValueError(
            "Password must contain at least 12 characters."
        )

    db = SessionLocal()

    try:

        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            print("This email is already registered.")
            return

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role="ADMIN",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("Admin account successfully created.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()