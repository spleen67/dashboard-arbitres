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
df.columns = df.columns.str.strip().str.upper()
df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date

# Normalisation des valeurs de DISPONIBILITE
df['DISPONIBILITE'] = df['DISPONIBILITE'].astype(str).str.strip().str.upper()

# Pivot du tableau
pivot = df.pivot_table(index=['NOM', 'PRENOM'], columns='DATE', values='DISPONIBILITE', aggfunc='first', fill_value='NON')

# Formatage des dates en colonnes (format FR)
pivot.columns = [pd.to_datetime(date).strftime('%d/%m/%Y') for date in pivot.columns]
pivot.reset_index(inplace=True)

# Affichage Streamlit
st.title("Disponibilité des arbitres par jour")
st.dataframe(pivot)

