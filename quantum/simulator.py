# quantum/simulator.py

from algo.complexity import quantic_time_breakable
from quantum.grover import estimate_quantum_time as grover_estimate


def estimate_quantum_time(results: dict) -> dict:
    """Estime le temps de cassage quantique pour les algorithmes détectés."""
    tls = results.get("tls", {})
    algo = tls.get("key_algorithm", "")
    key_size = tls.get("key_size", 0)

    quantum_results = {}

    # Estimation pour Grover (chiffrement symétrique)
    quantum_results.update(grover_estimate(results))

    # Estimation pour Shor (chiffrement asymétrique)
    if algo in ["RSA", "EC", "DH", "DSA"] and key_size > 0:
        shor_estimate = quantic_time_breakable(key_size, algo)
        quantum_results["shor_estimate"] = {
            "algo": algo,
            "key_size": key_size,
            "ops": shor_estimate["ops_estimees"],
            "time_readable": shor_estimate["temps_quantique"],
        }

    return quantum_results
