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
        n = pow(2, key_size)
        ops = exp(1.923 * pow(log(n), (1/3)) * pow(log(log(n)), (2/3)))
    elif algo in ("ECC", "EC"):
        ops = pow(2, (key_size / 2))
    else:
        ops = pow(2, key_size)

    seconds = ops / OPS_PER_SECOND_CLASSIC
    return {
        "algo": algo,
        "key_size": key_size,
        "ops_estimees": f"{ops:.2e}",
        "temps_classique": _seconds_to_readable(seconds),
    }

def quantic_time_breakable(key_size: int, algo: str) -> dict:
    if algo in ("RSA", "DH", "ECC", "EC"):
        ops = pow(key_size, 3)
    else:
        ops = pow(2, (key_size / 2))

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
