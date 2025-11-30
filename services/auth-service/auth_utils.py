import jwt
import datetime
import os

SECRET = os.getenv("JWT_SECRET", "dev-secret")

def create_token(username: str, admin: bool):
    return jwt.encode(
        {
            "sub": username,
            "admin": admin,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        SECRET,
        algorithm="HS256"
    )