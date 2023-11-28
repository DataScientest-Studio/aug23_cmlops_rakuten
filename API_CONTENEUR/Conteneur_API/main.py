from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from airflow.api.client.local_client import Client
from datetime import datetime, timedelta
import httpx
import jwt
import uuid
import os
from script_de_prediction import predict

app = FastAPI(title='RAKUTEN API')
# App Airflow
client = Client(api_base_url='http://localhost:8080/api/v1')
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

    Args:
        token (str): Le token JWT pour l'authentification.
        text (str): Le texte à utiliser pour la prédiction.
        image (UploadFile, optional): L'image à utiliser pour la prédiction. Par défaut à None.

    Returns:
        JSONResponse: La réponse contenant le code de type de produit et la thématique prédits.

    Raises:
        HTTPException: Si le fichier image est manquant ou si la vérification du token échoue.
    """
    payload = verify_token(token)

    if image:
        temp_image_path = "temp_image_" + str(uuid.uuid4()) + ".jpg"
        try:
            image_contents = await image.read()
            with open(temp_image_path, "wb") as f:
                f.write(image_contents)
            
            prdtypecode, thematique = predict(text, temp_image_path)
            return JSONResponse(content={"prdtypecode": prdtypecode, "thematique": thematique})
        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    else:
        raise HTTPException(status_code=400, detail="Image file is missing")

    execution_date = datetime.utcnow()
    dag_trigger_response = client.trigger_dag(
        dag_id='recup_data_dag',
        run_id=f"predict_run_{execution_date}",
        conf={'text': text, 'image_path': temp_image_path, 'token': token},
        execution_date=execution_date,
    )
    
    return JSONResponse(content={"message": "Prédiction réussie. DAG déclenché."})

