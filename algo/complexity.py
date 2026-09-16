# algo/complexity.py

from math import log

OPS_PER_SECOND_CLASSIC = 1e12
OPS_PER_SECOND_QUANTIC = 1e6


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
        ln2 = log(2)
        log_n = key_size * ln2
        log2_ops = (1.923 * (log_n ** (1/3)) * (log(log_n) ** (2/3))) / ln2
    elif algo in ("ECC", "EC"):
        log2_ops = key_size / 2
    else:
        log2_ops = key_size

    if log2_ops < 990:
        ops = 2 ** log2_ops
        seconds = ops / OPS_PER_SECOND_CLASSIC
    else:
        ops = float('inf')
        seconds = float('inf')

    ops_str = f"{ops:.2e}" if ops != float('inf') else "1.00e+300"
    seconds_capped = seconds if seconds != float('inf') else 1e300

    return {
        "algo": algo,
        "key_size": key_size,
        "ops_estimees": ops_str,
        "temps_classique": _seconds_to_readable(seconds_capped),
    }


def quantic_time_breakable(key_size: int, algo: str) -> dict:
    if algo in ("RSA", "DH", "ECC", "EC"):
        ops = float(key_size ** 3)
    else:
        log2_ops = key_size / 2
        ops = 2 ** log2_ops if log2_ops < 990 else 1e300

    seconds = ops / OPS_PER_SECOND_QUANTIC

    return {
        "algo": algo,
        "key_size": key_size,
        "ops_estimees": f"{ops:.2e}",
        "temps_quantique": _seconds_to_readable(seconds),
    }


def estimate_classical_time(results: dict) -> dict:
    tls = results.get("tls") or {}
    algo = tls.get("key_algorithm", "")
    key_size = tls.get("key_size", 0)

    if not algo or not key_size:
        return {}

    for known in ("RSA", "EC", "DSA", "DH"):
        if known in algo.upper():
            algo = known
            break

    classical = classic_time_breakable(key_size, algo)
    quantical = quantic_time_breakable(key_size, algo)

    return {
        "classique": classical,
        "quantique_estimation": quantical,
        "vulnerable_quantique": algo in ("RSA", "EC", "DH", "DSA"),
    }
