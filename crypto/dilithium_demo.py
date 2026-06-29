# crypto/dilithium_demo.py

try:
    from oqs import Signature
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False


# Démo de Dilithium — signature post-quantique (NIST ML-DSA).
def dilithium_demo() -> dict:
    if not OQS_AVAILABLE:
        return {
            "algo": "Dilithium3",
            "error": "liboqs-python non disponible (pip install liboqs-python)",
            "valid": False,
        }

    sig_name = "Dilithium3"
    sig = Signature(sig_name)

    public_key = sig.generate_keypair()
    message = b"Qsentinel - test de signature post-quantique"
    signature = sig.sign(message)
    is_valid = sig.verify(message, signature, public_key)

    return {
        "algo": sig_name,
        "public_key_size": len(public_key),
        "signature_size": len(signature),
        "message_size": len(message),
        "valid": is_valid,
    }
