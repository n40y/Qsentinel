# algo/bsgs.py

from math import isqrt
from time import time


# Résout g^x ≡ h (mod p) par Baby-step Giant-step.
# Retourne x ou Nne si pas de solution

# Complexité : O(√p) en temps et en espace.

def bsgs(g: int, h: int, p: int) -> int | None:
    m = isqrt(p) + 1
    baby, gj = {}, 1
    
    for j in range(m):
        baby[gj] = j
        gj = (gj * g) % p
    
    gm_inverse = pow(g, -m, p)
    
    giant = h
    for i in range(m):
        if giant in baby:
            x = i * m + baby[giant]
            return x % (p - 1)
        giant = (giant * gm_inverse) % p
    
    return None

# Mesure la durée d'exécution
def benchmark_bsgs(g, h, p, max_time=10):
    start = time()
    result = bsgs(g, h, p)
    elapsed = time() - start
    
    return {
        "result": result,
        "time_seconds": elapsed,
        "ops_per_second": p / elapsed if elapsed > 0 else float('inf')
    }
