import os
import re
import string
from collections import Counter
import pandas as pd
import nltk
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nltk import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Téléchargement des ressources NLTK nécessaires
nltk.download('punkt')
nltk.download('stopwords')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1EcGShIAltGZSdWB6-wpd796O_BeEICfs5ciUu3yGJJE'


def clean_text(text):
    """
    Nettoyer et prétraiter le texte.
    """
    text = text.lower()
    replacements = {
        'ã©': 'é', 'Ã ': 'à', 'Ã´': 'ô', 'Ã§': 'ç', 'Ã¨': 'è',
        'Ãª': 'ê', 'ãª': 'ê', 'ã': 'à', 'Ã®': 'î', 'Ã»': 'û',
        'Ã¹': 'ù', 'â': 'â', 'à¨': 'è'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    allowed_punctuation = string.punctuation.replace("'", "")
    text = text.translate(str.maketrans('', '', allowed_punctuation))
    text = re.sub(r'\d+', '', text)  # Supprimer les chiffres
    text = re.sub(' +', ' ', text).strip()  # Supprimer les espaces supplémentaires
    return text


def generate_ngrams(text, n):
    """
    Generer les ngrams d'un text donné en parametre
    """
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return list(ngrams(tokens, n))


def generate_ngrams_no_stopwords(text, n):
    """
    Generer les n-grams d'un text donné en parametre mais sans stopwords
    """
    stop_words = set(stopwords.words('french'))
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return list(ngrams(tokens, n))


def analyze_ngrams_frequencies(text, n):
    """
    Analyser la fréquence des n-grams et identifier les plus fréquents.
    """
    n_grams = generate_ngrams(text, n)
    return Counter(n_grams)


def document_insights(n_grams_freq, top_n=10):
    """
    Documenter les insights obtenus à partir de l'analyse n-gram.
    """
    top_ngrams = n_grams_freq.most_common(top_n)
    insights = f"Top {top_n} {len(top_ngrams[0][0])}-grams:\n"
    insights += '\n'.join([f"{' '.join(ngram)}: {freq}" for ngram, freq in top_ngrams])
    return insights


def get_credentials():
    """
    Obtenir les informations d'identification pour accéder à l'API Google Sheets.
    """
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


def get_data():
    """
    Récupérer les données de Google Sheets.
    """
    credentials = get_credentials()
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="sheet1").execute()
        return result.get("values", [])
    except HttpError as error:
        print(error)
        return None


def insert_data(df):
    """
    Insérer les données d'un DataFrame dans Google Sheets.

    """
    credentials = get_credentials()
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Convertir la DataFrame en une liste de listes
        values = [df.columns.tolist()] + df.values.tolist()

        # Définir la plage de cellules où les données doivent être insérées
        range_ = 'sheet1!A1'

        # Créer le corps de la requête
        body = {'values': values}

        # Utiliser l'API Sheets pour mettre à jour les valeurs
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"{result.get('updatedCells')} cellules mises à jour.")
    except HttpError as error:
        print(error)


def main():
    df = pd.read_csv("data.csv")
    df['texte'] = df['texte'].apply(clean_text)

    # Effectuer l'analyse n-gram
    text_data = ' '.join(df['texte'])
    n_grams_freq = analyze_ngrams_frequencies(text_data, 1)  # Exemple pour les bigrams
    insights = document_insights(n_grams_freq)
    print(insights)

    # Insérer les données dans Google Sheets
    insert_data(df)

    # Obtenir les données de Google Sheets et les afficher
    data = get_data()
    if data:
        for row in data:
            print(row)


if __name__ == '__main__':
    main()
