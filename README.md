# Système de Commande Vocale pour Robot (Speech-to-Intent)

Ce projet implémente un système complet de compréhension de la parole pour le contrôle de robots. Il convertit les commandes vocales en intentions exploitables par un robot en utilisant des modèles d'apprentissage profond de pointe.

## 🚀 Fonctionnalités

- **Reconnaissance Vocale (ASR)** : Utilise un modèle Wav2Vec2 affiné pour transcrire la parole en texte.
- **Classification d'Intention** : Utilise un modèle DistilBERT pour classifier le texte transcrit en commandes d'intention spécifiques pour le robot.
- **Interface Web** : Une application Web Flask pour interagir avec le système, enregistrer des commandes vocales et visualiser les résultats.
- **Pipeline d'Entraînement** : Un notebook Jupyter complet pour l'entraînement et l'évaluation des modèles.

## 📂 Structure du Projet

```
PROJET_ROPOTIQUE/
├── robot_voice_dataset/    # Données vocales et modèles entraînés
│   ├── audio/              # Fichiers audio du dataset
│   └── models/             # Modèles sauvegardés (ASR et Intent)
├── web_app/                # Application Web Flask
│   ├── app.py              # Point d'entrée de l'application
│   ├── static/             # Fichiers statiques (JS, CSS)
│   └── templates/          # Templates HTML
├── speech_to_intent.ipynb  # Notebook d'entraînement et d'analyse
└── metadata.py             # Script de gestion des métadonnées
```

## 🛠️ Prérequis

- Python 3.8+
- PyTorch
- Hugging Face Transformers
- Flask
- Librosa
- Autres dépendances listées dans `web_app/requirements.txt`

## 📦 Installation

1. Clonez ce dépôt :
   ```bash
   git clone <votre-url-repo>
   cd PROJET_ROPOTIQUE
   ```

2. Installez les dépendances (recommandé dans un environnement virtuel) :
   ```bash
   pip install -r web_app/requirements.txt
   ```

   *Note : Assurez-vous d'avoir installé les outils nécessaires pour le traitement audio (comme ffmpeg) sur votre système.*

## ▶️ Utilisation

### Application Web

Pour lancer l'interface de contrôle :

1. Naviguez vers le dossier de l'application web :
   ```bash
   cd web_app
   ```

2. Lancez le serveur Flask :
   ```bash
   python app.py
   ```

3. Ouvrez votre navigateur à l'adresse indiquée (généralement `http://127.0.0.1:5000`).

### Entraînement / Analyse

Pour réentraîner les modèles ou explorer les données :

1. Lancez Jupyter Notebook :
   ```bash
   jupyter notebook
   ```

2. Ouvrez le fichier `speech_to_intent.ipynb`.

## 🤖 Modèles

Le système repose sur deux modèles principaux situés dans `robot_voice_dataset/models/` :

1. **ASR Model** : Modèle acoustique pour la transcription (basé sur Wav2Vec2).
2. **Intent Model** : Modèle de compréhension du langage naturel (basé sur DistilBERT).

## 📝 Auteurs

- YOUSSEF RAHLI


