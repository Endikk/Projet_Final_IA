#import locale
import os
import json
import requests

#import externe
from time import sleep
from datetime import datetime
from os.path import join, realpath, dirname, exists
from PIL import Image
import imagehash
import numpy as np
import cv2
import torch
import sys

# Ajouter le chemin 'src' à sys.path
sys.path.append(join(dirname(realpath(__file__)), 'src'))

from model import LargeModel  # Importer le modèle choisi (LargeModel)

# Chemins
PROJECT_PATH = dirname(realpath(__file__))
IMAGES_DIR = join(PROJECT_PATH, 'images')
RESULTS_FILE = join(PROJECT_PATH, 'vehicle_results.json')
MASK_PATH = join(PROJECT_PATH, 'src','models','ref_image.png')  # Chemin du fichier masque

# Charger les variables d'environnement
IMAGE_URL = os.getenv("IMAGE_URL")

# Fonction pour télécharger une image
def download_image(url, destination, headers=None):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                f.write(response.content)
            print(f"L'image {os.path.basename(destination)} a été téléchargée avec succès.")
            return True
        else:
            print(f"Échec du téléchargement de l'image {destination}. {response.status_code} {response.reason}")
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement de l'image {destination}. Détails: {e}")
    return False

# Fonction pour vérifier si deux images sont identiques
def is_identical(image1, image2):
    try:
        hash1 = imagehash.average_hash(Image.open(image1))
        hash2 = imagehash.average_hash(Image.open(image2))
        if (hash1 - hash2) == 0:
            return True
    except Exception:
        pass
    return False

# Fonction pour supprimer une image
def remove_image(filename):
    if exists(filename):
        os.remove(filename)

# Fonction principale pour extraire et traiter les images
def extract_and_identify_vehicles(loop=50, wait=60):
    if not exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    images = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    last = join(IMAGES_DIR, images[-1]) if images else None

    model = LargeModel()  # Initialiser le modèle choisi

    # Charger le masque
    mask = cv2.imread(MASK_PATH, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"Le masque {MASK_PATH} n'a pas été trouvé.")

    vehicle_results = []

    for i in range(loop):
        if i > 0:
            sleep(wait)

        filename = join(IMAGES_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        if download_image(IMAGE_URL, filename):
            if is_identical(last, filename):
                print(f'Image {os.path.basename(filename)} identique à la précédente. Suppression...')
                remove_image(filename)
                continue

            last = filename

            # Charger l'image
            image = cv2.imread(filename)
            if image is None:
                print(f"Impossible de charger l'image {filename}")
                continue

            # Redimensionner le masque pour qu'il corresponde à la taille de l'image
            mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))

            # Appliquer le masque sur l'image
            masked_image = cv2.bitwise_and(image, image, mask=mask_resized)

            # Détecter les véhicules dans l'image
            preds = model.detect_image(masked_image)

            # Dessiner les bounding boxes sur l'image
            model.detect_and_draw_on_image(masked_image, filename)

            # Vérifier si des objets ont été détectés
            if preds[0].boxes.shape[0] == 0:
                image_class_counts = {"nothing": 0}
            else:
                class_counts = torch.bincount(preds[0].boxes.cls.long(), minlength=8)
                d = {0: 'Bicycle', 1: 'Bus', 2: 'Car', 3: 'Motor scooter', 4: 'Motorbike', 5: 'Pedestrian', 6: 'Scooter', 7: 'Truck'}
                CUSTOM_CATEGORIES = {0: 5, 1: 0, 2: 2, 3: 4, 5: 1, 7: 7}
                image_class_counts = {d[CUSTOM_CATEGORIES[index]]: count for index, count in enumerate(class_counts.tolist()) if count > 0}

            result = {
                "image": os.path.basename(filename),  # Utiliser uniquement le nom de l'image
                "categories": image_class_counts
            }

            vehicle_results.append(result)

            # Afficher les résultats immédiatement après traitement de chaque image
            print(json.dumps(result, indent=4))

            # Écrire les résultats dans le fichier JSON après chaque image traitée
            with open(RESULTS_FILE, 'w') as f:
                json.dump(vehicle_results, f, indent=4)

    print(f"Toutes les images ont été traitées et les résultats sont enregistrés dans {RESULTS_FILE}.")

# Point d'entrée du script
if __name__ == "__main__":
    extract_and_identify_vehicles(loop=50, wait=60)
