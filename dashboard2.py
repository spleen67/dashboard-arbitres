import streamlit as st
import pandas as pd
import unidecode

st.set_page_config(page_title="Disponibilités des arbitres", layout="wide")
st.title("📅 Tableau de bord des disponibilités des arbitres")

# 📥 Chargement des données depuis Google Sheets
@st.cache_data
def charger_disponibilites():
    url = "https://docs.google.com/spreadsheets/d/113KAFUl9E4ceFqm-gIfQ-zhigYGnOGPh/export?format=xlsx"
    df = pd.read_excel(url)
    df.columns = [unidecode.unidecode(col).upper() for col in df.columns]
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date
    df['DISPONIBILITE'] = df['DISPONIBILITE'].astype(str).str.strip().str.upper()
    df['DISPONIBILITE'] = df['DISPONIBILITE'].apply(lambda x: "✅" if x == "OUI" else "☑️")
    return df

@st.cache_data
def charger_arbitres():
    url = "https://docs.google.com/spreadsheets/d/1UUZBFPMCkVGzVKeTP_D44ZpGwTHlu0Q0/export?format=xlsx"
    df = pd.read_excel(url)
    df.columns = [unidecode.unidecode(col).upper() for col in df.columns]
    return df[['NUMERO AFFILIATION', 'CATEGORIE', 'CODE CLUB']]

# 📊 Chargement
df_dispo = charger_disponibilites()
df_arbitres = charger_arbitres()

# 🔗 Fusion des données
df = pd.merge(df_dispo, df_arbitres, left_on='NO LICENCE', right_on='NUMERO AFFILIATION', how='left')

# 🧱 Création du tableau pivoté
pivot = df.pivot_table(
    index=['NOM', 'PRENOM', 'CATEGORIE', 'CODE CLUB'],
    columns='DATE',
    values='DISPONIBILITE',
    aggfunc='first',
    fill_value='☑️'
)

# 📅 Formatage des dates en colonnes (format FR)
pivot.columns = [pd.to_datetime(date).strftime('%d/%m/%Y') for date in pivot.columns]
pivot.reset_index(inplace=True)

# 📋 Affichage
st.dataframe(pivot, use_container_width=True)
