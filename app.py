import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuration
st.set_page_config(layout="wide", page_title="Dashboard Boursier")
st.markdown("""<style>.stApp {background-color: #0e1117; color: white;}</style>""", unsafe_allow_html=True)

# 1. Chargement de la base de données
@st.cache_data
def load_db():
    return pd.read_csv('Analyse ACTION - DATA BASE.csv')

df_base = load_db()

# Votre liste complète
tickers_list = [
    "TTE.PA", "AI.PA", "MC.PA", "RACE.MI", "VRLA.PA", "NESN.SW", "SU.PA", "RMS.PA", 
    "ASML.AS", "TSM", "ATCO-A.ST", "GTT.PA", "DSY.PA", "AM.PA", "DG.PA", "EL.PA", 
    "RI.PA", "FDJ.PA", "EN.PA", "ML.PA", "AC.PA", "EDEN.PA", "AIR.PA", "VIE.PA", 
    "HO.PA", "SAP.DE", "CPRT", "CMG", "DPZ", "COST", "IBE.MC", "SAN.PA", "RMD", 
    "NOVO-B.CO", "IPS.PA", "ZTS", "NVDA", "GOOGL", "MSFT", "COIN", "ACA.PA", 
    "GLE.PA", "BNP.PA", "CS.PA", "ASRNL.AS", "ALV.DE", "COV.PA", "GFC.PA", "DB1.DE", 
    "ENX.PA", "AMUN.PA", "1810.HK", "ADBE", "0700.HK", "KPG.AX", "TSLA", "CRM", 
    "SPGI", "BKNG", "CSU.TO", "EQS.PA", "MA", "MCD", "KO", "V", "ENGI.PA", "ORA.PA"
]

# 2. Fonctions Technique
@st.cache_data
def get_data(ticker, years):
    data = yf.download(ticker, period=f"{years}y", interval='1wk', progress=False)
    if data.empty: return None
    y = data['Close'].iloc[:, 0].values if isinstance(data['Close'], pd.DataFrame) else data['Close'].values
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    reg = slope * x + intercept
    std = np.std(y)
    return data.index, y, reg, std

def plot_tech(ticker, years):
    data = get_data(ticker, years)
    if not data: return
    idx, y, reg, std = data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=idx, y=y, name='Prix', line=dict(color='white', width=1)))
    fig.add_trace(go.Scatter(x=idx, y=reg, name='Régression', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=idx, y=reg+std, name='+1σ', line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg-std, name='-1σ', line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg+2*std, name='+2σ', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg-2*std, name='-2σ', line=dict(color='red', dash='dot')))
    fig.update_layout(template="plotly_dark", title=f"{years} ans", height=350, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 3. Interface
st.title("Dashboard Boursier Complet")
tab1, tab2 = st.tabs(["📊 Analyse Technique", "📈 Analyse Fondamentale"])

with tab1:
    selected = st.multiselect("Actions à afficher :", tickers_list, default=["TTE.PA"])
    for t in selected:
        st.subheader(f"Technique : {t}")
        c1, c2 = st.columns(2)
        with c1: plot_tech(t, 10)
        with c2: plot_tech(t, 20)

with tab2:
    target = st.selectbox("Sélectionner l'action :", tickers_list)
    # On filtre le CSV avec la liste de tickers
    hist = df_base[df_base['TICKER'] == target].sort_values(by='Anné')
    
    if not hist.empty:
        latest = hist.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PER", str(latest.get('Per', 'N/A')))
        c2.metric("Dette/EBITDA", str(latest.get('Dette/EBITDA', 'N/A')))
        c3.metric("Score", str(latest.get('SCORE VALUE', 'N/A')))
        c4.metric("Div %", str(latest.get('Dividende %', 'N/A')))
        
        st.write("---")
        colA, colB = st.columns(2)
        with colA:
            st.subheader("Dividende €")
            fig = go.Figure(go.Scatter(x=hist['Anné'], y=hist['Dividende €'], mode='lines+markers', line=dict(color='green')))
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, use_container_width=True)
        with colB:
            st.subheader("Payout Ratio")
            fig = go.Figure(go.Scatter(x=hist['Anné'], y=hist['PAY OUT RATIO'], mode='lines+markers', line=dict(color='orange')))
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, use_container_width=True)
