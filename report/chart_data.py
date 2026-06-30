# report/chart_data.py

"""
Prépare les données issues du pipeline Qsentinel au format JSON
attendu par Chart.js. Aucune dépendance externe (pas de matplotlib) :
les graphiques sont rendus côté navigateur, l'utilisateur n'a rien à
installer en plus de jinja2.
"""
import json


def _extract_number(value) -> float:
    """
    Convertit en float et plafonne à 1e50 — au-delà, la valeur exacte
    n'a plus de sens pédagogique et casse le rendu de l'échelle log
    de Chart.js. 1e50 reste largement supérieur à toute valeur
    quantique réaliste, donc le ratio visuel reste parlant.
    """
    try:
        num = float(value)
        if num != num:  # NaN
            return 0.0
        return min(num, 1e50)
    except (TypeError, ValueError):
        return 0.0


def prepare_classical_vs_quantum(classique: dict, quantique: dict):
    """
    Construit le JSON pour le graphique en barres horizontales comparant
    le nombre d'opérations nécessaires pour casser la clé détectée,
    en classique vs en quantique (Shor).

    Attend les dicts retournés par algo/complexity.py :
        classique  = {"algo": ..., "key_size": ..., "ops_estimees": "1.2e+34", ...}
        quantique  = {"algo": ..., "key_size": ..., "ops_estimees": "1.2e+07", ...}

    Retourne None si les données sont absentes (le template masque
    alors le graphique automatiquement).
    """
    if not classique or not quantique:
        return None

    ops_classique = _extract_number(classique.get("ops_estimees"))
    ops_quantique = _extract_number(quantique.get("ops_estimees"))

    if ops_classique <= 0 and ops_quantique <= 0:
        return None

    data = {
        "labels": ["Classique", "Quantique (Shor)"],
        "datasets": [{
            "label": "Opérations nécessaires",
            "data": [ops_classique, ops_quantique],
            "backgroundColor": ["#f85149", "#39d0c8"],
            "borderRadius": 4,
        }]
    }
    return json.dumps(data)


def prepare_grover_distribution(counts: dict, target: str):
    """
    Construit le JSON pour l'histogramme des mesures de la démo Grover.

    Attend :
        counts = {"101": 780, "010": 45, ...}  (sortie de quantum/grover.py)
        target = "101"

    Met en évidence la barre correspondant à l'état cible.
    Retourne None si pas de données (template masque le graphique).
    """
    if not counts:
        return None

    states = list(counts.keys())
    values = list(counts.values())
    colors = ["#f85149" if s == target else "#39d0c8" for s in states]

    data = {
        "labels": states,
        "datasets": [{
            "label": f"Mesures (cible: {target})" if target else "Mesures",
            "data": values,
            "backgroundColor": colors,
            "borderRadius": 4,
        }]
    }
    return json.dumps(data)
