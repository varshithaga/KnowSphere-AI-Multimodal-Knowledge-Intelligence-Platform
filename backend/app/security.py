import bcrypt


def hash_password(password: str) -> str:
    """Turn a plain password into a secure hash."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a typed password against the stored hash (used in login)."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))