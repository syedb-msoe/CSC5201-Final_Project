from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from utils import decode_token
from models import User
import database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_doc = database.find_user_by_email(email)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return User(id=user_doc["id"], email=user_doc["email"])