from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse,HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from typing import Optional,List
import httpx
import jwt
import uuid
import os
import json
import numpy as np 
import shutil
import pandas as pd
from script_de_prediction import predict , preprocess_image_for_display
import requests
import stat
import subprocess


app = FastAPI(title='RAKUTEN API')

AUTH_SERVICE_URL = "http://users-db:8001/auth"


SECRET_KEY = "IkxhcGV0aXRlbWFpc29uIg=="


security = HTTPBasic()


headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
}



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



def require_role(*allowed_roles):
    """
    Crée un décorateur pour vérifier si l'utilisateur possède les rôles autorisés.

    Args:
        *allowed_roles (str): Les rôles autorisés pour accéder à la route.

    Returns:
        Callable: Une fonction asynchrone qui vérifie les rôles de l'utilisateur et lève une exception HTTP 403 (Accès interdit)
        s'il n'a pas les rôles autorisés.

    Example:
        Utilisez cette fonction comme décorateur pour restreindre l'accès à une route spécifique aux rôles autorisés. Par exemple :

        @app.post("/admin_only_route", include_in_schema=False)
        async def admin_only_route(payload: dict = Depends(require_role("admin"))):
            return {"message": "Accès administrateur autorisé"}

        Dans cet exemple, seuls les utilisateurs avec le rôle "admin" auront accès à la route "/admin_only_route".
    """
    async def role_checker(credentials: HTTPBasicCredentials = Depends(security)):
        """
    Vérifie les rôles de l'utilisateur à partir des informations d'identification de base HTTP.

    Args:
        credentials (HTTPBasicCredentials): Les informations d'identification de base HTTP de l'utilisateur.

    Returns:
        dict: Un dictionnaire contenant les informations du token utilisateur si les rôles sont autorisés.

    Raises:
        HTTPException: Si l'utilisateur n'a pas les rôles autorisés, une exception HTTP 403 (Accès interdit) est levée
        avec un détail indiquant que l'accès n'est pas autorisé pour ce rôle.
        """

        token = await get_token(credentials)
        payload = verify_token(token)
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Accès non autorisé pour ce rôle")
        return payload
    return role_checker






@app.post("/admin_only_route", include_in_schema=False)
async def admin_only_route(payload: dict = Depends(require_role("admin"))):
    """
    Route pour accéder à des fonctionnalités réservées aux administrateurs.
    
    return {"message": "Accès administrateur autorisé"}
    """

@app.post("/predict")
async def predict_endpoint(
    payload: dict = Depends(require_role("user", "admin")),
    text: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """
    Endpoint pour la prédiction en utilisant un texte et une image.

    Args:
        token (str, optional): Le token JWT pour l'authentification. Obtenu à partir de l'en-tête HTTP.
        text (str): Le texte à utiliser pour la prédiction.
        image (UploadFile, optional): Le fichier image à utiliser pour la prédiction. Par défaut, None.

    Returns:
        JSONResponse: Une réponse JSON contenant les résultats de la prédiction.

    Raises:
        HTTPException: En cas d'erreur lors de la prédiction ou si le fichier image est manquant.
    """
    try:

        
        temp_dir = "/app/Conteneur_API/temp"

        os.makedirs(temp_dir, exist_ok=True)

        images_temp_dir = os.path.join(temp_dir, "images_temp")
        text_temp_dir = os.path.join(temp_dir, "text_temp")
        numpy_temp_dir = os.path.join(temp_dir, "numpy_temp")

        os.makedirs(images_temp_dir, exist_ok=True)
        os.makedirs(text_temp_dir, exist_ok=True)
        os.makedirs(numpy_temp_dir, exist_ok=True)

        base_filename = str(uuid.uuid4())
        image_filename = f"{base_filename}.jpg"
        json_filename = f"{base_filename}.json"
        np_filename = f"{base_filename}.npy"

        image_filepath = os.path.join(images_temp_dir, image_filename)
        json_filepath = os.path.join(text_temp_dir, json_filename)
        np_filepath = os.path.join(numpy_temp_dir, np_filename) 

        if image:
            image_contents = await image.read()
            with open(image_filepath, "wb") as f:
                f.write(image_contents)
                
            np_image = preprocess_image_for_display(image_filepath)
            
            np.save(np_filepath, np_image)

            prdtypecode, thematique = predict(text, image_filepath)

            data_to_save = {"prdtypecode": prdtypecode, "img_pd": image_filename, "description_complete": text}

            with open(json_filepath, "w") as json_file:
                json.dump(data_to_save, json_file)

            return JSONResponse(content={"prdtypecode": prdtypecode, "thematique": thematique})
        else:
            raise HTTPException(status_code=400, detail="Image file is missing")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@app.get("/list_temp_data", response_class=HTMLResponse)
async def list_temp_data(payload: dict = Depends(require_role("admin"))):
    """
    Endpoint pour lister et afficher les fichiers temporaires (images et JSON).

    Returns:
        HTMLResponse: Une réponse HTML affichant les liens vers les fichiers temporaires.
    """    
    images_temp_dir = "/app/Conteneur_API/temp/images_temp"
    
    
    text_temp_dir = "/app/Conteneur_API/temp/text_temp"

    
    if not os.path.exists(images_temp_dir):
        return HTMLResponse(content="<p>Le répertoire d'images temporaires est vide.</p>")
    
    
    image_files = [f for f in os.listdir(images_temp_dir) if f.endswith(".jpg")]
    
    
    json_files = [f for f in os.listdir(text_temp_dir) if f.endswith(".json")]

    
    base_url = "http://localhost:8000"  

    
    html_content = "<h1>Images Temporaires</h1>"
    for image_filename in image_files:
        image_url = f"{base_url}/view_temp_image/{image_filename}"
        html_content += f'<a href="{image_url}" target="_blank">{image_filename}</a><br>'

    
    html_content += "<h1>Fichiers JSON Temporaires</h1>"
    for json_filename in json_files:
        json_url = f"{base_url}/view_temp_json/{json_filename}"
        with open(os.path.join(text_temp_dir, json_filename), "r") as json_file:
            json_data = json.load(json_file)
            json_content = json.dumps(json_data, indent=4)
            html_content += f'<h2>{json_filename}</h2><pre>{json_content}</pre><br>'

    return HTMLResponse(content=html_content)






@app.get("/view_temp_image/{image_filename}", include_in_schema=False)
async def view_temp_image(image_filename: str, payload: dict = Depends(require_role("admin"))):
    """
    Endpoint pour afficher une image temporaire.

    Args:
        image_filename (str): Le nom du fichier image à afficher.

    Returns:
        FileResponse: Une réponse de fichier pour afficher l'image.

    Raises:
        HTTPException: Si le fichier image n'est pas trouvé.
    """    
    image_path = f"/app/Conteneur_API/temp/images_temp/{image_filename}"
    
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    
    return FileResponse(image_path, media_type="image/jpeg")






@app.patch("/modify_json/{filename}")
async def modify_json(filename: str, prdtypecode: int = Form(...), payload: dict = Depends(require_role("admin"))):
    """
    Endpoint pour modifier le prdtypecode dans un fichier JSON.
    Accessible uniquement par les administrateurs.

    Args:
        filename (str): Le nom du fichier JSON à modifier.
        prdtypecode (int): La nouvelle valeur pour prdtypecode.

    Returns:
        JSONResponse: Une réponse JSON indiquant le succès de la modification.

    Raises:
        HTTPException: Si le fichier JSON n'est pas trouvé ou en cas d'erreur de token.
    """
    try:
        
        text_temp_dir = "/app/Conteneur_API/temp/text_temp"
        json_filepath = os.path.join(text_temp_dir, f"{filename}.json")

        
        if not os.path.exists(json_filepath):
            raise HTTPException(status_code=404, detail="JSON file not found")

        
        with open(json_filepath, "r") as file:
            json_data = json.load(file)

        
        json_data['prdtypecode'] = prdtypecode

        
        with open(json_filepath, "w") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)

        return JSONResponse(content={"message": "JSON data updated successfully"})

    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@app.post("/validate_prediction/{filename}")
async def validate_prediction(filename: str, validation: bool, payload: dict = Depends(require_role("admin"))):
    """
    Valide une prédiction enregistrée avec les données du fichier spécifié.

    :param filename: Le nom du fichier à valider.
    :type filename: str
    :param validation: Indique si la validation est réussie ou non.
    :type validation: bool
    :param payload: Les données du payload pour l'authentification de l'administrateur.
    :type payload: dict

    :return: Un message de validation enregistrée.
    :rtype: dict

    :raises HTTPException 404: Si le fichier Numpy spécifié n'existe pas.
    :raises HTTPException 500: Si une erreur inattendue se produit.
    """
    try:

        
        temp_dir = "/app/Conteneur_API/temp"
        data_dir = "/app/data"
        
        images_temp_dir = os.path.join(temp_dir, "images_temp")
        text_temp_dir = os.path.join(temp_dir, "text_temp")
        numpy_temp_dir = os.path.join(temp_dir, "numpy_temp")

        
        image_filepath = os.path.join(images_temp_dir, f"{filename}.jpg")
        json_filepath = os.path.join(text_temp_dir, f"{filename}.json")
        np_filepath = os.path.join(numpy_temp_dir, f"{filename}.npy")
        np_dest_path = os.path.join(data_dir, f"{filename}.npy")  
        csv_filepath = os.path.join(data_dir, f"{filename}.csv")

        if validation:
            
            if os.path.exists(np_filepath):
                shutil.move(np_filepath, np_dest_path)
                
                os.chmod(np_dest_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # Permissions 777
            else:
                raise HTTPException(status_code=404, detail=f"Numpy file {filename}.npy does not exist.")

            
            if os.path.exists(json_filepath):
                with open(json_filepath, 'r') as json_file:
                    json_data = json.load(json_file)
                df = pd.DataFrame([json_data])
                df.to_csv(csv_filepath, index=False)
                os.chmod(csv_filepath, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # Permissions 777

                # Supprimer le fichier JSON
                os.remove(json_filepath)
                os.remove(image_filepath)
            
            dag_run_config = {"conf": {}}
            
            AIRFLOW_API_URL = "http://airflow:8080/api/v1/dags/api_dag/dagRuns"
            
            AIRFLOW_USER = "admin"
            AIRFLOW_PASSWORD = "admin"
            
            auth_airflow = (AIRFLOW_USER, AIRFLOW_PASSWORD)
            
            response = requests.post(AIRFLOW_API_URL, json=dag_run_config, auth=auth_airflow, headers=headers)

            
            if response.status_code == 200:
                print("DAG déclenché avec succès!")
            
            else:
                print(f"Échec du déclenchement du DAG. Statut de la réponse : {response.status_code}")
                print(response.text)

        
        else:
            # Définir les chemins des répertoires dans le nouveau volume partagé
            backup_csv_dir = os.path.join("/app/drive", "csv")
            backup_images_dir = os.path.join("/app/drive", "jpg")
            backup_numpy_dir = os.path.join("/app/drive", "npy")

            # Créer les dossiers s'ils n'existent pas
            os.makedirs(backup_csv_dir, exist_ok=True)
            os.makedirs(backup_images_dir, exist_ok=True)
            os.makedirs(backup_numpy_dir, exist_ok=True)

            # Déplacer ou copier les fichiers dans les répertoires appropriés
            if os.path.exists(json_filepath):
                with open(json_filepath, 'r') as json_file:
                    json_data = json.load(json_file)

                # Convertir les données JSON en DataFrame puis en CSV
                df = pd.DataFrame([json_data])
                csv_backup_filepath = os.path.join(backup_csv_dir, f"{filename}.csv")
                df.to_csv(csv_backup_filepath, index=False)

                # Supprimer le fichier JSON temporaire
                os.remove(json_filepath)

            if os.path.exists(image_filepath):
                image_backup_filepath = os.path.join(backup_images_dir, f"{filename}.jpg")
                shutil.move(image_filepath, image_backup_filepath)

            if os.path.exists(np_filepath):
                np_backup_filepath = os.path.join(backup_numpy_dir, f"{filename}.npy")
                shutil.move(np_filepath, np_backup_filepath)

    except Exception as e:
        print(f"Erreur lors de la sauvegarde des fichiers dans le volume partagé: {e}")

        return JSONResponse(content={"message": "Validation enregistrée", "filename": filename})
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

