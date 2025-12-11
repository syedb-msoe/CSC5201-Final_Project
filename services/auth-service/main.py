from fastapi import FastAPI, HTTPException, Depends
from models import UserCreate, UserLogin, User
from utils import hash_password, verify_password, create_access_token
import database
from auth import get_current_user

app = FastAPI(title="Auth Service")


@app.post("/register")
def register(user: UserCreate):
    existing = database.find_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pass = hash_password(user.password)
    new_user = database.create_user(user.email, hashed_pass)

    return {"id": new_user["id"], "email": new_user["email"]}


@app.post("/login")
def login(user: UserLogin):
    db_user = database.find_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=403, detail="Incorrect password")

    token = create_access_token({
        "sub": db_user["id"],
        "email": db_user["email"]
    })

    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
def me(current: User = Depends(get_current_user)):
    return current
