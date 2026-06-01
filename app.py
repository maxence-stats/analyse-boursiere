import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuration
st.set_page_config(layout="wide", page_title="Dashboard Boursier")
st.markdown("""<style>.stApp {background-color: #0e1117; color: white;}</style>""", unsafe_allow_html=True)

# 1. Chargement
@st.cache_data
def load_db():
    # Remplacez par votre nom de fichier exact
    df = pd.read_csv('Analyse ACTION - DATA BASE.csv')
    # Nettoyage : on s'assure que les colonnes numériques sont bien interprétées
    # Conversion de "Dividende €" si nécessaire (remplacement des virgules)
    if df['Dividende €'].dtype == 'object':
        df['Dividende €'] = df['Dividende €'].astype(str).str.replace(',', '.').astype(float)
    return df

df_base = load_db()

# 2. Fonction Technique
@st.cache_data
def get_tech_data(ticker, years):
    # Gestion des tickers (ex: EPA:TTE -> TTE.PA)
    clean_ticker = ticker.split(':')[-1] if ':' in ticker else ticker
    if not clean_ticker.endswith('.PA') and not any(x in clean_ticker for x in ['.SW', '.DE', '.MI', '.AS']):
        clean_ticker += ".PA"
        
    data = yf.download(clean_ticker, period=f"{years}y", interval='1wk', progress=False)
    if data.empty: return None, None, None, None
    y = data['Close'].iloc[:, 0].values
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    reg = slope * x + intercept
    std = np.std(y)
    return data.index, y, reg, std

# 3. Dashboard
st.title("Dashboard Boursier")
tab1, tab2 = st.tabs(["📊 Analyse Technique", "📈 Analyse Fondamentale"])

with tab1:
    all_tickers = df_base['TICKER'].dropna().unique()
    selected = st.selectbox("Action :", all_tickers)
    idx, y, reg, std = get_tech_data(selected, 10)
    if idx is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=idx, y=y, name='Prix', line=dict(color='white')))
        fig.add_trace(go.Scatter(x=idx, y=reg, name='Régression', line=dict(color='red', width=3)))
        fig.add_trace(go.Scatter(x=idx, y=reg+std, name='±1σ', line=dict(color='blue', dash='dot')))
        fig.add_trace(go.Scatter(x=idx, y=reg-std, name='±1σ', line=dict(color='blue', dash='dot')))
        fig.add_trace(go.Scatter(x=idx, y=reg+2*std, name='±2σ', line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter(x=idx, y=reg-2*std, name='±2σ', line=dict(color='red', dash='dot')))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    hist = df_base[df_base['TICKER'] == selected].sort_values(by='Anné')
    
    # Indicateurs clés (sans le PER)
    col1, col2, col3 = st.columns(3)
    latest = hist.iloc[-1]
    col1.metric("Score Value", str(latest.get('SCORE VALUE', 'N/A')))
    col2.metric("Dette/EBITDA", str(latest.get('Dette/EBITDA', 'N/A')))
    col3.metric("Dividende %", str(latest.get('Dividende %', 'N/A')))
    
    # Graphiques
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Dividende €")
        st.line_chart(hist.set_index('Anné')['Dividende €'])
    with c2:
        st.subheader("Payout Ratio")
        st.line_chart(hist.set_index('Anné')['PAY OUT RATIO'])
