import uvicorn
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File , Form
from pydantic import BaseModel
import tempfile
import shutil
import data_query
import data_update
import log
import model_update
from model_RESNET import predict_category as predict_category_resnet
from model_BERT import modele_bert, convert_prediction_to_thematique_and_code
import numpy as np
from model_Fusion import predict
from fastapi.responses import JSONResponse
from typing import Dict




app = FastAPI(title="API RAKUTEN")

# Modèles Pydantic
class LoginData(BaseModel):
    username: str
    password: str

class MessageResponse(BaseModel):
    message: str

class TextItem(BaseModel):
    text: str

# Routes

@app.post("/model/resnet/predict")
async def predict_resnet_endpoint(file: UploadFile):
    try:
        # Utilisez la fonction renommée ici et supprimez "await"
        category, thematique = predict_category_resnet(file)
        return {"category": category, "thematique": thematique}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/model/bert/predict")
async def predict_category(item: TextItem):
    try:
        prediction = modele_bert(item.text)
        prd_type_code, thematique = convert_prediction_to_thematique_and_code(prediction)
        return {
            "prd_type_code": prd_type_code,
            "thematique": thematique
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/model/fusion/predict")
async def predict_endpoint(text: str = Form(...), image: UploadFile = UploadFile(...)):
    image_contents = await image.read()
    with open("temp_image.jpg", "wb") as f:
        f.write(image_contents)
    
    prdtypecode, thematique = predict(text, "temp_image.jpg")
    return JSONResponse(content={"prdtypecode": prdtypecode, "thematique": thematique})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

