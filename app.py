from pathlib import Path
import matplotlib.pyplot as plt
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

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Type de quartier",
    "Évolution annuelle",
    "Chaleur ou courant ?",
    "Coupures de courant",
    "Relevés records"
])
# Onglet 1
with tab1:
    st.subheader("Consommation moyenne par abonné selon le quartier")
    moy_type = df_filtre.groupby("type")["kwh_par_abonne"].mean().round(1)
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.write("**Moyenne par type :**")
        st.dataframe(moy_type.reset_index(name="kWh / abonné"), hide_index=True)
        st.caption("Les quartiers commerciaux présentent une intensité d'usage nettement supérieure.")
    
    with col_b:
        classement = (
            df_filtre.groupby("quartier")["kwh_par_abonne"]
            .mean()
            .sort_values(ascending=True)
        )
        fig, ax = plt.subplots(figsize=(8, 4))
        classement.plot(kind="barh", ax=ax, color="#1f77b4")
        ax.set_xlabel("kWh par abonné")
        ax.set_ylabel("Quartier")
        ax.grid(axis="x", linestyle="--", alpha=0.6)
        st.pyplot(fig)
        plt.close(fig)
# Onglet 2
with tab2:
    st.subheader("Évolution mensuelle par commune")
    st.markdown("Comparatif des profils de consommation sur les mois de l'année sélectionnée.")
    
    courbes = df_filtre.groupby(["mois", "commune"])["kwh_par_abonne"].mean().unstack()
    fig, ax = plt.subplots(figsize=(10, 4.5))
    courbes.plot(ax=ax, marker="o")
    ax.set_ylabel("kWh par abonné")
    ax.set_xlabel("Mois")
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)
    plt.close(fig)
# Onglet 3
with tab3:
    st.subheader("Analyse des corrélations (Secteur Résidentiel)")
    df_res = df_filtre[df_filtre["type"] == "Résidentiel"]
    
    if len(df_res) > 2:
        r_courant = df_res["kwh_par_abonne"].corr(df_res["heures_courant"]).round(2)
        r_temp = df_res["kwh_par_abonne"].corr(df_res["temperature_c"]).round(2)
        
        st.info(f"**Corrélations observées :** **{r_courant}** avec les heures de courant | **{r_temp}** avec la température.")
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.scatter(df_res["heures_courant"], df_res["kwh_par_abonne"], color="teal", alpha=0.7)
        ax.set_xlabel("Heures de courant par jour")
        ax.set_ylabel("kWh par abonné")
        ax.set_title("Heures de courant vs Consommation par abonné")
        ax.grid(True, linestyle="--", alpha=0.6)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.write("Pas assez de données résidentielles pour calculer la corrélation sur ce filtre.")
# Onglet 4
with tab4:
    st.subheader("Distribution de la disponibilité électrique")
    stats_c = df_filtre.groupby("commune")["heures_courant"].agg(
        Médiane="median",
        Q1=lambda s: s.quantile(0.25),
        Q3=lambda s: s.quantile(0.75)
    ).round(1)
    
    st.dataframe(stats_c)
    
    if "Cap-Haïtien" in df_filtre["commune"].values:
        cap_data = df_filtre[df_filtre["commune"] == "Cap-Haïtien"]["heures_courant"]
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.hist(cap_data, bins=8, color="darkorange", edgecolor="black")
        ax.set_title("Distribution des heures de courant - Cap-Haïtien")
        ax.set_xlabel("Heures de courant par jour")
        ax.set_ylabel("Nombre de relevés")
        st.pyplot(fig)
        plt.close(fig)
        
# Onglet 5 
with tab5:
    st.subheader("Relevés avec la plus forte consommation")
    top_records = df_filtre.sort_values(by="kwh", ascending=False).head(5)
    st.dataframe(
        top_records[["mois", "commune", "quartier", "type", "kwh", "kwh_par_abonne"]],
        hide_index=True
    )
st.divider()
