# TestTechniqueEskimoz

Ce projet propose une intégration avec l'API Google Sheets pour faciliter la collaboration et la sauvegarde des résultats. Grâce à cette API, les insights générés à partir de l'analyse des n-grams sont automatiquement insérés dans une feuille Google Sheets. En plus de cela, le tableau de bord permet de nettoyer les données textuelles, d'analyser les n-grams, et de visualiser les résultats sous forme de graphiques et de nuages de mots.

## Contenu

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du Code](#structure-du-code)


## Fonctionnalités

- **Nettoyage des Données**: Remplacement des caractères spéciaux et suppression des mots inutiles.
- **Analyse des N-grams**: Génération et analyse des n-grams (groupes de n mots consécutifs) les plus fréquents.
- **Visualisation des Résultats**: Visualisation des n-grams les plus fréquents avec Plotly et création de nuages de mots.
- **Intégration avec Google Sheets**: Exportation des insights vers une feuille Google Sheets.
- **Tableau de Bord Interactif**: Utilisation de Streamlit pour créer un tableau de bord interactif permettant le filtrage et l'exploration des données.

## Installation

1. Clonez le dépôt:
    ```bash
    git clone https://github.com/votre_nom/votre_projet.git
    cd votre_projet
    ```

2. Installez les dépendances:
    ```bash
    pip install -r requirements.txt
    ```

3. Configurez vos informations d'identification Google API:
    - Téléchargez le fichier `credentials.json` depuis Google Cloud Console et placez-le dans le répertoire du projet.
    - Suivez les instructions [ici](https://developers.google.com/sheets/api/quickstart/python) pour obtenir les informations d'identification.

## Utilisation

1. Exécutez l'application Streamlit:
    ```bash
    streamlit run [path]/main.py
    ```

2. Ouvrez le navigateur et accédez à l'adresse [http://localhost:8501](http://localhost:8501).

3. Utilisez les options de filtrage sur la barre latérale pour ajuster les paramètres de l'analyse.

## Structure du Code

- `main.py`: Script principal contenant les fonctions pour nettoyer les données, analyser les n-grams, et générer les visualisations.
- `config.json`: Fichier de configuration pour les informations d'identification Google API.(Ignoré)
- `data.csv`: Fichier de données textuelles à analyser.
- `requirements.txt`: Liste des dépendances Python nécessaires pour le projet.

### Fonctions Principales

- **clean_text(text)**: Nettoie le texte en remplaçant les caractères spéciaux et en supprimant les mots inutiles.
- **generate_ngrams_no_stopwords(text, n)**: Génère les n-grams à partir du texte en excluant les stopwords.
- **analyze_ngrams_frequencies(text, n)**: Analyse la fréquence des n-grams dans le texte.
- **document_insights(ngrams_freq, top_n)**: Documente les insights des n-grams les plus fréquents.
- **get_credentials()**: Obtient les informations d'identification pour l'API Google Sheets.
- **clear_sheet()**: Vide la feuille Google Sheets avant d'insérer de nouvelles données.
- **insert_data(insights)**: Insère les insights dans Google Sheets.
- **generate_word_cloud(text)**: Génère un nuage de mots à partir du texte.
- **main(n, top_n)**: Fonction principale pour l'analyse des n-grams et la génération de visualisations.
- **run_dashboard(n)**: Fonction pour exécuter le tableau de bord Streamlit.



