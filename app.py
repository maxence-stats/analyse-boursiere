import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Tableau de bord : Analyse Technique Long Terme")

# Votre liste complète d'entreprises
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

def get_regression_data(ticker, years):
    data = yf.download(ticker, period=f"{years}y", progress=False)
    if data.empty: return None
    
    # Gestion des colonnes
    y = data['Close'].iloc[:, 0].values if isinstance(data['Close'], pd.DataFrame) else data['Close'].values
    x = np.arange(len(y))
    
    # Calculs
    slope, intercept = np.polyfit(x, y, 1)
    reg = slope * x + intercept
    std = np.std(y)
    
    return pd.DataFrame({'Prix': y, 'Reg': reg, '+1σ': reg+std, '-1σ': reg-std, '+2σ': reg+2*std, '-2σ': reg-2*std})

# Sélection pour filtrer
selected_tickers = st.multiselect("Filtrer par action", tickers_list, default=tickers_list[:5])

for t in selected_tickers:
    st.subheader(f"Action : {t}")
    col1, col2 = st.columns(2)
    
    data10 = get_regression_data(t, 10)
    data20 = get_regression_data(t, 20)
    
    with col1:
        st.write("10 Ans")
        if data10 is not None: st.line_chart(data10)
    with col2:
        st.write("20 Ans")
        if data20 is not None: st.line_chart(data20)
