
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analisi Ore Lavorate", layout="wide")
st.title("📊 Ore Lavorate per Cliente - Parziale (1-15) e Totale (1-fine) del mese")

uploaded_file = st.file_uploader("Carica un file Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()

        required_cols = {'cliente', 'data', 'ore'}
        if not required_cols.issubset(df.columns):
            st.error("Il file deve contenere le colonne: cliente, data, ore")
        else:
            df['data'] = pd.to_datetime(df['data'], format='%d-%m-%Y', errors='coerce')
            if df['data'].isnull().any():
                st.warning("Alcune date non sono state lette correttamente. Controlla il formato gg-mm-aaaa.")

            df['mese'] = df['data'].dt.to_period('M').astype(str)
            df['giorno'] = df['data'].dt.day

            # Dataset 1: dal giorno 1 al 15
            df_1_15 = df[df['giorno'] <= 15].copy()
            pivot_1_15 = df_1_15.pivot_table(index='cliente', columns='mese', values='ore', aggfunc='sum', fill_value=0)
            pivot_1_15.columns = [f"{col} (1-15)" for col in pivot_1_15.columns]

            # Dataset 2: tutto il mese
            pivot_1_fine = df.pivot_table(index='cliente', columns='mese', values='ore', aggfunc='sum', fill_value=0)
            pivot_1_fine.columns = [f"{col} (1-fine)" for col in pivot_1_fine.columns]

            # Merge
            pivot = pd.concat([pivot_1_15, pivot_1_fine], axis=1).fillna(0)

            # Ordina le colonne per mese (alfanumerico)
            pivot = pivot.reindex(sorted(pivot.columns, key=lambda x: (x.split()[0], x.split()[1])), axis=1)

            # Calcolo Totale
            pivot["Totale Ore"] = pivot.sum(axis=1)

            st.subheader("Tabella riepilogativa per Cliente")
            st.dataframe(pivot, use_container_width=True)

    except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")
