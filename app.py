
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analisi Budget vs Effettivo", layout="wide")
st.title("📊 Confronto Ore Lavorate vs Ore a Budget per Cliente")

uploaded_file = st.file_uploader("Carica un file Excel con due fogli", type=["xlsx"])

if uploaded_file:
    try:
        # Lettura dei due fogli
        df_eff = pd.read_excel(uploaded_file, sheet_name=0)
        df_budget = pd.read_excel(uploaded_file, sheet_name=1)

        # Normalizzazione colonne
        df_eff.columns = df_eff.columns.str.strip().str.lower()
        df_budget.columns = df_budget.columns.str.strip()

        # Controllo colonne essenziali
        if not {'cliente', 'data', 'ore'}.issubset(df_eff.columns):
            st.error("Il primo foglio deve contenere le colonne: cliente, data, ore")
        else:
            df_eff['data'] = pd.to_datetime(df_eff['data'], format='%d-%m-%Y', errors='coerce')
            if df_eff['data'].isnull().any():
                st.warning("Alcune date non sono state lette correttamente. Controlla il formato gg-mm-aaaa.")

            df_eff['mese'] = df_eff['data'].dt.to_period('M').astype(str)
            df_eff['giorno'] = df_eff['data'].dt.day

            # Dataset 1: dal 1 al 15
            df_1_15 = df_eff[df_eff['giorno'] <= 15].copy()
            pivot_1_15 = df_1_15.pivot_table(index='cliente', columns='mese', values='ore', aggfunc='sum', fill_value=0)
            pivot_1_15.columns = [f"{col} (1-15)" for col in pivot_1_15.columns]

            # Dataset 2: tutto il mese
            pivot_1_fine = df_eff.pivot_table(index='cliente', columns='mese', values='ore', aggfunc='sum', fill_value=0)
            pivot_1_fine.columns = [f"{col} (1-fine)" for col in pivot_1_fine.columns]

            # Unione effettivi
            df_eff_tot = pd.concat([pivot_1_15, pivot_1_fine], axis=1).fillna(0)
            df_eff_tot = df_eff_tot.reindex(sorted(df_eff_tot.columns), axis=1)

            # Uniforma l'indice
            df_eff_tot.index = df_eff_tot.index.astype(str)
            df_budget.index = df_budget['cliente'].astype(str)
            df_budget = df_budget.drop(columns=['cliente'])

            # Allineamento colonne
            comuni = df_eff_tot.columns.intersection(df_budget.columns)
            if comuni.empty:
                st.error("Nessuna colonna in comune tra effettivo e budget. Controlla l'intestazione del secondo foglio.")
            else:
                eff = df_eff_tot[comuni].copy()
                budget = df_budget[comuni].copy()

                # Calcolo scostamento %
                diff_percent = (budget - eff) / budget.replace(0, np.nan) * 100
                diff_percent = diff_percent.replace([np.inf, -np.inf], np.nan)

                st.subheader("Scostamento percentuale tra Budget e Ore Effettive")

                def color_map(val):
                    if pd.isna(val):
                        return ''
                    elif val >= 10:
                        return 'background-color: #b6fcb6'  # verde
                    elif 0 <= val < 10:
                        return 'background-color: #fff59d'  # giallo
                    else:
                        return 'background-color: #ff9999'  # rosso

                styled = diff_percent.style.format("{:.1f}%").applymap(color_map)
                st.dataframe(styled, use_container_width=True)

    except Exception as e:
        st.error(f"Errore durante l'elaborazione: {e}")
