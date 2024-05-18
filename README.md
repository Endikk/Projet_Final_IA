# Installation du Projet

Ce fichier README fournit des instructions sur la façon d'installer et de démarrer le projet.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :

- [Conda](https://www.anaconda.com/download/success) (Download Anaconda)

## Étapes d'Installation

1. **Créer un environnement virtuel :**  

    <span style="color:red; font-size:larger;">⚠️ Important ! Veuillez ouvrir le terminal Conda et exécuter les commandes ci-dessous : ⚠️</span>  

    ```bash
    conda create --name IA_Projet python=3.11 -y
    conda activate IA_Projet
    ```

2. **Cloner le projet depuis le dépôt Git :**
    ```bash 
    # Étape 1 :
    cd CheminDuProjetSouhaitez

    # Exemple : 
    cd C:\Users\labonde\Documents\Cours_CESI\

    # Étape 2 :
    git clone https://github.com/Endikk/Vehicule_Recognition_ProjetIA.git

    # Étape 3 :
    cd Vehicule_Recognition_ProjetIA
    ```

3. **Installer les dépendances Python :**

    ```bash
    # Étape 4 : Via le terminal du projet
    pip install -r requirements.txt
    ```

4. **Ouvrir directement vers la direction du code :**

    ```bash
    # Étape 5 : Pour ouvrir le projet
    code .
    ```

5. **Créer un fichier `.env` :**

    Créez un fichier `.env` à la racine du projet et ajoutez les variables d'environnement nécessaires. Vous avez pour exemple le fichier .env_exemple.

    ```plaintext
    TOKEN=votre_token
    IMAGE_URL=url_de_l'image
    ```
    Remplacez `votre_token` par votre token de Label Studio et `url_de_l'image` par l'URL de l'image.

6. **Exporter votre `.json` :**

    Exportez votre fichier JSON depuis votre Label Studio et placez-le à la racine du projet (vous pouvez le renommer comme vous le souhaitez).

    Si vous pensez avoir oublié un fichier, vérifiez la structure du projet dans le technical_review.

## Utilisation

Une fois l'installation terminée, vous pouvez utiliser le script Python pour effectuer différentes opérations. Voici les utilisations possibles :

- **Extraire les images de l'URL :**

    ```bash
    # Extraction automatique de 50 images par seconde.
    python main.py extract
    
    # Vous pouvez spécifier le nombre d'images par seconde que vous souhaitez.
    python main.py extract 80
    ```

    Cela extraira les images de l'URL spécifiée et les sauvegardera dans le répertoire `images`.

- **Télécharger les annotations depuis un fichier JSON :**

    ```bash
    # Vous devez mettre le nom de votre fichier JSON
    python main.py annotations chemin_vers_le_fichier_json

    # Exemple de votre fichier JSON 
    python .\main.py annotations .\export_67163_project-67163-at-2024-05-17-11-52-bb58ed83.json
    ```

    Cela téléchargera les annotations à partir du fichier JSON spécifié et les sauvegardera dans le répertoire `images_labels`.

## Remarque

- Assurez-vous d'avoir configuré les variables d'environnement nécessaires dans le fichier `.env` avant d'exécuter le script.

- Si vous avez ajouté des importations dans votre code, vous pouvez régénérer le requirements.
    ```bash
    Génere le fichier requirements.txt 

    pip freeze > requirements.txt 
    ```
    
- Ne vous inquiétez pas, les dossiers contenant les images se créent automatiquement.
---
