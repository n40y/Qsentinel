# Algorithmes vulnérables aux attaques quantiques
# True = cassable par Shor / Grover
# "partiel" = affaibli mais pas cassé

QUANTUM_VULNERABLE = {
    "RSA":      True,
    "ECC":      True,
    "EC":       True,
    "DH":       True,
    "DSA":      True,
    "AES128":   "partiel",
    "AES256":   False,
    "SHA256":   "partiel",
    "SHA384":   False,
}
