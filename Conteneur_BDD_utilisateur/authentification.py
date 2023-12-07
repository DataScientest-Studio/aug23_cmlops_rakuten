from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import jwt
import time

app = FastAPI()

security = HTTPBasic()

SECRET_KEY = "IkxhcGV0aXRlbWFpc29uIg=="
VALID_USERNAME = "test"
VALID_PASSWORD = "secret63"

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Vérifie les identifiants fournis via l'authentification HTTP Basic.

    Args:
        credentials (HTTPBasicCredentials, optional): Les identifiants de l'utilisateur. 
        Dépend de l'authentification HTTP Basic (security).

    Returns:
        str: Le nom d'utilisateur validé.

    Raises:
        HTTPException: Si les identifiants sont incorrects, renvoie une erreur 401 Non autorisé.
    """
    if credentials.username == VALID_USERNAME and credentials.password == VALID_PASSWORD:
        return credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.post("/auth")
async def authenticate(username: str = Depends(verify_credentials)):
    """
    Authentifie l'utilisateur et renvoie un token JWT.

    Cette route génère un token JWT pour l'utilisateur après une authentification réussie. 
    Le token expire après une heure.

    Args:
        username (str): Le nom d'utilisateur validé, obtenu à partir de la fonction `verify_credentials`.

    Returns:
        dict: Un dictionnaire contenant le token JWT généré.
    """
    expiration_time = time.time() + 3600  # Token valide pour 1 heure
    token = jwt.encode({"username": username, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")
    return {"token": token}


