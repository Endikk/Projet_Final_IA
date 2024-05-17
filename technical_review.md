## Description du Projet et Technique

### Explication de ce Projet

Ce projet a été conçu dans le cadre de notre Bachelor en Intelligence Artificielle. L'objectif est de récupérer des images à partir d'une caméra de la Métropole de Lyon accessible via une URL.  
Notre script télécharge ces images toutes les 60 secondes. Ensuite, nous avons utilisé LABEL STUDIO pour annoter les images avec les labels suivants : Car, Pedestrian, Truck, Scooter, Motorbike, Bus, Bicycle, et Motor Scooter. Une fois les annotations terminées, les images annotées sont exportées au format JSON. Une autre partie de notre script peut alors récupérer ces images annotées pour les traiter ultérieurement.

### Structure du Projet

- **`.env`** : Contient les variables d'environnement.
- **`main.py`** : Contient les fonctions pour télécharger, comparer et gérer les images.
- **`requirements.txt`** : Contient les importations des modules systèmes et tiers.
- **Répertoires** :
  - `images` : Stocke les images téléchargées.
  - `images_labels` : Stocke les images annotées.

### Détails Techniques

1. **Importation des Modules**

    ```python
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
    ```

2. **Chargement des Variables d'Environnement**

    ```python
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    IMAGE_URL = os.getenv("IMAGE_URL")
    BASE_URL = "https://app.heartex.com/storage-data/uploaded/?filepath="
    ```

3. **Définition des Chemins**

    ```python
    PROJECT_PATH = dirname(realpath(__file__))
    IMAGES_DIR = join(PROJECT_PATH, 'images')
    IMAGES_LABELS_DIR = join(PROJECT_PATH, 'images_labels')
    ```

4. **Fonctions Utilitaires**

    - **Téléchargement d'Images**

        ```python
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
        ```

    - **Comparaison d'Images**

        ```python
        def is_identical(image1, image2):
            try:
                hash1 = imagehash.average_hash(Image.open(image1)) # Calcul du hash de l'image 1 (image précédente)
                hash2 = imagehash.average_hash(Image.open(image2)) # Calcul du hash de l'image 2 (image actuelle)
                if (hash1 - hash2) == 0:
                    return True
            except Exception:
                pass
            return False
        ```

    - **Suppression d'Images**

        ```python
        def remove_image(filename):
            if exists(filename): # Vérifie si le fichier existe
                os.remove(filename)
        ```

5. **Fonction Principale pour Extraire des Images**

    ```python
    def extract_image(loop=50, wait=60): # Extrait 50 images par défaut avec un intervalle de 60 secondes
        images = sorted([f for f in os.listdir(IMAGES_DIR) if f.endswith('.jpg')])
        last = join(IMAGES_DIR, images[-1]) if images else None
        for i in range(loop):
            if i > 0:
                sleep(wait)
            # Permet de renommer les images avec un timestamp en format YmdHMS
            filename = join(IMAGES_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            download_image(IMAGE_URL, filename)
            if is_identical(last, filename):
                print(f'Image {os.path.basename(filename)} identique à la précédente. Suppression...')
                remove_image(filename)
            last = filename
    ```

6. **Fonction Principale pour Traiter le Fichier JSON**

    ```python
    def process_json(json_file):
        if not exists(json_file):
            print("Fichier JSON introuvable.")
            return

        with open(json_file, 'r') as file:
            data = json.load(file)
        
        failed_downloads = [] # Liste des images qui n'ont pas été téléchargées
        for item in data:
            try:
                image_url = f"{BASE_URL}{item['data']['image']}"
                filename = item['file_upload']
            except:
                print('Erreur lors de la récupération des données. JSON Malformé.')
            
            if not exists(join(IMAGES_LABELS_DIR, filename)):
                if not download_image(image_url, join(IMAGES_LABELS_DIR, filename), headers={"Authorization": f"Token {TOKEN}"}):
                    failed_downloads.append(filename)

        if failed_downloads:
            print(f"\nÉchec du téléchargement de certaines images. {len(data)-len(failed_downloads)}/{len(data)}")
            print(failed_downloads)
        else:
            print("\nToutes les images ont été téléchargées avec succès.")
    ```

7. **Point d'Entrée du Script**

    ```python
    if __name__ == "__main__":
        main()
    ```
