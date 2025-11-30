from fastapi import FastAPI, HTTPException
from fastapi import Body
from auth_utils import create_token

app = FastAPI(title="Auth Service")

@app.post("/auth/login")
def login(username: str = Body(...), password: str = Body(...)):
    if username == "admin" and password == "pass":
        return {"token": create_token(username, admin=True)}
    if username == "user" and password == "pass":
        return {"token": create_token(username, admin=False)}
    raise HTTPException(401, "Invalid credentials")