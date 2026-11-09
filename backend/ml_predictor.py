"""
ml_predictor.py
---------------
Module d'intégration du modèle Machine Learning WhatAPlant.

Ce module charge le modèle Random Forest entraîné (whataPlant_model.pkl)
et fournit une prédiction locale de la comestibilité d'une plante,
en complément de l'analyse IA Groq.

Architecture :
  PlantNet API → plant_info → [ml_predictor] → enrichissement de scan_data
                           └→ [ai_agent]    → rapport complet Groq
"""

import os
import pickle
import logging

logger = logging.getLogger(__name__)

# Chemin vers le modèle entraîné (notebook/whataPlant_model.pkl)
_BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_BASE_DIR, "..", "notebook", "whataPlant_model.pkl")

# Artefact chargé une seule fois au démarrage (singleton)
_artifact = None


def _load_model():
    """Charge le modèle pkl en mémoire (lazy loading)."""
    global _artifact
    if _artifact is not None:
        return _artifact
    path = os.path.abspath(_MODEL_PATH)
    if not os.path.exists(path):
        logger.warning(f"Modèle ML introuvable : {path} — prédiction ML désactivée")
        return None
    try:
        with open(path, "rb") as f:
            _artifact = pickle.load(f)
        logger.info(f"✅ Modèle ML chargé depuis {path}")
        return _artifact
    except Exception as e:
        logger.error(f"Erreur chargement modèle ML : {e}")
        return None


def predict_edibility(plant_info: dict, ai_result: dict) -> dict:
    """
    Prédit la comestibilité d'une plante à partir des données PlantNet + Groq.

    Paramètres
    ----------
    plant_info : dict
        Résultat de parse_plantnet_result() — contient scientific_name, family, confidence
    ai_result : dict
        Résultat de analyze_plant() — contient is_medicinal, is_toxic, is_invasive

    Retourne
    --------
    dict avec :
        - ml_prediction     : str  — "Oui" | "Non" | "Partiellement"
        - ml_confidence     : float — probabilité de la classe prédite (0–1)
        - ml_probabilities  : dict — probabilités pour chaque classe
        - ml_available      : bool — True si le modèle est chargé
    """
    artifact = _load_model()
    if artifact is None:
        return {
            "ml_prediction":    None,
            "ml_confidence":    None,
            "ml_probabilities": {},
            "ml_available":     False
        }

    try:
        import pandas as pd

        pipeline = artifact["pipeline"]
        le_family    = artifact["label_encoders"]["family"]
        le_medicinal = artifact["label_encoders"]["medicinal"]
        le_toxic     = artifact["label_encoders"]["toxic"]
        le_invasive  = artifact["label_encoders"]["invasive"]
        le_target    = artifact["label_encoders"]["target"]

        # ── Extraire et normaliser les valeurs ─────────────────────────
        family     = plant_info.get("family", "Inconnue")
        confidence = float(plant_info.get("confidence", 50.0))
        medicinal  = _normalize_label(ai_result.get("is_medicinal", "Non"))
        toxic      = _normalize_label(ai_result.get("is_toxic",     "Non"))
        invasive   = _normalize_label(ai_result.get("is_invasive",  "Non"))

        # ── Encoder les variables catégorielles ────────────────────────
        # Pour les familles inconnues, utiliser 0 (valeur par défaut)
        try:
            fam_enc = le_family.transform([family])[0]
        except ValueError:
            fam_enc = 0

        med_enc = _safe_encode(le_medicinal, medicinal, 0)
        tox_enc = _safe_encode(le_toxic,     toxic,     0)
        inv_enc = _safe_encode(le_invasive,  invasive,  0)

        # Feature confidence_vs_family : 0 si famille inconnue
        conf_vs_fam = 0.0

        X_new = pd.DataFrame([{
            "confidence":            confidence,
            "family_enc":            fam_enc,
            "medicinal_enc":         med_enc,
            "toxic_enc":             tox_enc,
            "invasive_enc":          inv_enc,
            "confidence_vs_family":  conf_vs_fam
        }])

        pred_enc = pipeline.predict(X_new)[0]
        proba    = pipeline.predict_proba(X_new)[0]
        pred_label = le_target.inverse_transform([pred_enc])[0]

        # Capitaliser pour cohérence avec les labels de l'app
        pred_label = pred_label.capitalize()

        probabilities = {
            le_target.inverse_transform([i])[0].capitalize(): round(float(p), 3)
            for i, p in enumerate(proba)
        }

        return {
            "ml_prediction":    pred_label,
            "ml_confidence":    round(float(proba[pred_enc]), 3),
            "ml_probabilities": probabilities,
            "ml_available":     True
        }

    except Exception as e:
        logger.error(f"Erreur prédiction ML : {e}")
        return {
            "ml_prediction":    None,
            "ml_confidence":    None,
            "ml_probabilities": {},
            "ml_available":     False
        }


def _normalize_label(val: str) -> str:
    """Normalise un label Oui/Non/Partiellement."""
    if not val:
        return "Non"
    v = val.strip().capitalize()
    if v in ("Oui", "Non", "Partiellement"):
        return v
    return "Non"


def _safe_encode(encoder, value: str, default: int) -> int:
    """Encode une valeur en gérant les classes inconnues."""
    try:
        return encoder.transform([value])[0]
    except ValueError:
        return default


def is_model_available() -> bool:
    """Retourne True si le modèle ML est chargé et opérationnel."""
    return _load_model() is not None
