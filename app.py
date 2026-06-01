import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuration
st.set_page_config(layout="wide", page_title="Dashboard Pro")
st.markdown("""<style>.stApp {background-color: #0e1117; color: white;}</style>""", unsafe_allow_html=True)

## --- 1. CHARGEMENT ET CONFIGURATION ---
@st.cache_data
def load_db():
    # ASSUREZ-VOUS QUE LE FICHIER EST À LA RACINE
    return pd.read_csv('Analyse ACTION - DATA BASE.csv')

# Liste des tickers
tickers_list = ["TTE.PA", "AI.PA", "MC.PA", "RACE.MI", "VRLA.PA", "NESN.SW", "SU.PA", "RMS.PA", 
    "ASML.AS", "TSM", "ATCO-A.ST", "GTT.PA", "DSY.PA", "AM.PA", "DG.PA", "EL.PA", 
    "RI.PA", "FDJ.PA", "EN.PA", "ML.PA", "AC.PA", "EDEN.PA", "AIR.PA", "VIE.PA", 
    "HO.PA", "SAP.DE", "CPRT", "CMG", "DPZ", "COST", "IBE.MC", "SAN.PA", "RMD", 
    "NOVO-B.CO", "IPS.PA", "ZTS", "NVDA", "GOOGL", "MSFT", "COIN", "ACA.PA", 
    "GLE.PA", "BNP.PA", "CS.PA", "ASRNL.AS", "ALV.DE", "COV.PA", "GFC.PA", "DB1.DE", 
    "ENX.PA", "AMUN.PA", "1810.HK", "ADBE", "0700.HK", "KPG.AX", "TSLA", "CRM", 
    "SPGI", "BKNG", "CSU.TO", "EQS.PA", "MA", "MCD", "KO", "V", "ENGI.PA", "ORA.PA"]

df_base = load_db()

st.title("Mon Dashboard Boursier")
tab1, tab2 = st.tabs(["📊 Analyse Technique", "📈 Analyse Fondamentale"])

## --- 2. ONGLET TECHNIQUE ---
with tab1:
    st.header("Graphiques de Régression")
    selected_t = st.selectbox("Action à analyser :", tickers_list, key="tech_select")
    
    @st.cache_data
    def get_tech_data(ticker, years):
        data = yf.download(ticker, period=f"{years}y", interval='1wk', progress=False)
        if data.empty: return None
        y = data['Close'].iloc[:, 0].values
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        reg = slope * x + intercept
        std = np.std(y)
        return data.index, y, reg, std

    def plot_final(ticker, years):
        idx, y, reg, std = get_tech_data(ticker, years)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=idx, y=y, name='Prix', line=dict(color='white')))
        fig.add_trace(go.Scatter(x=idx, y=reg, name='Rég', line=dict(color='red', width=3)))
        fig.add_trace(go.Scatter(x=idx, y=reg+std, name='+1σ', line=dict(color='blue', dash='dot')))
        fig.add_trace(go.Scatter(x=idx, y=reg-std, name='-1σ', line=dict(color='blue', dash='dot')))
        fig.add_trace(go.Scatter(x=idx, y=reg+2*std, name='+2σ', line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter(x=idx, y=reg-2*std, name='-2σ', line=dict(color='red', dash='dot')))
        fig.update_layout(template="plotly_dark", title=f"{years} ans", height=400)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1: plot_final(selected_t, 10)
    with c2: plot_final(selected_t, 20)

## --- 3. ONGLET FONDAMENTAL ---
with tab2:
    st.header("Historique Financier")
    target = st.selectbox("Sélectionner l'action :", tickers_list, key="fund_select")
    
    # FILTRAGE DU CSV
    hist = df_base[df_base['TICKER'] == target].sort_values(by='Anné')
    
    if not hist.empty:
        # Affichage métriques
        row = hist.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PER", str(row.get('Per', 'N/A')))
        c2.metric("Dette/EBITDA", str(row.get('Dette/EBITDA', 'N/A')))
        c3.metric("Score Value", str(row.get('SCORE VALUE', 'N/A')))
        c4.metric("Dividende %", str(row.get('Dividende %', 'N/A')))
        
        # Graphiques historiques
        colA, colB = st.columns(2)
        with colA:
            st.subheader("Dividende €")
            st.line_chart(hist.set_index('Anné')['Dividende €'])
        with colB:
            st.subheader("Payout Ratio")
            st.line_chart(hist.set_index('Anné')['PAY OUT RATIO'])
    else:
        st.error("Aucune donnée trouvée dans le CSV pour ce ticker.")
