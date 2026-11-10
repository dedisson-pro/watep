"""Test rapide de l'agent IA avec la nouvelle clé Groq."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from ai_agent import analyze_plant, chat_with_agent

errors = []

# ── Test 1 : Analyse complète ────────────────────────────────
print("Test 1 : analyze_plant (Moringa oleifera)...", end=" ")
try:
    result = analyze_plant({
        "scientific_name": "Moringa oleifera",
        "common_name": "Moringa",
        "family": "Moringaceae",
        "confidence": 91.5
    })
    if result.get("error"):
        print(f"ECHEC — {result['error']}")
        errors.append(result["error"])
    else:
        print("OK")
        print(f"  is_edible   : {result.get('is_edible')}")
        print(f"  is_medicinal: {result.get('is_medicinal')}")
        print(f"  is_toxic    : {result.get('is_toxic')}")
        print(f"  summary     : {str(result.get('summary',''))[:90]}")
except Exception as e:
    print(f"ECHEC — {e}")
    errors.append(str(e))

# ── Test 2 : Plante toxique ──────────────────────────────────
print("\nTest 2 : analyze_plant (Datura stramonium)...", end=" ")
try:
    result2 = analyze_plant({
        "scientific_name": "Datura stramonium",
        "common_name": "Datura",
        "family": "Solanaceae",
        "confidence": 65.0
    })
    if result2.get("error"):
        print(f"ECHEC — {result2['error']}")
        errors.append(result2["error"])
    else:
        print("OK")
        print(f"  is_edible   : {result2.get('is_edible')}")
        print(f"  is_toxic    : {result2.get('is_toxic')}")
except Exception as e:
    print(f"ECHEC — {e}")
    errors.append(str(e))

# ── Test 3 : Chat agent ──────────────────────────────────────
print("\nTest 3 : chat_with_agent...", end=" ")
try:
    ctx = {
        "scientific_name": "Moringa oleifera",
        "common_name": "Moringa",
        "ai_report": "{}"
    }
    chat = chat_with_agent(ctx, "Comment preparer une sauce avec le Moringa ?", [])
    reply = chat.get("reply", "")
    if not reply or "Erreur" in reply:
        print(f"ECHEC — {reply}")
        errors.append(reply)
    else:
        print("OK")
        print(f"  reply : {reply[:100]}")
except Exception as e:
    print(f"ECHEC — {e}")
    errors.append(str(e))

# ── Résultat ─────────────────────────────────────────────────
print()
print("=" * 50)
if errors:
    print(f"ECHECS ({len(errors)}) :")
    for e in errors:
        print(f"  - {e[:120]}")
    sys.exit(1)
else:
    print("TOUS LES TESTS PASSES OK")
    sys.exit(0)
