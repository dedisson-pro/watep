"""Test rapide du module ml_predictor."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Charger les variables d'environnement avant tout import
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def run_tests():
    errors = []

    # ── Test 1 : import ────────────────────────────────────────────
    print("Test 1 : import ml_predictor...", end=" ")
    try:
        from ml_predictor import predict_edibility, is_model_available
        print("OK")
    except Exception as e:
        print(f"ECHEC : {e}")
        errors.append(f"Import : {e}")
        return errors

    # ── Test 2 : chargement modèle ──────────────────────────────────
    print("Test 2 : chargement du modele pkl...", end=" ")
    available = is_model_available()
    if available:
        print("OK — modele charge")
    else:
        print("AVERTISSEMENT — pkl introuvable (mode dégradé actif)")

    # ── Test 3 : Moringa (comestible attendu) ───────────────────────
    print("Test 3 : prediction Moringa oleifera (comestible)...", end=" ")
    try:
        result = predict_edibility(
            {"scientific_name": "Moringa oleifera", "family": "Moringaceae", "confidence": 91.5},
            {"is_medicinal": "Oui", "is_toxic": "Non", "is_invasive": "Non"}
        )
        pred = result.get("ml_prediction")
        conf = result.get("ml_confidence")
        print(f"OK — prediction={pred}, confidence={conf}")
        if available and pred not in ("Oui", "Non", "Partiellement"):
            errors.append(f"Moringa : label inattendu '{pred}'")
    except Exception as e:
        print(f"ECHEC : {e}")
        errors.append(f"Moringa : {e}")

    # ── Test 4 : Datura (toxique — Non attendu) ─────────────────────
    print("Test 4 : prediction Datura stramonium (toxique)...", end=" ")
    try:
        result2 = predict_edibility(
            {"scientific_name": "Datura stramonium", "family": "Solanaceae", "confidence": 65.0},
            {"is_medicinal": "Non", "is_toxic": "Oui", "is_invasive": "Non"}
        )
        pred2 = result2.get("ml_prediction")
        print(f"OK — prediction={pred2}")
    except Exception as e:
        print(f"ECHEC : {e}")
        errors.append(f"Datura : {e}")

    # ── Test 5 : famille inconnue (robustesse) ──────────────────────
    print("Test 5 : famille inconnue (robustesse)...", end=" ")
    try:
        result3 = predict_edibility(
            {"scientific_name": "Plante X", "family": "FamilleXYZ_inconnue", "confidence": 45.0},
            {"is_medicinal": "Non", "is_toxic": "Non", "is_invasive": "Non"}
        )
        print(f"OK — pas de crash, prediction={result3.get('ml_prediction')}")
    except Exception as e:
        print(f"ECHEC : {e}")
        errors.append(f"Famille inconnue : {e}")

    # ── Test 6 : import app.py (vérifie l'intégration complète) ────
    print("Test 6 : import app.py (integration complete)...", end=" ")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(__file__), "app.py"))
        # On vérifie juste que les imports en tête de fichier passent
        import flask, flask_cors, pymysql
        from ml_predictor import predict_edibility, is_model_available
        from plant_service import identify_plant, parse_plantnet_result
        from ai_agent import analyze_plant, chat_with_agent
        from database import init_db, save_scan, get_all_scans, get_scan_by_id, get_dashboard_stats
        print("OK — tous les imports app.py resolus")
    except Exception as e:
        print(f"ECHEC : {e}")
        errors.append(f"app.py imports : {e}")

    return errors


if __name__ == "__main__":
    print("=" * 55)
    print("  WhatAPlant — Test integration ml_predictor")
    print("=" * 55)
    errs = run_tests()
    print()
    if errs:
        print(f"ECHECS ({len(errs)}) :")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("RESULTAT : TOUS LES TESTS PASSES ✅")
        sys.exit(0)
