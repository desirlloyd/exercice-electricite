from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")
DOSSIER = Path(__file__).parent / "donnees"

@st.cache_data
def charger_donnees():
    chemin = DOSSIER / "consommation_propre.csv"
    return pd.read_csv(chemin)
df = charger_donnees()
st.markdown("""
Cette application analyse deux années de consommation électrique (2024-2025) réparties sur 12 quartiers de 4 communes haïtiennes.
L'objectif est d'identifier si les variations de consommation sont pilotées par les hausses de température ou par le nombre d'heures de disponibilité du courant.
""")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")


st.sidebar.header("Filtres")

communes_disponibles = sorted(df["commune"].unique())
communes_selectionnees = st.sidebar.multiselect(
    "Communes",
    options=communes_disponibles,
    default=communes_disponibles
)

annees_disponibles = sorted(df["annee"].unique(), reverse=True)
annee_selectionnee = st.sidebar.selectbox(
    "Année",
    options=annees_disponibles,
    index=0  
)

if not communes_selectionnees:
    st.warning("Veuillez sélectionner au moins une commune dans la barre latérale.")
    st.stop()


df_filtre = df[
    (df["commune"].isin(communes_selectionnees)) &
    (df["annee"] == annee_selectionnee)
]

conso_totale_m = (df_filtre["kwh"].sum() / 1e6).round(2)
kwh_abonne_moy = df_filtre["kwh_par_abonne"].mean().round(1)
heures_moy = df_filtre["heures_courant"].mean().round(1)

col1, col2, col3 = st.columns(3)
col1.metric("Consommation totale", f"{conso_totale_m} M kWh")
col2.metric("Moyenne par abonné", f"{kwh_abonne_moy} kWh")
col3.metric("Disponibilité moyenne", f"{heures_moy} h / jour")

brut = pd.read_csv(DOSSIER / "consommation_brut.csv")
st.write(f"Le fichier brut compte {len(brut)} lignes.")
st.dataframe(brut.head(10), hide_index=True)
