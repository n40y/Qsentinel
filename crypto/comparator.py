# crypto/comparator.py


# Recommande des algorithmes post-quantiques en fonction des vulnérabilités détectées.
def get_pqc_recommendation(results: dict) -> dict:
    tls = results.get("tls", {})
    algo = tls.get("key_algorithm", "")
    key_size = tls.get("key_size", 0)
    cipher_suites = tls.get("cipher_suites", [])

    recommendations = {
        "asymmetric": [],
        "symmetric": [],
        "hash": [],
    }

    # Recommendations : 
    
    ## Sur les algo asymétriques
    if algo in ["RSA", "EC", "DH", "DSA"]:
        if key_size <= 2048:
            recommendations["asymmetric"].append({
                "current": f"{algo} {key_size} bits",
                "recommendation": "Kyber768 (KEM) + Dilithium3 (Signatures)",
                "reason": "Vulnérable à Shor. Passer à des algorithmes PQC standardisés par le NIST.",
            })
        else:
            recommendations["asymmetric"].append({
                "current": f"{algo} {key_size} bits",
                "recommendation": "Kyber1024 (KEM) + Dilithium5 (Signatures)",
                "reason": "Taille de clé élevée, mais toujours vulnérable à long terme.",
            })

    ## Sur les algo symétriques
    if any("AES_128" in cs for cs in cipher_suites):
        recommendations["symmetric"].append({
            "current": "AES-128",
            "recommendation": "AES-256",
            "reason": "AES-128 est affaibli par Grover (64 bits effectifs).",
        })

    ## Pour les hashs
    if any("SHA256" in cs for cs in cipher_suites):
        recommendations["hash"].append({
            "current": "SHA-256",
            "recommendation": "SHA-384 ou SHA-3",
            "reason": "SHA-256 est partiellement vulnérable à Grover.",
        })

    return recommendations
