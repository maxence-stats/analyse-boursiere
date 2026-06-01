import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Analyse Boursière : Régression Linéaire Hebdomadaire")

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

@st.cache_data
def get_data(ticker, years):
    # Données hebdomadaires pour un lissage identique à vos graphiques
    data = yf.download(ticker, period=f"{years}y", interval='1wk', progress=False)
    if data.empty: return None
    
    y = data['Close'].iloc[:, 0].values if isinstance(data['Close'], pd.DataFrame) else data['Close'].values
    x = np.arange(len(y))
    
    slope, intercept = np.polyfit(x, y, 1)
    reg = slope * x + intercept
    std = np.std(y)
    return data.index, y, reg, std

def plot_graph(ticker, years):
    data = get_data(ticker, years)
    if not data: return
    idx, y, reg, std = data
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=idx, y=y, name='Prix', line=dict(color='black', width=1.5)))
    fig.add_trace(go.Scatter(x=idx, y=reg, name='Régression', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=idx, y=reg+std, name='+1σ', line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg-std, name='-1σ', line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg+2*std, name='+2σ', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg-2*std, name='-2σ', line=dict(color='red', dash='dot')))
    
    fig.update_layout(template="plotly_white", title=f"Horizon {years} ans", height=400, margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

selected_tickers = st.multiselect("Sélectionnez les entreprises :", tickers_list, default=["TTE.PA"])

for t in selected_tickers:
    st.subheader(f"Action : {t}")
    col1, col2 = st.columns(2)
    with col1: plot_graph(t, 10)
    with col2: plot_graph(t, 20)
