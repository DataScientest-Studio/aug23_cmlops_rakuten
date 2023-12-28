from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import jwt
import time

app = FastAPI()

security = HTTPBasic()

SECRET_KEY = "IkxhcGV0aXRlbWFpc29uIg=="

users = {
    "admin": {"password": "admin63", "role": "admin"},
    "customer": {"password": "secret63", "role": "user"}
}

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Vérifie les identifiants fournis via l'authentification HTTP Basic.
    """
    user_info = users.get(credentials.username)
    if user_info and user_info["password"] == credentials.password:
        return credentials.username, user_info["role"]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.post("/auth")
async def authenticate(user_details: tuple = Depends(verify_credentials)):
    """
    Authentifie l'utilisateur et renvoie un token JWT.
    """
    username, role = user_details
    expiration_time = time.time() + 3600  
    token = jwt.encode({"username": username, "role": role, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")
    return {"token": token}



