# WhatAPlant 🌿

Application PWA d'identification et d'analyse intelligente des plantes par photo.

---

## Architecture globale

```
Photo utilisateur
      │
      ▼
[Frontend PWA]  ←─── HTML / CSS / JavaScript (Scanner, Historique, Dashboard)
      │
      ▼  HTTP POST /api/scan
[Backend Flask]
      ├── plant_service.py  →  OpenCV (prétraitement) + PlantNet API (identification)
      ├── ai_agent.py       →  Groq LLaMA 3.3 70B (rapport complet) + Pexels/Wikipedia
      ├── ml_predictor.py   →  Random Forest local (prédiction comestibilité)
      └── database.py       →  MySQL (stockage, historique, statistiques)
```

---

## Stack technique

| Couche | Technologie |
|---|---|
| **Frontend** | HTML5 / CSS3 / JavaScript (PWA, Service Worker) |
| **Backend** | Python 3.11 · Flask · Flask-CORS |
| **Vision** | OpenCV (CLAHE) · PlantNet API |
| **IA générative** | Groq API — LLaMA 3.3 70B |
| **ML local** | Scikit-learn — Random Forest (accuracy 96.8%) |
| **Base de données** | MySQL (pymysql) |
| **Images** | Pexels API · Wikipedia API |
| **Déploiement** | Railway (Procfile, Gunicorn) |

---

## Fonctionnalités

- 📷 Scan via caméra (mobile + desktop) ou import galerie
- 🔬 Prétraitement OpenCV : CLAHE, redimensionnement adaptatif
- 🌱 Identification PlantNet : nom scientifique, famille, score de confiance
- 🤖 Rapport IA complet : comestibilité, toxicité, médecine, impact environnemental
- 🧠 Prédiction ML locale : Random Forest entraîné sur 30 espèces (468 échantillons)
- 💬 Chat conversationnel contextuel avec l'agent IA (mémoire 6 tours)
- 📋 Historique des scans avec recherche
- 📊 Dashboard avec graphiques Chart.js (donut, ligne, barres)
- 🔌 PWA installable : manifest.json + Service Worker

---

## Module ML — Entraînement du modèle

Le modèle est développé et documenté dans `notebook/WhatAPlant_ML.ipynb`.

### Problème Machine Learning
Classification multi-classes : prédire la **comestibilité** d'une plante  
(`Oui` / `Non` / `Partiellement`) à partir de ses caractéristiques botaniques.

### Données
- **Données réelles** : scans stockés en MySQL via l'application
- **Données synthétiques** : 30 espèces × 15 échantillons = 450 entrées  
  (basées sur des données botaniques réelles d'Afrique de l'Ouest)

### Features utilisées
| Feature | Description |
|---|---|
| `confidence` | Score de confiance PlantNet (%) |
| `family_enc` | Famille botanique (encodée) |
| `medicinal_enc` | Propriété médicinale |
| `toxic_enc` | Toxicité |
| `invasive_enc` | Caractère invasif |
| `confidence_vs_family` | Confiance relative à la famille |

### Résultats

| Modèle | Accuracy | F1 Score |
|---|---|---|
| Logistic Regression | ~82% | ~81% |
| SVM | ~87% | ~86% |
| Gradient Boosting | ~92% | ~91% |
| **Random Forest** ✅ | **96.8%** | **97.0%** |

**Meilleurs hyperparamètres** (GridSearchCV 5-fold) :  
`n_estimators=50, max_depth=10, min_samples_split=2`

### Intégration dans l'application
Le modèle entraîné (`notebook/whataPlant_model.pkl`) est chargé au démarrage du backend via `ml_predictor.py`. Chaque scan retourne désormais :

```json
{
  "ml_prediction": "Oui",
  "ml_confidence": 0.94,
  "ml_probabilities": { "Non": 0.03, "Oui": 0.94, "Partiellement": 0.03 },
  "ml_available": true
}
```

Endpoint de statut : `GET /api/ml/status`

---

## Installation locale

### 1. Clés API

```bash
# Remplir PLANTNET_API_KEY et GROQ_API_KEY dans backend/.env
# PlantNet : https://my.plantnet.org/
# Groq     : https://console.groq.com/
```

### 2. Dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 3. Modèle ML (optionnel — déjà généré)

```bash
cd notebook
jupyter notebook WhatAPlant_ML.ipynb
# Exécuter toutes les cellules → génère whataPlant_model.pkl
```

### 4. Démarrer le backend

```bash
cd backend
python app.py
# Serveur sur http://localhost:8080
```

---

## Structure du projet

```
whataPlant/
├── backend/
│   ├── app.py              # Serveur Flask + routes API
│   ├── ai_agent.py         # Agent IA Groq (analyse + chat)
│   ├── ml_predictor.py     # Prédiction ML locale (Random Forest)
│   ├── plant_service.py    # PlantNet API + prétraitement OpenCV
│   ├── database.py         # MySQL — CRUD + statistiques
│   ├── setup_db.py         # Initialisation base de données
│   └── requirements.txt
├── frontend/
│   ├── index.html          # Application PWA mono-page
│   ├── js/
│   │   ├── app.js          # Navigation + utilitaires
│   │   ├── scanner.js      # Scan caméra/galerie + résultats
│   │   ├── history.js      # Historique des scans
│   │   └── dashboard.js    # Graphiques Chart.js
│   ├── css/style.css
│   ├── manifest.json       # Config PWA
│   └── sw.js               # Service Worker (cache offline)
├── notebook/
│   ├── WhatAPlant_ML.ipynb         # Notebook ML complet (10 sections)
│   ├── WhatAPlant_ML_executed.ipynb # Notebook avec toutes les sorties
│   ├── whataPlant_model.pkl        # Modèle Random Forest entraîné
│   ├── model_metrics.json          # Métriques finales
│   └── *.png                       # Graphiques (EDA, matrices, features)
├── Procfile                # Déploiement Railway/Heroku
└── README.md
```

---

## API REST

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/scan` | Analyser une plante (image) |
| `GET` | `/api/history` | Liste de tous les scans |
| `GET` | `/api/scan/<id>` | Détail d'un scan |
| `POST` | `/api/chat` | Chat avec l'agent IA |
| `GET` | `/api/dashboard` | Statistiques et données graphiques |
| `GET` | `/api/ml/status` | Statut du modèle ML local |
| `GET` | `/api/image/<filename>` | Servir une image uploadée |

---

## Déploiement Railway

```bash
# Variables d'environnement à configurer sur Railway :
PLANTNET_API_KEY=...
GROQ_API_KEY=...
PEXELS_API_KEY=...
MYSQL_URL=...   # fourni automatiquement par Railway MySQL plugin
```
