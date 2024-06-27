#import locale
import os
from os.path import join, realpath, dirname, exists
import random

#import externe
from PIL import Image
import cv2
import numpy as np
import torch
import hashlib
import pandas as pd
import torch # YoloV5 import
from ultralytics import YOLO  # YOLOv8 import

# Importer les classes des modèles
CUSTOM_CATEGORIES = {
    0: 5,
    1: 0,
    2: 2,
    3: 4,
    5: 1,
    7: 7,
}

class BasicModel:
    def __init__(self):
        # Charger le modèle YOLOv5 pré-entraîné
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

    def get_unique_color(self, label):
        # Générer une couleur unique pour chaque catégorie
        random.seed(hash(label))  # Assurer la même couleur pour la même étiquette
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def detect_and_draw_image(self, image_path, output_path):
        # Charger l'image
        image = Image.open(image_path)
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Effectuer la détection
        results = self.model(image)
        results_data = results.pandas().xyxy[0]  # Bounding boxes

        # Dessiner les bounding boxes
        for index, row in results_data.iterrows():
            color = self.get_unique_color(row['name'])  # Obtenir la couleur pour la catégorie
            confidence_score = row['confidence']
            label = f"{row['name']} {confidence_score:.2f}"
            cv2.rectangle(image_cv, (int(row['xmin']), int(row['ymin'])), (int(row['xmax']), int(row['ymax'])), color, 2)
            cv2.putText(image_cv, label, (int(row['xmin']), int(row['ymin'])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Sauvegarder l'image avec les bounding boxes
        cv2.imwrite(output_path, image_cv)

        # calculate precision, recall, F1 score, IoU, Map, Ap
        precision = results_data[results_data['confidence'] > 0.5]['name'].value_counts().get('car', 0) / results_data['name'].value_counts().get('car', 1)
        recall = results_data[results_data['name'] == 'car']['confidence'].apply(lambda x: x > 0.5).sum() / results_data['name'].value_counts().get('car', 1)
        f1_score = 2 * (precision * recall) / (precision + recall)
        print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1 Score: {f1_score:.2f}")

        # calculate le nombre de labels car sur l'image
        print(f"Number of cars detected: {results_data['name'].value_counts().get('car', 0)}")
        print(f"Number of labels: {results_data.shape[0]}")

# Base class for YOLO models
class BaseModel:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
    
    def validation(self):
        return self.model(data="C:/Users/labon/Documents/Cours CESI/Projet_Final_IA_DEV/src/coco.yaml", imgsz=640, batch=2, conf=0.25, iou=0.5, device='cpu')
        
    def get_unique_color(self, label):
        random.seed(int(hashlib.md5(label.encode()).hexdigest(), 16))
        return [random.randint(0, 255) for _ in range(3)]

    def detect_and_draw_on_image(self, image, save_path):
        results = self.model.predict(image, classes=[0, 1, 2, 3, 5, 7], conf=0.2, iou=0.8, imgsz=640)
        df = pd.DataFrame(results[0].boxes.data.cpu().numpy(), columns=["xmin", "ymin", "xmax", "ymax", "confidence", "class"])
        df["label"] = df["class"].apply(lambda x: results[0].names[int(x)])
        
        for index, row in df.iterrows():
            color = self.get_unique_color(row["label"])
            cv2.rectangle(image, (int(row["xmin"]), int(row["ymin"])), (int(row["xmax"]), int(row["ymax"])), color, 2)
            label = f"{row['label']} {row['confidence']:.2f}"
            cv2.putText(image, label, (int(row["xmin"]), int(row["ymin"] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        cv2.imwrite(save_path, image)

    def detect_image(self, image_path):
        return self.model.predict(image_path, classes=[0, 1, 2, 3, 5, 7 ], conf=0.2, iou=.8, imgsz=640)
     
    def convert_to_coco(self, results, img_id):
        coco_results = []
        for result in results:
            for box in result.boxes:
                bbox = box.xyxy[0].tolist()              
                coco_results.append({
                    "image_id": img_id,
                    "category_id": CUSTOM_CATEGORIES[int(box.cls)],
                    "bbox": [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]],
                    "score": float(box.conf)
                })
        return coco_results
    
    def calculate_metrics(self, df, category="car", confidence_threshold=0.5):
        relevant_predictions = df[(df["label"] == category) & (df["confidence"] > confidence_threshold)]
        true_positives = len(relevant_predictions)
        total_predicted_positives = len(df[df["label"] == category])
        precision = true_positives / total_predicted_positives if total_predicted_positives > 0 else 0
        recall = true_positives / len(relevant_predictions) if len(relevant_predictions) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        return precision, recall, f1_score

# Specific model classes
class SmallModel(BaseModel):
    def __init__(self):
        super().__init__(join(dirname(realpath(__file__)), 'models', 'yolov9t.pt'))

class MediumModel(BaseModel):
    def __init__(self):
        super().__init__(join(dirname(realpath(__file__)), 'models', 'yolov9m.pt'))

class LargeModel(BaseModel):
    def __init__(self):
        super().__init__(join(dirname(realpath(__file__)), 'models', 'yolov5x6u.pt'))
