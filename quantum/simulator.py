# quantum/simulator.py

from algo.complexity import quantic_time_breakable
from quantum.grover import estimate_quantum_time as grover_estimate
from quantum.grover import grover

def estimate_quantum_time(results: dict) -> dict:
    tls = results.get("tls") or {}
    algo = tls.get("key_algorithm", "")
    key_size = tls.get("key_size", 0)

    # Normaliser l'algo comme dans complexity.py
    for known in ("RSA", "EC", "DSA", "DH"):
        if known in algo.upper():
            algo = known
            break

    quantum_results = {
        "algo": algo,
        "key_size": key_size,
    }

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
    
    if algo in ["RSA", "EC", "DH", "DSA"] and key_size > 0:
        target = format(key_size % (2 ** 4), '04b')
        quantum_results["grover_demo"] = grover(target)

    return quantum_results   # ← on retourne le dict réellement construit
