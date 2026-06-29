# crypto/dilithium_demo.py

from liboqs import Signature


# Démo de Dilithium — signature post-quantique (NIST ML-DSA).
def dilithium_demo() -> dict:
    sig_name = "Dilithium3"
    sig = Signature(sig_name)

    # Génération des clés
    public_key = sig.generate_keypair()

    # Signature d'un message
    message = b"Qsentinel - test de signature post-quantique"
    signature = sig.sign(message)

    # Vérification
    is_valid = sig.verify(message, signature, public_key)

    return {
        "algo": sig_name,
        "public_key_size": len(public_key),
        "signature_size": len(signature),
        "message_size": len(message),
        "valid": is_valid,
    }
