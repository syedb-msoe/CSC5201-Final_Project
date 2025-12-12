import os
from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt

JWT_SECRET = os.getenv("JWT_SECRET", None)
JWT_ALGORITHM = "HS256"

async def get_current_user(request: Request):
    user = await verify_jwt(request)
    return user
    
async def verify_jwt(request: Request):
    """
    Extracts JWT from Authorization header and verifies it.
    Returns a dict with user info if valid.
    """

    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="Auth secret not configured")

    auth_header: str = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, token = get_authorization_scheme_param(auth_header)
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Must contain user ID and email
    if "sub" not in payload or "email" not in payload:
        raise HTTPException(status_code=401, detail="Malformed token")

    return {
        "id": payload["sub"],
        "email": payload["email"]
    }