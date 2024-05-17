# Importation des modules système
import os
import sys
from time import sleep
from datetime import datetime
import json
from os.path import join, realpath, dirname, exists

# Importation des modules tiers
from dotenv import load_dotenv
from PIL import Image
import imagehash
import requests

# Variables d'environnement qui prendront les valeurs du fichier .env à la racine du projet
load_dotenv()
TOKEN = os.getenv("TOKEN")
IMAGE_URL = os.getenv("IMAGE_URL")
BASE_URL = "https://app.heartex.com/storage-data/uploaded/?filepath="

# Paths
PROJECT_PATH = dirname(realpath(__file__))
IMAGES_DIR = join(PROJECT_PATH, 'images')
IMAGES_LABELS_DIR = join(PROJECT_PATH, 'images_labels')

# Fonctions utilitaires pour les téléchargements d'images
def download_image(url, destination, headers=None):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200: # Vérifie si la requête a abouti
            with open(destination, 'wb') as f:
                f.write(response.content)
            print(f"\nL'image {os.path.basename(destination)} a été téléchargée avec succès.")
            return True
        else:
            print(url)
            print(f"Échec du téléchargement de l'image {destination}. {response.status_code} {response.reason}")
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement de l'image {destination}. Détails: {e}")
    return False

# Fonctions utilitaires pour la comparaison d'images
def is_identical(image1, image2):
    try:
        hash1 = imagehash.average_hash(Image.open(image1)) # Calcul du hash de l'image 1 (image précédente)
        hash2 = imagehash.average_hash(Image.open(image2)) # Calcul du hash de l'image 2 (image actuelle)
        if (hash1 - hash2) == 0:
            return True
    except Exception:
        pass
    return False

# Fonctions utilitaires pour la suppression d'images si elles sont identiques
def remove_image(filename):
    if exists(filename): # Vérifie si le fichier existe
        os.remove(filename) 

# Fonction principale pour extraire les images à partir d'une URL
def extract_image(loop=50, wait=60): # Extrait 50 images par défaut avec un intervalle de 60 secondes
    images = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
    last = join(IMAGES_DIR, images[-1]) if images else None
    for i in range(loop):
        if i > 0: 
            try:
                sleep(wait) 
            except KeyboardInterrupt:
                break
        # Permet de renommer les images avec un timestamp en format YmdHMS
        filename = join(IMAGES_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        download_image(IMAGE_URL, filename)
        if is_identical(last, filename):
            print(f'Image {os.path.basename(filename)} identique à la précédente. Suppression...')
            remove_image(filename)
        last = filename # Affectation de la dernière image téléchargée

# Fonction principale pour traiter le fichier JSON et télécharger les images
def process_json(json_file):
    if not exists(json_file):
        print("Fichier JSON introuvable.")
        return

    with open(json_file, 'r') as file:
        data = json.load(file)
    
    failed_downloads = [] # Liste des images qui n'ont pas été téléchargées
    for item in data:
        try:
            image_url = f"{BASE_URL}{item['data']['image']}" # URL de l'image complète
            filename = item['file_upload']
        except:
            print('Erreur lors de la récupération des données. JSON Malformé.')
        
        if not exists(join(IMAGES_LABELS_DIR, filename)):
            if not download_image(image_url, join(IMAGES_LABELS_DIR, filename), headers={"Authorization": f"Token {TOKEN}"}):
                failed_downloads.append(filename)

    if failed_downloads:
        print(f"\nÉchec du téléchargement de certaines images. {len(data)-len(failed_downloads)}/{len(data)}")
        print(failed_downloads) # Le nom des images qui n'ont pas été téléchargées
    else:
        print("\nToutes les images ont été téléchargées avec succès.")

# Fonction principale pour lancer le script
def main():
    args = sys.argv[1:]
    if args:
        # Cette partie du script permet de télécharger les images à partir d'une URL
        if args[0] == 'extract':
            
            if not exists(IMAGES_DIR):
                os.makedirs(IMAGES_DIR)
            
            try:
                extract_image(loop=int(args[1]))
            except:
                print("Valeur incorrecte pour le nombre de boucles. Utilisation de la valeur par défaut (50 boucles).")
                extract_image(loop=50, wait=60)

        # Cette partie du script permet de télécharger les images à partir d'un fichier JSON
        elif args[0] == 'annotations':

            if not exists(IMAGES_LABELS_DIR):
                os.makedirs(IMAGES_LABELS_DIR)

            if len(args) >= 2:
                process_json(args[1])
            else:
                print("Veuillez fournir le chemin vers l'export JSON.")    

# Point d'entrée du script
if __name__ == "__main__":
    main()