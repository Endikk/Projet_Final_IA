# Revue technique du projet

## Aperçu
Ce projet vise à créer un système de surveillance du trafic en utilisant des modèles de détection d'objets YOLO (You Only Look Once). Le système télécharge des images à partir d'une URL spécifiée, traite ces images pour détecter les véhicules, et affiche les résultats dans un tableau de bord convivial à l'aide de Streamlit.

## Structure du projet
### main.py
**Description :**

Objectif : Le script principal orchestre le téléchargement des images, l'application d'un masque, la détection des véhicules et l'enregistrement des résultats.
Principales bibliothèques utilisées : requests, PIL, imagehash, numpy, cv2, torch, datetime.

**Principaux composants :**

- Constantes et configuration de l'environnement :
    - PROJECT_PATH, IMAGES_DIR, RESULTS_FILE, MASK_PATH définissent les chemins utilisés dans le script.
    - IMAGE_URL est récupérée à partir des variables d'environnement.

- Fonctions d'aide :
    - download_image(url, destination, headers=None) : Télécharge une image à partir de l'URL fournie.
    - is_identical(image1, image2) : Vérifie si deux images sont identiques en utilisant le hachage moyen.
    - remove_image(filename) : Supprime le fichier image spécifié.

- Fonction de traitement principale :
    - extract_and_identify_vehicles(loop=50, wait=60) : Gère la logique principale du téléchargement des images, de la vérification des doublons, de l'application des masques, de la détection des véhicules à l'aide d'un modèle, et de l'enregistrement des résultats.

- Point d'entrée :
    - Exécute la fonction extract_and_identify_vehicles si le script est exécuté directement.

### model.py
**Description :**

Objectif : Contient des classes pour différents modèles YOLO et des méthodes de détection d'objets et de traitement d'images.
Principales bibliothèques utilisées : PIL, cv2, torch, ultralytics, hashlib, pandas.

**Principaux composants :**

- Classe BaseModel :
    - Initialise le modèle YOLO.
    - Fournit des méthodes pour détecter des objets dans des images, dessiner des boîtes englobantes et convertir les résultats de détection au format COCO.
    - Comprend des fonctions utilitaires pour générer des couleurs uniques pour les boîtes englobantes et calculer des métriques telles que la précision, le rappel et le score F1.

- Variantes du modèle :
    - SmallModel, MediumModel, LargeModel : Sous-classes de BaseModel qui initialisent des versions spécifiques du modèle YOLO.

### interface.py
**Description :**

Objectif : Implémente un tableau de bord Streamlit pour visualiser et interagir avec les résultats de détection des véhicules.
Principales bibliothèques utilisées : streamlit, pandas, plotly, PIL, streamlit_autorefresh.

**Principaux composants :**

- Fonctions d'aide :
    - clean_date(date_str) : Convertit une chaîne de caractères en objet datetime.
    - load_data() : Charge et prépare les données pour l'analyse.
    - load_vehicle_results() : Charge les résultats des véhicules détectés.

- Pages du tableau de bord :
    - home() : Affiche la page d'accueil avec une introduction et les principales fonctionnalités.
    - label_image(df) : Permet d'analyser les catégories d'images avec des filtres et des graphiques interactifs.
    - camera_directe() : Permet de visualiser des flux de caméra en direct et les résultats de détection des véhicules.

- Configuration de la page :
    - Utilise st.set_page_config pour configurer le titre, l'icône et la mise en page de la page.
    - Charge les données avec load_data().
    - Crée une barre de navigation avec option_menu.

- Logique de navigation :
    - Affiche différentes pages en fonction de la sélection dans la barre de navigation.

**Extraits de code clés :**

- Téléchargement d'images :
```python
def download_image(url, destination, headers=None):
        try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                        with open(destination, 'wb') as f:
                                f.write(response.content)
                        print(f"Téléchargement réussi de l'image {os.path.basename(destination)}.")
                        return True
                else:
                        print(f"Échec du téléchargement de l'image {destination}. {response.status_code} {response.reason}")
        except requests.RequestException as e:
                print(f"Erreur lors du téléchargement de l'image {destination}. Détails : {e}")
        return False
```

- Détection d'objets et dessin de boîtes englobantes :
```python
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
```

- Chargement et préparation des données :
```python
def load_data():
        try:
                with open('class_counts.json', 'r') as f:
                        data = json.load(f)
                records = []
                for key, value in data.items():
                        if key != "Total":
                                record = {"Nom": value["Nom"], "Filename": key}
                                record.update(value["Categorie"])
                                records.append(record)
                df = pd.DataFrame(records)
                df['Date'] = df['Nom'].apply(clean_date)
                df = df.dropna(subset=['Date'])
                return df
        except (json.JSONDecodeError, KeyError) as e:
                st.error("Error loading data. The service is under maintenance. Please try again later.")
                return pd.DataFrame()  # Returns an empty DataFrame
        except FileNotFoundError:
                st.error("File 'class_counts.json' not found. Please check the file path.")
                return pd.DataFrame()  # Returns an empty DataFrame
```

## Conclusion
This project is well-structured and utilizes modern libraries for image processing and machine learning. The main functionalities are well-defined, ranging from image downloading to vehicle detection and displaying the results in an intuitive user interface. The key code snippets and utility functions effectively handle complex tasks of object detection and image manipulation.
