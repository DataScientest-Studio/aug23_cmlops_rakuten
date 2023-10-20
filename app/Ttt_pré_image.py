from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

class ImagePreparation:
    
    def __init__(self, image_path=None):
        self.image_path = image_path
    
    def load_image(self, image_path=None):
        if image_path:
            return Image.open(image_path)
        return Image.open(self.image_path)

    def ensure_rgb(self, image):
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image

    def resize_image(self, image, target_size=(224, 224)):
        return image.resize(target_size)

    def to_numpy_array(self, image):
        return np.asarray(image) / 255.0

    def expand_dims(self, image_array):
        return np.expand_dims(image_array, axis=0)
    
    def prepare(self, image_path=None):
        image = self.load_image(image_path)
        image = self.ensure_rgb(image)
        image = self.resize_image(image)
        image_array = self.to_numpy_array(image)
        image_ready = self.expand_dims(image_array)
        return image_ready

    def batch_prepare(self, image_paths):
        images_ready = []
        for image_path in image_paths:
            image_ready = self.prepare(image_path)
            images_ready.append(image_ready)
        return np.concatenate(images_ready, axis=0)

class ModelPredictor:

    def __init__(self, model_path):
        self.model = load_model(model_path)

    def predict(self, images_ready):
        predictions = self.model.predict(images_ready)
        predicted_classes = np.argmax(predictions, axis=1)
        return predicted_classes

    def translate_prediction_to_thematique(self, predicted_classes, prdtypecode_list, thematique_list):
        code_to_thematique = dict(zip(prdtypecode_list, thematique_list))
        return [code_to_thematique[code] for code in predicted_classes]

# Utilisation pour la préparation d'images
image_path_single = "path_to_your_image.jpg"
image_preparation_single = ImagePreparation(image_path_single)
image_ready_single = image_preparation_single.prepare()

image_paths = ["path_to_image1.jpg", "path_to_image2.jpg", "path_to_image3.jpg"]
image_preparation_batch = ImagePreparation()
images_ready_batch = image_preparation_batch.batch_prepare(image_paths)

# Prédiction
model_path = "/path_to_your_model/resnet_model.h5"
predictor = ModelPredictor(model_path)

liste_prdtypecode = [10, 40, 50, 60, 1140, 1160, 1180, 1280, 1281, 1300, 1301, 1302, 1320, 1560, 1920, 1940, 2060, 2220, 2280, 2403, 2462, 2522, 2582, 2583, 2585, 2705, 2905]
liste_thématique = ['Livres_magazines','Jeux_vidéos','Jeux_vidéos','Jeux_vidéos', 'Collections', 'Collections', 'Collections', 'Jeux_enfants', 'Jeux_enfants', 'Jeux_vidéos', 'Jeux_enfants', 'Jeux_enfants', 'Jeux_enfants', 'Mobilier_intérieur', 'Mobilier_intérieur', 'Alimentation', 'Mobilier_intérieur', 'Animaux', 'Livres_magazines', 'Livres_magazines', 'Jeux_vidéos', 'Papeterie', 'Mobilier_extérieur', 'Mobilier_extérieur', 'Mobilier_extérieur', 'Livres_magazines', 'Jeux_vidéos']

predicted_class_single = predictor.predict(image_ready_single)
thematique_single = predictor.translate_prediction_to_thematique(predicted_class_single, liste_prdtypecode, liste_thématique)
print(f"Image {image_path_single} - Classe prédite : {predicted_class_single[0]} - Thématique : {thematique_single[0]}")

predicted_classes_batch = predictor.predict(images_ready_batch)
thematiques_batch = predictor.translate_prediction_to_thematique(predicted_classes_batch, liste_prdtypecode, liste_thématique)
for path, pred_class, thematique in zip(image_paths, predicted_classes_batch, thematiques_batch):
    print(f"Image {path} - Classe prédite : {pred_class} - Thématique : {thematique}")
