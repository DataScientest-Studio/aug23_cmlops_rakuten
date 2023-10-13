from fastapi import FastAPI, HTTPException
from transformers import BertTokenizer, TFBertModel
from pydantic import BaseModel
import numpy as np
import pandas as pd
from typing import List

app = FastAPI()

# Chargement du modèle BERT

loaded_bert_model = TFBertModel.from_pretrained('bert-base-multilingual-cased')
loaded_bert_model.load_weights(r'C:\Users\PatriciaWintrebert\Projects\Rakuten MLOps\MLOps_API\model\model_bert.h5')

# Fonction pour effectuer la tokenisation et la prédiction
def predict_with_model(texts: List[str]):
    input_ids = []
    attention_mask = []

    for text in texts:
        tokenized = tokenizer.encode_plus(
            text,
            truncation=True,
            padding=True,
            max_length=256,
            return_tensors='tf'
        )
        input_ids.append(tokenized['input_ids'])
        attention_mask.append(tokenized['attention_mask'])

    input_ids = np.array(input_ids)
    attention_mask = np.array(attention_mask)

    predictions = loaded_bert_model.predict([input_ids, attention_mask])
    predicted_labels = np.argmax(predictions, axis=1)
    
    return label_encoder.inverse_transform(predicted_labels)


class TextData(BaseModel):
    designation: str
    description: str
    productid: int
    imageid: int
    prdtypecode: int
    img_pd: str
    description_complete: str
    description_complete_languages: str
    description_complete_prétraite: str

class TextsInput(BaseModel):
    texts: List[TextData]

# Endpoint pour effectuer des prédictions
@app.post("/bert128/predict/")
async def predict(texts_input: TextsInput):
    try:
        texts = [item.description_complete_prétraite for item in texts_input.texts]
        predicted_labels = predict_with_model(texts)
        return {"predictions": predicted_labels.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
