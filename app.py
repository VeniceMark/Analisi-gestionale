
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analisi Ore Lavorate", layout="wide")

st.title("📊 Analisi Ore Lavorate per Cliente e Mese")

uploaded_file = st.file_uploader("Carica un file Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # Normalizzazione nomi colonne
        df.columns = df.columns.str.strip().str.lower()

        # Controllo colonne obbligatorie
        required_cols = {'cliente', 'data', 'ore'}
        if not required_cols.issubset(df.columns):
            st.error("Il file deve contenere le colonne: cliente, data, ore")
        else:
            # Conversione colonna data
            df['data'] = pd.to_datetime(df['data'], format='%d-%m-%Y', errors='coerce')
            if df['data'].isnull().any():
                st.warning("Alcune date non sono state lette correttamente. Controlla il formato gg-mm-aaaa.")

            df['mese'] = df['data'].dt.to_period('M').astype(str)

            # Tabella pivot: clienti in riga, mesi in colonna, ore sommate
            pivot = df.pivot_table(index='cliente', columns='mese', values='ore', aggfunc='sum', fill_value=0)

            # Calcolo Totale Ore per cliente
            pivot['Totale Ore'] = pivot.sum(axis=1)

            st.subheader("Tabella riepilogativa per Cliente e Mese")
            st.dataframe(pivot, use_container_width=True)

            st.subheader("Grafico ore per cliente per mese")
            fig, ax = plt.subplots(figsize=(10, 6))
            pivot.drop(columns='Totale Ore').T.plot(kind='bar', stacked=True, ax=ax)
            ax.set_ylabel("Ore totali")
            ax.set_xlabel("Mese")
            ax.set_title("Ore lavorate per Cliente per Mese")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
