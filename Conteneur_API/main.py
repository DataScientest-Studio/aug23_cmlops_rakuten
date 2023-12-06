from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
import httpx
import jwt
import uuid
import os
import json
from script_de_prediction import predict

app = FastAPI(title='RAKUTEN API')

# URL du service d'authentification
AUTH_SERVICE_URL = "http://users-db:8001/auth"
# Clé secrète utilisée pour décoder le token JWT
SECRET_KEY = "IkxhcGV0aXRlbWFpc29uIg=="

# Configuration de l'authentification HTTP Basic
security = HTTPBasic()


async def get_token(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Obtient un token JWT en utilisant l'authentification HTTP Basic.

    Args:
        credentials (HTTPBasicCredentials, optional): Les identifiants de l'utilisateur. Par défaut à Depends(security).

    Returns:
        str: Le token JWT obtenu.

    Raises:
        HTTPException: Si l'authentification échoue.
    """    
    async with httpx.AsyncClient() as client:
        response = await client.post(AUTH_SERVICE_URL, auth=(credentials.username, credentials.password))
        if response.status_code == 200:
            return response.json()["token"]
        else:
            raise HTTPException(status_code=response.status_code, detail="Authentication failed")


def verify_token(token: str):
    """
    Vérifie le token JWT.

    Args:
        token (str): Le token JWT à vérifier.

    Returns:
        dict: Les informations décodées du token si valide.

    Raises:
        HTTPException: Si le token est invalide.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


@app.post("/predict")
async def predict_endpoint(token: str = Depends(get_token), text: str = Form(...), image: Optional[UploadFile] = File(None)):
    """
    Endpoint pour la prédiction en utilisant un texte et une image.
    """
    try:
        payload = verify_token(token)

        
        temp_dir = "/app/Conteneur_API/temp"

        
        os.makedirs(temp_dir, exist_ok=True)

        
        images_temp_dir = os.path.join(temp_dir, "images_temp")
        text_temp_dir = os.path.join(temp_dir, "text_temp")

        
        os.makedirs(images_temp_dir, exist_ok=True)
        os.makedirs(text_temp_dir, exist_ok=True)

        json_filename = f"prediction_data_{uuid.uuid4()}.json"
        json_filepath = os.path.join(text_temp_dir, json_filename)
        image_filename = f"image_{uuid.uuid4()}.jpg"
        image_filepath = os.path.join(images_temp_dir, image_filename)

        if image:
            image_contents = await image.read()
            with open(image_filepath, "wb") as f:
                f.write(image_contents)

            prdtypecode, thematique = predict(text, image_filepath)
            data_to_save = {"prdtypecode": prdtypecode, "image_id": image_filename, "description_complete": text}

            with open(json_filepath, "w") as json_file:
                json.dump(data_to_save, json_file)

            return JSONResponse(content={"prdtypecode": prdtypecode, "thematique": thematique})
        else:
            raise HTTPException(status_code=400, detail="Image file is missing")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



