# report/scorer.py

"""
Calcule un score de 0 à 100 représentant la robustesse post-quantique
de la configuration auditée. Utilisé par html_report.py pour l'anneau
de score et le bandeau de couleur du rapport.
"""


def score(results: dict) -> int:
    """
    100 = configuration entièrement résistante au quantique
    0   = configuration totalement vulnérable / scan en échec

    La logique :
      - un scan en erreur ou vide -> 0
      - aucun algo vulnérable détecté -> score élevé (90)
      - chaque algo vulnérable détecté (RSA, EC, DH, DSA...) pénalise le score
      - la présence de cipher suites obsolètes (RC4, 3DES, NULL, EXPORT)
        pénalise un peu plus, car cumulée à la vulnérabilité quantique
    """
    tls = results.get("tls", {}) or {}

    if not tls or tls.get("errors"):
        return 0

    vulnerable = tls.get("quantum_vulnerable", [])
    cipher_suites = tls.get("cipher_suites", [])

    if not vulnerable:
        base_score = 90
    else:
        penalty = min(70, len(vulnerable) * 25)
        base_score = max(15, 90 - penalty)

    legacy_markers = ("RC4", "3DES", "NULL", "EXPORT", "DES_CBC")
    legacy_count = sum(
        1 for cs in cipher_suites if any(marker in cs for marker in legacy_markers)
    )
    if legacy_count > 0:
        base_score = max(5, base_score - min(20, legacy_count * 5))

    return int(base_score)
