# crypto/kyber_demo.py

try:
    from kyber_py.ml_kem import ML_KEM_512
    KYBER_AVAILABLE = True
except ImportError:
    KYBER_AVAILABLE = False


def kyber_demo() -> dict:
    """
    Démo Kyber (ML-KEM-512, FIPS 203) — implémentation pure Python,
    zéro dépendance C/compilation. pip install kyber-py suffit.
    """
    if not KYBER_AVAILABLE:
        return {
            "algo": "ML-KEM-512 (Kyber)",
            "error": "kyber-py non installé (pip install kyber-py)",
            "success": False,
        }

    ek, dk = ML_KEM_512.keygen()
    shared_secret_sender, ciphertext = ML_KEM_512.encaps(ek)
    shared_secret_receiver = ML_KEM_512.decaps(dk, ciphertext)

    return {
        "algo": "ML-KEM-512 (Kyber)",
        "public_key_size": len(ek),
        "ciphertext_size": len(ciphertext),
        "shared_secret_size": len(shared_secret_sender),
        "success": shared_secret_sender == shared_secret_receiver,
    }
