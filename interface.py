#import locale
import os
import json

# import externe
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# Fonction pour nettoyer et normaliser les dates
def clean_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y%m%d%H%M%S')
    except ValueError:
        return None

# Fonction pour charger et préparer les données
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
        st.error("Erreur de chargement des données. Le service est en maintenance. Veuillez réessayer plus tard.")
        return pd.DataFrame()  # Retourne un DataFrame vide
    except FileNotFoundError:
        st.error("Fichier 'class_counts.json' non trouvé. Veuillez vérifier le chemin du fichier.")
        return pd.DataFrame()  # Retourne un DataFrame vide

# Fonction pour charger les résultats des véhicules
def load_vehicle_results():
    try:
        with open('vehicle_results.json', 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError) as e:
        st.error("Erreur de chargement des résultats des véhicules. Le service est en maintenance. Veuillez réessayer plus tard.")
        return []
    except FileNotFoundError:
        st.error("Fichier 'vehicle_results.json' non trouvé. Veuillez vérifier le chemin du fichier.")
        return []

# Fonction pour afficher l'image dans un pop-up
def display_image(image_path):
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption=os.path.basename(image_path))
    else:
        st.write("Image not found.")

# Page d'accueil
def accueil():
    st.title("Bienvenue sur le Tableau de Bord - Grand Lyon")
    
    st.image("src/models/trafic_IA.png", use_column_width=True)
    
    st.markdown("""
    <style>
    .big-font {
        font-size:40px !important;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-font {
        font-size:20px !important;
        text-align: center;
        margin-bottom: 30px;
    }
    .highlight {
        font-weight: bold;
        color: #FF5733;
    }
    .stButton>button {
        font-size: 18px;
        background-color: #FF5733;
        color: white;
        border: None;
        padding: 10px 20px;
        border-radius: 5px;
        margin-top: 20px;
    }
    .stButton>button:hover {
        background-color: #FF4500;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">Bienvenue dans le système de suivi et d’analyse des données de trafic du Grand Lyon</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-font">Explorez les différentes catégories d\'images, suivez les flux en direct des caméras et plus encore.</p>', unsafe_allow_html=True)

    st.markdown("""
    ## Fonctionnalités principales :
    - <span class="highlight">Analyse des catégories d'images :</span> Filtrez et explorez les données selon différentes catégories et plages de dates.
    - <span class="highlight">Caméra Directe :</span> Visualisez les flux en direct des caméras situées à divers points stratégiques.
    """, unsafe_allow_html=True)

    st.markdown("""
    ## Pourquoi utiliser ce tableau de bord ?
    - **Optimisation du trafic** : Prenez des décisions éclairées pour améliorer la circulation.
    - **Sécurité accrue** : Suivez les incidents en temps réel pour une intervention rapide.
    - **Analyse approfondie** : Accédez à des données historiques pour des analyses détaillées.
    """)

    st.button('Commencez ici !')

# Page d'analyse des catégories d'images
def label_image(df):
    if df.empty:
        st.write("Données indisponibles pour l'analyse des catégories d'images.")
        return
    
    st.title("Analyse des Catégories d'Images")
    st.markdown("""
    Bienvenue dans l'application d'analyse des catégories d'images. Utilisez les filtres sur le côté gauche pour explorer les données selon vos critères.
    - **Catégorie** : Sélectionnez les catégories à afficher.
    - **Plage de dates** : Choisissez une plage de dates pour filtrer les résultats.
    - **Filtrer par nombre d’images** : Affichez les catégories avec un nombre minimum d'images.
    """)

    # Ajouter une barre de recherche en haut du tableau
    search_term = st.text_input('Recherche par nom d\'image', '')

    if search_term:
        # Rechercher le nom de fichier correspondant
        matching_row = df[df['Nom'] == search_term]
        if not matching_row.empty:
            filename = matching_row.iloc[0]['Filename']
            image_path = f"src/output_images/{filename}"
            display_image(image_path)
        else:
            st.write("Aucune image trouvée pour ce nom.")
    
    # Créer les filtres
    st.sidebar.header("Filtres")
    categories = df.columns[2:-1].tolist()  # Exclure 'Nom', 'Filename' et 'Date'
    categorie_filter = st.sidebar.multiselect('Catégorie', categories, categories)
    date_range = st.sidebar.date_input('Plage de dates', [])
    image_filter = st.sidebar.selectbox('Filtrer par nombre d’images', ['Toutes', '>= 1', '>= 5', '>= 10'])

    # Appliquer les filtres
    filtered_df = df.copy()
    if categorie_filter:
        filtered_df = filtered_df[['Nom', 'Date'] + categorie_filter]

    if date_range:
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Convertir les dates en objets datetime
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())
            filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]

    if image_filter != 'Toutes':
        min_images = int(image_filter.split('>= ')[1])
        filtered_df['Total'] = filtered_df[categorie_filter].sum(axis=1)
        filtered_df = filtered_df[filtered_df['Total'] >= min_images]

    # Calculer le total pour chaque date
    if not filtered_df.empty and categorie_filter:
        filtered_df['Total'] = filtered_df[categorie_filter].sum(axis=1)
        date_totals = filtered_df.groupby('Date')['Total'].sum().reset_index()

        # Afficher les données filtrées
        st.subheader("Données Filtrées")
        st.dataframe(filtered_df)

        # Créer un graphique interactif basé sur les données filtrées
        st.subheader('Graphique des catégories filtrées')
        fig = px.line(date_totals, x='Date', y='Total', title='Nombre de voitures par date', markers=True)
        fig.update_layout(xaxis_title='Date', yaxis_title='Nombre de voitures')
        st.plotly_chart(fig)
    else:
        st.write("Aucune donnée ne correspond aux filtres sélectionnés.")

    if not filtered_df.empty and categorie_filter:
        st.subheader('Distribution des Catégories')
        category_totals = filtered_df[categorie_filter].sum().reset_index()
        category_totals.columns = ['Catégorie', 'Total']
        fig_bar = px.bar(category_totals, x='Catégorie', y='Total', title='Distribution des Catégories')
        fig_bar.update_layout(xaxis_title='Catégorie', yaxis_title='Nombre d\'images')
        st.plotly_chart(fig_bar)

# Page caméra directe
def camera_directe():
    st.title("Caméra Directe")
    st.write("Visualisez les flux en direct des caméras.")
    
    # Rafraîchir la page toutes les 5 secondes
    st_autorefresh(interval=5000, key="datarefresh")
    
    vehicle_results = load_vehicle_results()
    last_image = vehicle_results[-1] if vehicle_results else None

    if last_image:
        image_path = os.path.join('images', last_image["image"])
        display_image(image_path)

        st.json(last_image["categories"])
    else:
        st.write("Aucune image disponible pour l'instant.")
    
    # Ajouter une barre de recherche en haut du tableau
    search_term = st.text_input('Recherche par nom d\'image', '')

    if search_term: