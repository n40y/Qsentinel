# scanner/vuln_db.py


# Algorithmes vulnérables aux attaques quantiques:
# True = cassable par Shor / Grover
# "partiel" = affaibli mais pas cassé

QUANTUM_VULNERABLE = {
    # Asymétriques (vulnérables à Shor)
    "RSA": True,
    "ECC": True,
    "EC": True,
    "DH": True,
    "DSA": True,
    "Ed25519": "partiel",  # Courbes elliptiques (partiellement vulnérables)
    "Ed448": "partiel",
    "ecdsa-sha2-nistp256": True,
    "ecdsa-sha2-nistp384": True,
    "ecdsa-sha2-nistp521": True,
    "ssh-rsa": True,
    "rsa-sha2-256": True,
    "rsa-sha2-512": True,

    # Symétriques (vulnérables à Grover)
    "AES128": "partiel",
    "AES256": False,
    "3DES": True,  # Très faible, même sans quantique
    "aes128-ctr": "partiel",
    "aes128-gcm": "partiel",
    "aes256-ctr": False,
    "aes256-gcm": False,

    # Hashs (vulnérables à Grover)
    "SHA256": "partiel",
    "SHA384": False,
    "SHA512": False,
    "SHA1": True,  # Déjà cassé classiquement
    "MD5": True,   # Déjà cassé classiquement

    # Key Exchange (vulnérables à Shor)
    "diffie-hellman-group1-sha1": True,
    "diffie-hellman-group14-sha1": True,
    "diffie-hellman-group14-sha256": True,
    "diffie-hellman-group16-sha512": True,
    "diffie-hellman-group18-sha512": True,
    "ecdh-sha2-nistp256": True,
    "ecdh-sha2-nistp384": True,
    "ecdh-sha2-nistp521": True,
}
