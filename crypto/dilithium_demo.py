# crypto/dilithium_demo.py

try:
    from dilithium_py.ml_dsa import ML_DSA_44
    DILITHIUM_AVAILABLE = True
except ImportError:
    DILITHIUM_AVAILABLE = False


def dilithium_demo() -> dict:
    """
    Démo Dilithium (ML-DSA-44, FIPS 204) — implémentation pure Python.
    pip install dilithium-py suffit, aucune compilation requise.
    """
    if not DILITHIUM_AVAILABLE:
        return {
            "algo": "ML-DSA-44 (Dilithium)",
            "error": "dilithium-py non installé (pip install dilithium-py)",
            "valid": False,
        }

    pk, sk = ML_DSA_44.keygen()
    message = b"Qsentinel - test de signature post-quantique"
    signature = ML_DSA_44.sign(sk, message)
    is_valid = ML_DSA_44.verify(pk, message, signature)

    return {
        "algo": "ML-DSA-44 (Dilithium)",
        "public_key_size": len(pk),
        "signature_size": len(signature),
        "message_size": len(message),
        "valid": is_valid,
    }
