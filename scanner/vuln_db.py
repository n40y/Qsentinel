# scanner/vuln_db.py

"""
 Algorithmes vulnérables aux attaques quantiques

True = cassable par Shor / Grover
"partiel" = affaibli mais pas cassé
"""

QUANTUM_VULNERABLE = {
    "RSA":      True,
    "ECC":      True,
    "EC":       True,
    "DH":       True,
    "DSA":      True,
    "Ad25519":  "partiel",
    "AES128":   "partiel",
    "AES256":   False,
    "SHA256":   "partiel",
    "SHA384":   False,
    "SHA3":     False,
}
