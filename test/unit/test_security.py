from app.core.security import (
    hash_password,
    verify_password,
)

from app.services.token_service import (
    create_access_token,
    decode_token,
)


def test_password_hashing():

    password = "MedicalWriter@2026!"

    hashed = hash_password(password)

    assert hashed != password

    assert verify_password(password, hashed)

    assert not verify_password(
        "WrongPassword@2026",
        hashed,
    )


def test_access_token():

    token = create_access_token(
        user_id="12345678-1234-5678-1234-567812345678",
        role="MEDICAL_WRITER",
    )

    payload = decode_token(token)

    assert payload["sub"] == (
        "12345678-1234-5678-1234-567812345678"
    )

    assert payload["role"] == "MEDICAL_WRITER"

    assert payload["type"] == "access"