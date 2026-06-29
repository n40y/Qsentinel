from math import isqrt


# Résout g^x ≡ h (mod p) par Baby-step Giant-step.
# Retourne x ou Nne si pas de solution
def bsgs(g: int, h: int, p: int) -> int | None:
    """ Complexité : O(√p) en temps et en espace. """
    
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
