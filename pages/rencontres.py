import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="Affectation des arbitres", layout="wide")
st.title("Affectation automatique des arbitres aux rencontres")

# Fonction de nettoyage des colonnes
def nettoyer_colonnes(df):
    df.columns = [
        unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8').strip().upper()
        for col in df.columns
    ]
    return df

# Table CATEGORIE → NIVEAU
categorie_niveau = {
    "INTERNATIONAUX": 1,
    "2EME DIVISION PRO": 2,
    "NATIONALE 1 ET 2": 3,
    "ARBITRES ASSISTANTS PRO": 4,
    "ARBITRES ASSISTANTS NAT": 5,
    "DIVISIONNAIRES 1": 6,
    "DIVISIONNAIRES 2": 7,
    "DIVISIONNAIRES 3": 8,
    "LIGUE 1": 9,
    "LIGUE 2": 10,
    "LIGUE 3": 11,
    "LIGUE 4": 12,
    "LIGUE 5": 13,
    "MINEURS 17 ANS": 14,
    "MINEURS 16 ANS": 15,
    "MINEURS 15 ANS": 16
}

# Table COMPETITION NOM → (NIVEAU MIN, NIVEAU MAX)
niveau_competitions = {
    "ELITE 1 FEMININE": (6, 4),
    "ELITE 2 FEMININE": (7, 6),
    "ELITE ALAMERCERY": (7, 6),
    "ELITE CRABOS": (6, 4),
    "ESPOIRS FEDERAUX": (6, 4),
    "EUROPEAN RUGBY CHAMPIONS CUP": (1, 1),
    "EXCELLENCE B - CHAMPIONNAT DE FRANCE": (9, 7),
    "FEDERALE 1": (6, 6),
    "FEDERALE 2": (7, 7),
    "FEDERALE 3": (8, 8),
    "FEDERALE B - CHAMPIONNAT DE FRANCE": (9, 7),
    "FEMININES MOINS DE 18 ANS A XV - ELITE": (7, 6),
    "FEMININES REGIONALES A X": (13, 10),
    "FEMININES REGIONALES A X « MOINS DE 18 ANS »": (14, 13),
    "REGIONAL 1 U16": (15, 9),
    "REGIONAL 1 U19": (10, 9),
    "REGIONAL 2 U16": (15, 9),
    "REGIONAL 2 U19": (13, 9),
    "REGIONAL 3 U16": (15, 9),
    "REGIONAL 3 U19": (13, 9),
    "REGIONALE 1 - CHAMPIONNAT TERRITORIAL": (9, 7),
    "REGIONALE 2 - CHAMPIONNAT TERRITORIAL": (11, 9),
    "REGIONALE 3 - CHAMPIONNAT TERRITORIAL": (13, 9),
    "RESERVES ELITE": (7, 6),
    "RESERVES REGIONALES 1 - CHAMPIONNAT TERRITORIAL": (11, 9),
    "RESERVES REGIONALES 2 - CHAMPIONNAT TERRITORIAL": (13, 11)
}

# Chargement des données
@st.cache_data
def charger_rencontres():
    url = "https://docs.google.com/spreadsheets/d/1cM3QiYhiu22sKSgYKvpahvNWJqlxSk-e/export?format=xlsx"
    df = pd.read_excel(url)
    return nettoyer_colonnes(df)

@st.cache_data
def charger_categories():
    url = "https://docs.google.com/spreadsheets/d/1UcqLFBIxXPWS31O2pyT3Xc5lha7_vjAq/export?format=xlsx"
    df = pd.read_excel(url)
    return nettoyer_colonnes(df)

@st.cache_data
def charger_disponibilites():
    url = "https://docs.google.com/spreadsheets/d/113KAFUl9E4ceFqm-gIfQ-zhigYGnOGPh/export?format=xlsx"
    df = pd.read_excel(url)
    df = nettoyer_colonnes(df)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date
    df['DISPONIBILITE'] = df['DISPONIBILITE'].astype(str).str.strip().str.upper()
    df['DISPONIBILITE'] = df['DISPONIBILITE'].apply(lambda x: "OUI" if x == "OUI" else "NON")
    return df

# Chargement
rencontres = charger_rencontres()
categories = charger_categories()
disponibilites = charger_disponibilites()

# Sélection d'une rencontre
st.subheader("Sélectionnez une rencontre")
rencontre_id = st.selectbox("Rencontre :", rencontres['RENCONTRE NUMERO'].unique())

if rencontre_id:
    ligne = rencontres[rencontres['RENCONTRE NUMERO'] == rencontre_id]
    st.write("Détails de la rencontre :", ligne)

    competition = ligne.iloc[0]['COMPETITION NOM'].strip().upper()
    date_rencontre = ligne.iloc[0]['DATE']

    # Récupération du niveau requis
    niveau_min, niveau_max = niveau_competitions.get(competition, (None, None))
    st.markdown(f"Niveau requis pour cette compétition : **{niveau_min} → {niveau_max}**")

    # Arbitres disponibles à la date
    dispo_date = disponibilites[disponibilites['DATE'] == date_rencontre]
    dispo_oui = dispo_date[dispo_date['DISPONIBILITE'] == "OUI"]

    # Ajout du niveau arbitre
    categories['CATEGORIE'] = categories['CATEGORIE'].str.upper()
    categories['NIVEAU'] = categories['CATEGORIE'].map(categorie_niveau)
    arbitres = pd.merge(dispo_oui, categories[['NUMERO AFFILIATION', 'NIVEAU']], 
                        left_on='NO LICENCE', right_on='NUMERO AFFILIATION', how='left')

    # Filtrage des arbitres compatibles
    arbitres_eligibles = arbitres[
        arbitres['NIVEAU'].apply(lambda x: niveau_min <= x <= niveau_max if pd.notna(x) else False)
    ]

    st.subheader("Arbitres proposés")
    if not arbitres_eligibles.empty:
        st.dataframe(arbitres_eligibles[['NOM', 'PRENOM', 'NO LICENCE', 'NIVEAU']])
    else:
        st.warning("Aucun arbitre disponible et compatible avec le niveau requis.")
