import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
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

# Sélection de la date dans la barre latérale
dates_disponibles = df["DATE"].sort_values().unique()
date_selectionnee = st.sidebar.selectbox("📅 Sélectionnez une date :", dates_disponibles)

# On filtre par date
df_filtre = df[df["DATE"] == pd.to_datetime(date_selectionnee)]

# 🔍 Filtres supplémentaires
st.sidebar.markdown("### 🎛️ Filtres avancés")

# Disposnibilité
disponibilites = ["Tous"] + sorted(df_filtre["DISPONIBILITE"].unique())
dispo_filtre = st.sidebar.selectbox("Disponibilité :", disponibilites)

# Département
departements = ["Tous"] + sorted(df_filtre["DPT DE RESIDENCE"].astype(str).unique())
dpt_filtre = st.sidebar.selectbox("Département :", departements)

# Club
clubs = ["Tous"] + sorted(df_filtre["CLUB NOM"].dropna().unique())
club_filtre = st.sidebar.selectbox("Club :", clubs)

# Application des filtres
if dispo_filtre != "Tous":
    df_filtre = df_filtre[df_filtre["DISPONIBILITE"] == dispo_filtre]
if dpt_filtre != "Tous":
    df_filtre = df_filtre[df_filtre["DPT DE RESIDENCE"].astype(str) == dpt_filtre]
if club_filtre != "Tous":
    df_filtre = df_filtre[df_filtre["CLUB NOM"] == club_filtre]

# ✅ Option de filtrage rapide
filtrer_libres = st.sidebar.checkbox("🔎 Afficher uniquement les arbitres disponibles et non désignés")

# Appliquer le filtre si coché
if filtrer_libres:
    df_filtre = df_filtre[
        (df_filtre["DISPONIBILITE"] == "OUI") & (df_filtre["DESIGNATION"] == 0)
    ]


# KPIs
total = len(df_filtre)
dispo = (df_filtre["DISPONIBILITE"] == "OUI").sum()
designe = (df_filtre["DESIGNATION"] == 1).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total arbitres", total)
col2.metric("Disponibles", dispo)
col3.metric("Déjà désignés", designe)

# Affichage du tableau
# ✅ Remplacer DESIGNATION par ✅ / ❌
df_filtre = df_filtre.copy()  # éviter SettingWithCopyWarning
df_filtre["AFFECTÉ ?"] = df_filtre["DESIGNATION"].map({1: "✅", 0: "❌"})

# ✅ Définir les colonnes à afficher
colonnes = ["Nom", "PRENOM", "DPT DE RESIDENCE", "DISPONIBILITE", "AFFECTÉ ?"]

# Fonction de style conditionnel
def surligner_designation(row):
    return ['background-color: #ffe599'] * len(row) if row["DESIGNATION"] == 1 else [''] * len(row)

# Colonnes à afficher
# 🎨 Fonction de style sur les lignes
def style_lignes(row):
    if row["DISPONIBILITE"] == "OUI" and row["AFFECTÉ ?"] == "❌":
        return ['background-color: #d9ead3'] * len(row)  # vert clair
    elif row["AFFECTÉ ?"] == "✅":
        return ['background-color: #fff2cc'] * len(row)  # jaune clair
    else:
        return [''] * len(row)

styled_df = df_filtre[colonnes].style.apply(style_lignes, axis=1)

# 📋 Affichage du tableau
st.subheader("📋 Détails arbitres pour le {}".format(date_selectionnee.strftime('%d/%m/%Y')))
st.write(styled_df)


# Optionnel : graphique
st.subheader("📊 Répartition des disponibilités")
fig = px.pie(df_filtre, names="DISPONIBILITE", title="Disponibilité des arbitres")
st.plotly_chart(fig, use_container_width=True)
