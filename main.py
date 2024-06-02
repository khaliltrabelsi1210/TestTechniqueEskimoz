import os
import re
import string
from collections import Counter

from matplotlib import pyplot as plt
from wordcloud import WordCloud
import pandas as pd

import streamlit as st
import plotly.express as px
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nltk.corpus import stopwords
import spacy



# Definir les constantes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '16569gBFxOb_Tnh4msPGE4SkWxz-VJcDEalOGQ3axODo'
RANGE_NAME = 'sheet1!A1'
STOPWORDS = set(stopwords.words('french'))

# Charger le modèle SpaCy pour le français
nlp = spacy.load("fr_core_news_sm")


# Fonction pour nettoyer le texte
def clean_text(text):
    text = text.lower()
    allowed_punctuation = string.punctuation.replace("'", "")
    text = text.translate(str.maketrans('', '', allowed_punctuation))
    text = re.sub(r'\d+', '', text)
    text = re.sub(' +', ' ', text).strip()
    return text


# Fonction pour generer les n-grams sans stopwords
def generate_ngrams_no_stopwords(text, n):
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


# Fonction pour analyser la fréquence des n-grams
def analyze_ngrams_frequencies(text, n):
    ngrams = generate_ngrams_no_stopwords(text, n)
    return Counter(ngrams)


# Fonction pour documenter les insights
def document_insights(ngrams_freq, top_n=10):
    top_ngrams = ngrams_freq.most_common(top_n)
    insights = f"Top {top_n} {len(top_ngrams[0][0])}-grams:\n"
    insights += '\n'.join([f"{' '.join(ngram)}: {freq}" for ngram, freq in top_ngrams])
    return insights


# Fonction pour obtenir les informations d'identification pour l'API Google Sheets
def get_credentials():
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('config.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
    return credentials


# Fonction pour vider la feuille Google Sheets
def clear_sheet():
    credentials = get_credentials()
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        clear_values_request_body = {}
        request = sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, body=clear_values_request_body)
        request.execute()
    except HttpError as error:
        print(f"An error occurred: {error}")


# Fonction pour inserer les insights dans Google Sheets
def insert_data(insights):
    credentials = get_credentials()
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Preparer les donnees pour l'insertion
        rows = [["N-gram", "Fréquence"]]  # Ajouter les titres des colonnes
        for line in insights.split('\n')[1:]:
            ngram, freq = line.split(': ')
            rows.append([ngram, int(freq)])

        body = {'values': rows}
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"{result.get('updatedCells')} cellules mises à jour.")
    except HttpError as error:
        print(f"An error occurred: {error}")


# Fonction pour generer un nuage de mots
def generate_word_cloud(text, stopwords):
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    return plt


# Fonction principale pour l'analyse des n-grams et la generation de visualisations
def main(n=2, top_n=10):
    df = pd.read_csv("data.csv", encoding='utf-8')
    df['texte'] = df['texte'].apply(clean_text)
    text_data = ' '.join(df['texte'])
    n_grams_freq = analyze_ngrams_frequencies(text_data, n)
    insights = document_insights(n_grams_freq, top_n)
    print(insights)
    clear_sheet()
    insert_data(insights)
    return df


# Fonction pour exécuter le tableau de bord Streamlit
# Fonction pour exécuter le tableau de bord Streamlit
def run_dashboard(n, top_n):
    st.title('Insights Dashboard')

    # Charger les données
    df = main(n, top_n)
    df['texte'] = df['texte'].apply(clean_text)

    # Sidebar filters
    st.sidebar.header('Options de Filtrage')
    stat_min = st.sidebar.slider('Valeur Minimale de la Statistique', min_value=int(df['statistique'].min()),
                                 max_value=int(df['statistique'].max()), value=int(df['statistique'].min()))

    # Filtrer les données basées sur la statistique
    filtered_df = df[df['statistique'] >= stat_min]

    # Afficher la distribution des statistiques
    st.header('Distribution des Statistiques')
    fig = px.histogram(filtered_df, x='statistique', nbins=20, title='Distribution des Statistiques')
    st.plotly_chart(fig)

    # Afficher la DataFrame similaire à celle insérée dans Google Sheets
    st.header('DataFrame des N-grams et Fréquences')
    text_data = ' '.join(filtered_df['texte'])
    n_grams_freq = analyze_ngrams_frequencies(text_data, n)
    top_ngrams = n_grams_freq.most_common(top_n)  # Correction ici
    ngrams_df = pd.DataFrame(top_ngrams, columns=['N-gram', 'Fréquence'])
    ngrams_df['N-gram'] = ngrams_df['N-gram'].apply(lambda x: ' '.join(x))
    st.write(ngrams_df)

    # Afficher l'analyse des n-grams significatifs
    st.header('Analyse des N-grams Significatifs')
    insights = document_insights(n_grams_freq, top_n)  # Correction ici

    st.subheader(f'Top {top_n} n-grams')  # Correction ici
    st.write(insights)

    # Visualisation interactive des n-grams les plus fréquents
    fig = px.bar(ngrams_df, x='N-gram', y='Fréquence',
                 title=f'Top {top_n} des N-grams les plus fréquents')  # Correction ici
    st.plotly_chart(fig)

    # Afficher le nuage de mots
    st.header('Nuage de mots')
    wordcloud = generate_word_cloud(text_data, STOPWORDS)
    st.pyplot(wordcloud)


# Exécuter les fonctions principales
if __name__ == '__main__':
    run_dashboard(2, 7)
