from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

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

brut = pd.read_csv(DOSSIER / "consommation_brut.csv")
st.write(f"Le fichier brut compte {len(brut)} lignes.")
st.dataframe(brut.head(10), hide_index=True)
