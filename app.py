import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuration visuelle
st.set_page_config(layout="wide", page_title="Dashboard Boursier")
st.markdown("""<style>.stApp {background-color: #0e1117; color: white;}</style>""", unsafe_allow_html=True)

# 1. Chargement des données
@st.cache_data
def load_db():
    return pd.read_csv('Analyse ACTION - DATA BASE.csv')

df_base = load_db()

# 2. Fonctions techniques
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

def plot_graph(ticker, years):
    data = get_data(ticker, years)
    if not data: return
    idx, y, reg, std = data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=idx, y=y, name='Prix', line=dict(color='white', width=1.5)))
    fig.add_trace(go.Scatter(x=idx, y=reg, name='Régression', line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=idx, y=reg+std, name='+1σ', line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg-std, name='-1σ', line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg+2*std, name='+2σ', line=dict(color='red', dash='dot')))
    fig.add_trace(go.Scatter(x=idx, y=reg-2*std, name='-2σ', line=dict(color='red', dash='dot')))
    fig.update_layout(template="plotly_dark", title=f"{years} ans", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 3. Interface principale
st.title("Mon Tableau de Bord Boursier")
tab1, tab2 = st.tabs(["📊 Analyse Technique (Graphiques)", "📈 Analyse Fondamentale (Data)"])

# Onglet 1 : Graphiques
with tab1:
    tickers = df_base['TICKER'].dropna().unique()
    selected = st.multiselect("Actions à afficher :", tickers, default=[tickers[0]])
    for t in selected:
        st.subheader(f"Action : {t}")
        c1, c2 = st.columns(2)
        with c1: plot_graph(t, 10)
        with c2: plot_graph(t, 20)

# Onglet 2 : Dashboard Fondamental
with tab2:
    target = st.selectbox("Choisir l'action pour les détails :", df_base['TICKER'].unique())
    row = df_base[df_base['TICKER'] == target].iloc[0]
    st.write("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PER", row.get('PER', 'N/A'))
    c2.metric("Dette/EBITDA", row.get('Dette/EBITDA', 'N/A'))
    c3.metric("Score Value", row.get('SCORE VALUE', 'N/A'))
    c4.metric("Dividende %", row.get('Dividende %', 'N/A'))
    st.table(row) # Affiche toutes les colonnes du CSV pour cette ligne
