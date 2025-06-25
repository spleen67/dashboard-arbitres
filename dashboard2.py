import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="Disponibilités des arbitres", layout="wide")
st.title("Tableau de bord des disponibilités des arbitres")

# Fonction de nettoyage des noms de colonnes
def nettoyer_colonnes(df):
    df.columns = [
        unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8').strip().upper()
        for col in df.columns
    ]
    return df

# Chargement des données depuis Google Sheets
@st.cache_data
def charger_disponibilites():
    url = "https://docs.google.com/spreadsheets/d/113KAFUl9E4ceFqm-gIfQ-zhigYGnOGPh/export?format=xlsx"
    df = pd.read_excel(url)
    df = nettoyer_colonnes(df)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date
    df['DISPONIBILITE'] = df['DISPONIBILITE'].astype(str).str.strip().str.upper()
    df['DISPONIBILITE'] = df['DISPONIBILITE'].apply(lambda x: "✅" if x == "OUI" else "☑️")
    return df

@st.cache_data
def charger_arbitres():
    url = "https://docs.google.com/spreadsheets/d/1UUZBFPMCkVGzVKeTP_D44ZpGwTHlu0Q0/export?format=xlsx"
    df = pd.read_excel(url)
    df = nettoyer_colonnes(df)
    return df[['NUMERO AFFILIATION', 'CATEGORIE', 'CODE CLUB']]

# Chargement des données
df_dispo = charger_disponibilites()
df_arbitres = charger_arbitres()

# Fusion des données
if 'NO LICENCE' in df_dispo.columns:
    df = pd.merge(df_dispo, df_arbitres, left_on='NO LICENCE', right_on='NUMERO AFFILIATION', how='left')
else:
    st.error("La colonne 'NO LICENCE' est introuvable dans le fichier de disponibilités.")
    st.stop()

# Vérification des colonnes nécessaires
colonnes_requises = ['NOM', 'PRENOM', 'CATEGORIE_y', 'CODE CLUB', 'DATE', 'DISPONIBILITE']
colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]

if colonnes_manquantes:
    st.error(f"Colonnes manquantes pour le tableau : {', '.join(colonnes_manquantes)}")
    st.write("Colonnes disponibles :", df.columns.tolist())
    st.stop()

# Création du tableau pivoté
pivot = df.pivot_table(
    index=['NOM', 'PRENOM', 'CATEGORIE_y', 'CODE CLUB'],
    columns='DATE',
    values='DISPONIBILITE',
    aggfunc='first',
    fill_value='☑️'
)

# Formatage des dates en colonnes (format FR)
pivot.columns = [pd.to_datetime(date).strftime('%d/%m/%Y') for date in pivot.columns]
pivot.reset_index(inplace=True)

# Affichage du tableau
st.dataframe(pivot, use_container_width=True)
