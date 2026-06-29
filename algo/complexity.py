# algo/complexity.py
from math import exp, log, pow

OPS_PER_SECOND_CLASSIC = 1e12  # 1 Tera ops/sec
OPS_PER_SECOND_QUANTIC = 1e6   # 1 Million ops/sec

def _seconds_to_readable(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f} secondes"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} heures"
    elif seconds < 3.15e7:
        return f"{seconds/86400:.1f} jours"
    elif seconds < 3.15e9:
        return f"{seconds/3.15e7:.1f} ans"
    else:
        return f"{seconds/3.15e9:.2e} milliards d'années"


def classic_time_breakable(key_size: int, algo: str) -> dict:
    if algo in ("RSA", "DH"):
        # GNFS : complexité sous-exponentielle, calcul en log pour éviter l'overflow
        # log2(ops) ≈ 1.923 * (key_size * ln2)^(1/3) * (log(key_size * ln2))^(2/3) / ln2
        import math
        ln2 = math.log(2)
        log_n = key_size * ln2  # ln(2^key_size)
        log2_ops = (1.923 * (log_n ** (1/3)) * (math.log(log_n) ** (2/3))) / ln2
        ops_str = f"2^{log2_ops:.1f}"
        seconds = (2 ** log2_ops) / OPS_PER_SECOND_CLASSIC if log2_ops < 200 else float('inf')
    elif algo in ("ECC", "EC"):
        log2_ops = key_size / 2
        ops_str = f"2^{log2_ops:.1f}"
        seconds = (2 ** log2_ops) / OPS_PER_SECOND_CLASSIC if log2_ops < 200 else float('inf')
    else:
        log2_ops = key_size
        ops_str = f"2^{log2_ops:.1f}"
        seconds = (2 ** log2_ops) / OPS_PER_SECOND_CLASSIC if log2_ops < 200 else float('inf')

    return {
        "algo": algo,
        "key_size": key_size,
        "ops_estimees": ops_str,
        "temps_classique": _seconds_to_readable(seconds),
    }


def quantic_time_breakable(key_size: int, algo: str) -> dict:
    if algo in ("RSA", "DH", "ECC", "EC"):
        # Shor : polynomiale en key_size
        ops = float(key_size ** 3)
    else:
        # Grover : racine carrée de l'espace de recherche
        log2_ops = key_size / 2
        ops = 2 ** log2_ops if log2_ops < 200 else float('inf')

    seconds = ops / OPS_PER_SECOND_QUANTIC

    return {
        "algo": algo,
        "key_size": key_size,
        "ops_estimees": f"{ops:.2e}",
        "temps_quantique": _seconds_to_readable(seconds),
    }
    

def estimate_classical_time(results: dict) -> dict:
    tls = results.get("tls", {})
    algo = tls.get("key_algorithm", "")
    key_size = tls.get("key_size", 0)

    if not algo or not key_size:
        return {}

    # Normaliser l'algo
    for known in ("RSA", "EC", "DSA", "DH"):
        if known in algo.upper():
            algo = known
            break

    classical = classic_time_breakable(key_size, algo)
    quantical = quantic_time_breakable(key_size, algo)

    return {
        "classique": classical,
        "quantique_estimation": quantical,  # On garde une copie pour la comparaison
        "vulnerable_quantique": algo in ("RSA", "EC", "DH", "DSA"),
    }
