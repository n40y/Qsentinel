from math import exp, log, pow


# 1 Tera d'opé classiques/sec
OPS_PER_SECOND_CLASSIC = pow(10, 12)
# 1 million d'opé quantiques/sec (optimiste)
OPS_PER_SECOND_QUANTIC = pow(10, 6) 

# COnverti un nombre de secondes en texte lisible.
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


# Estime le temps de cassage selon la clé et l'algo utilisé 
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

#  Estime le temps de casse quantique (Shor / Grover)
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
    

# Fonction d'entrée, appelée par main.py
def estimate_classical_time(results: dict) -> dict:
    tls = results.get("tls", {})
    algo = tls.get("key_algorithm", "")
    key_size = tls.get("key_size", 0)
    
    print(f"DEBUG algo='{algo}' key_size={key_size}")
    
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
        "quantique": quantical,
        "vulnerable_quantique": algo in ("RSA", "EC", "DH", "DSA"),
    }
    
    
