# report/scorer.py


# Note la robustesse cryptographique de 0 à 100.
def score(results: dict) -> int:
    score = 100
    tls = results.get("tls", {})
    classical = results.get("classical", {})
    quantum = results.get("quantum", {})


    # Pénalités pour les algorithmes vulnérables
    algo = tls.get("key_algorithm", "")
    if algo in ["RSA", "EC", "DH", "DSA"]:
        key_size = tls.get("key_size", 0)
        if key_size <= 2048:
            score -= 40  # Très vulnérable
        elif key_size <= 4096:
            score -= 20  # Vulnérable à long terme
        else:
            score -= 10  # Moins vulnérable mais pas sûr


    # Pénalités pour AES-128
    cipher_suites = tls.get("cipher_suites", [])
    if any("AES_128" in cs for cs in cipher_suites):
        score -= 20

    # Bonus pour AES-256
    if any("AES_256" in cs for cs in cipher_suites):
        score += 5

    # Bonus pour les algorithmes post-quantiques (si détectés)
    if any("Kyber" in cs or "Dilithium" in cs for cs in cipher_suites):
        score += 30

     # Score entre 0 et 100
    return max(0, min(100, score))
