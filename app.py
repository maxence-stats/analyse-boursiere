import streamlit as st
import yfinance as yf

# Titre de l'application
st.title("Mon Application Boursière")

# Zone de saisie pour le symbole de l'action
ticker = st.text_input("Entrez le symbole d'une action (ex: AAPL, GOOG, TSLA)", "AAPL")

# Téléchargement des données via yfinance
data = yf.download(ticker, period="1mo")

# Affichage du graphique
st.line_chart(data['Close'])
