import streamlit as st
import pandas as pd
import unicodedata

st.set_page_config(page_title="Affectation des arbitres", layout="wide")
st.title("Affectation automatique des arbitres aux rencontres")

def nettoyer_colonnes(df):
    df.columns = [
        unicodedata.normalize('NFKD', col).encode('ascii', errors='ignore').decode('utf-8').strip().upper()
        for col in df.columns
    ]
    return df

categorie_niveau = {
    "INTERNATIONNAUX": 1, "2EME DIVISION PRO": 2, "NATIONALE 1 ET 2": 3,
    "ARBITRES ASSISTANTS PRO": 4, "ARBITRES ASSISTANTS NAT": 5,
    "DIVISIONNAIRES 1": 6, "DIVISIONNAIRES 2": 7, "DIVISIONNAIRES 3": 8,
    "LIGUE 1": 9, "LIGUE 2": 10, "LIGUE 3": 11, "LIGUE 4": 12, "LIGUE 5": 13,
    "MINEURS 17 ANS": 14, "MINEURS 16 ANS": 15, "MINEURS 15 ANS": 16
}

niveau_competitions = {
    "ELITE 1 FEMININE": (6, 4), "ELITE 2 FEMININE": (7, 6),
    "ELITE ALAMERCERY": (7, 6), "ELITE CRABOS": (6, 4),
    "ESPOIRS FEDERAUX": (6, 4), "EUROPEAN RUGBY CHAMPIONS CUP": (1, 1),
    "EXCELLENCE B - CHAMPIONNAT DE FRANCE": (9, 7), "FEDERALE 1": (6, 6),
    "FEDERALE 2": (7, 7), "FEDERALE 3": (8, 8),
    "FEDERALE B - CHAMPIONNAT DE FRANCE": (9, 7),
    "FEMININES MOINS DE 18 ANS A XV - ELITE": (7, 6),
    "FEMININES REGIONALES A X": (13, 10),
    "FEMININES REGIONALES A X « MOINS DE 18 ANS »": (14, 13),
    "REGIONAL 1 U16": (15, 9), "REGIONAL 1 U19": (10, 9),
    "REGIONAL 2 U16": (15, 9), "REGIONAL 2 U19": (13, 9),
    "REGIONAL 3 U16": (15, 9), "REGIONAL 3 U19": (13, 9),
    "REGIONALE 1 - CHAMPIONNAT TERRITORIAL": (9, 7),
    "REGIONALE 2 - CHAMPIONNAT TERRITORIAL": (11, 9),
    "REGIONALE 3 - CHAMPIONNAT TERRITORIAL": (13, 9),
    "RESERVES ELITE": (7, 6),
    "RESERVES REGIONALES 1 - CHAMPIONNAT TERRITORIAL": (11, 9),
    "RESERVES REGIONALES 2 - CHAMPIONNAT TERRITORIAL": (13, 11)
}

@st.cache_data
def charger_rencontres():
    url = "https://docs.google.com/spreadsheets/d/1cM3QiYhiu22sKSgYKvpahvNWJqlxSk-e/export?format=xlsx"
    return nettoyer_colonnes(pd.read_excel(url))

@st.cache_data
def charger_arbitres():
    url = "https://docs.google.com/spreadsheets/d/1UUZBFPMCkVGzVKeTP_D44ZpGwTHlu0Q0/export?format=xlsx"
    return nettoyer_colonnes(pd.read_excel(url))

@st.cache_data
def charger_disponibilites():
    url = "https://docs.google.com/spreadsheets/d/113KAFUl9E4ceFqm-gIfQ-zhigYGnOGPh/export?format=xlsx"
    df = nettoyer_colonnes(pd.read_excel(url))
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date
    df['DISPONIBILITE'] = df['DISPONIBILITE'].astype(str).str.strip().str.upper()
    df['DISPONIBILITE'] = df['DISPONIBILITE'].apply(lambda x: "OUI" if x == "OUI" else "NON")
    return df

# --- Affichage principal ---
rencontres = charger_rencontres()
arbitres = charger_arbitres()
disponibilites = charger_disponibilites()

st.subheader("Sélectionnez une rencontre")
rencontre_id = st.selectbox("Rencontre :", rencontres['RENCONTRE NUMERO'].dropna().unique())

if rencontre_id:
    ligne = rencontres[rencontres['RENCONTRE NUMERO'] == rencontre_id]

    if ligne.empty:
        st.error("Aucune ligne trouvée pour cette rencontre. Vérifiez que le numéro est correct.")
    else:
        try:
            competition = ligne.iloc[0]['COMPETITION NOM'].strip().upper()
            date_rencontre = ligne.iloc[0]['DATE']
        except Exception as e:
            st.error(f"Erreur lors de la lecture des données de la rencontre : {e}")
        else:
            st.write("Détails de la rencontre :", ligne)

            niveau_min, niveau_max = niveau_competitions.get(competition, (None, None))
            if niveau_min is None or niveau_max is None:
                st.warning("Compétition non reconnue dans la table des niveaux.")
            else:
                st.markdown(f"Niveau requis pour cette compétition : **{niveau_min} → {niveau_max}**")

                dispo_date = disponibilites[disponibilites['DATE'] == date_rencontre]
                dispo_oui = dispo_date[dispo_date['DISPONIBILITE'] == "OUI"]

                arbitres_dispo = pd.merge(dispo_oui, arbitres, left_on='NO LICENCE', right_on='NUMERO AFFILIATION', how='left')
                arbitres_dispo['CATEGORIE'] = arbitres_dispo['CATEGORIE'].str.upper()
                arbitres_dispo['NIVEAU'] = arbitres_dispo['CATEGORIE'].map(categorie_niveau)

                arbitres_eligibles = arbitres_dispo[
                    arbitres_dispo['NIVEAU'].apply(lambda x: niveau_min <= x <= niveau_max if pd.notna(x) else False)
                ]

                st.subheader("Arbitres proposés")
                if not arbitres_eligibles.empty:
                    st.dataframe(arbitres_eligibles[['NOM', 'PRENOM', 'NO LICENCE', 'CATEGORIE', 'NIVEAU']])
                else:
                    st.warning("Aucun arbitre disponible et compatible avec le niveau requis.")
