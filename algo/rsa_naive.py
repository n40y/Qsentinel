# algo/rsa_naive.py

from math import isqrt, gcd, sqrt
from random import randint


# Fonction pour rechercher les nombres premiers dans 0 à racine de N
def is_prime(n) -> bool:
    if n <= 1: return False
    if n == 2: return True
    if n & 1 == 0: return False
    if n == 3: return True
    if n % 3 == 0: return False
    
    square = int(sqrt(n))
    
    for i in range(5, square + 1, 2):
        if n % i == 0:
            return False
    return True
    

# On factorise avec l'algo Rho de Pollard pour traiter les petits noombres.
def pollards_rho(n):
    if n & 1 == 0: return 2
    if n % 3 == 0: return 3
    if n % 5 == 0: return 5
    
    while True:
        c = randint(1, n - 1)
        f = lambda x: (pow(x, 2, n) + c) % n
        x, y, d = 2, 2, 1
        
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = gcd(abs(x - y), n)
            
            if d != n:
                return d


# Factorisatio de N en me servant de l'algo de Pollard's Rho pour les petits facteurs
def factorize(n):
    factors = []
    def _factorize(n):
        if n == 1:
            return
        if is_prime(n):
            factors.append(n)
            return
        
        d = pollards_rho(n)
        _factorize(d)
        _factorize(n // d)
    
    _factorize(n)
    
    return sorted(factors)


