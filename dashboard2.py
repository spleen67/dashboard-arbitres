import streamlit as st
import pandas as pd

# Chargement du fichier
st.set_page_config(page_title="Disponibilités des arbitres", layout="wide")

# Titre
st.title("📅 Tableau de bord des disponibilités des arbitres")

# Chargement des données
@st.cache_data
def charger_donnees_depuis_url():
    url = "https://docs.google.com/spreadsheets/d/113KAFUl9E4ceFqm-gIfQ-zhigYGnOGPh/export?format=xlsx"
    df = pd.read_excel(url)
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df

df = charger_donnees_depuis_url()


# Nettoyage des colonnes
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['DISPONIBILITE'] = df['DISPONIBILITE'].str.upper().str.strip()

# Transformation : pivot table
df['DISPONIBILITE'] = df['DISPONIBILITE'].apply(lambda x: "OUI" if x == "DISPONIBLE" else "NON")

# Création du tableau pivoté
pivot = df.pivot_table(
    index=['Nom', 'PRENOM'],
    columns='Date',
    values='DISPONIBILITE',
    aggfunc='first',
    fill_value='NON'
)

# Remise en forme
pivot.reset_index(inplace=True)
pivot.columns.name = None  # Supprime le nom de l'index des colonnes

# Affichage Streamlit
st.title("Disponibilité par personne et par jour")
st.dataframe(pivot)
