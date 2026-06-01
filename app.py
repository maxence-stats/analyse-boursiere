import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.title("Analyse Boursière : TotalEnergies")

# Symbole par défaut réglé sur TotalEnergies (TTE.PA)
ticker = st.text_input("Symbole de l'action", "TTE.PA")

def plot_regression(ticker, years):
    # Télécharger les données
    data = yf.download(ticker, period=f"{years}y")
    
    # Vérification si les données existent
    if data.empty:
        st.error(f"Données non trouvées pour {ticker}. Vérifiez le symbole.")
        return
    
    # Préparer les données pour la régression
    data['Date_Ordinal'] = pd.to_datetime(data.index).map(pd.Timestamp.toordinal)
    x = data['Date_Ordinal'].values
    # Ajustement pour gérer les données multi-index de yfinance
    y = data['Close'].iloc[:, 0].values if isinstance(data['Close'], pd.DataFrame) else data['Close'].values
    
    # Calculer la régression linéaire
    slope, intercept = np.polyfit(x, y, 1)
    regression_line = slope * x + intercept
    
    # Affichage avec Streamlit
    st.subheader(f"Régression sur {years} ans")
    chart_data = pd.DataFrame({
        'Prix': y,
        'Régression': regression_line
    }, index=data.index)
    st.line_chart(chart_data)

# Affichage des deux graphiques
plot_regression(ticker, 10)
plot_regression(ticker, 20)
