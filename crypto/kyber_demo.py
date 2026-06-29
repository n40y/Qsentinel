# crypto/kyber_demo.py

try:
    from oqs import KeyEncapsulation
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False


# Démo de Kyber — KEM post-quantique (NIST ML-KEM).
def kyber_demo() -> dict:
    if not OQS_AVAILABLE:
        return {
            "algo": "Kyber512",
            "error": "liboqs-python non disponible (pip install liboqs-python)",
            "success": False,
        }

    kem_name = "Kyber512"
    kem = KeyEncapsulation(kem_name)

    public_key = kem.generate_keypair()
    ciphertext, shared_secret_sender = kem.encap_secret(public_key)
    shared_secret_receiver = kem.decap_secret(ciphertext)

    return {
        "algo": kem_name,
        "public_key_size": len(public_key),
        "ciphertext_size": len(ciphertext),
        "shared_secret_size": len(shared_secret_sender),
        "success": shared_secret_sender == shared_secret_receiver,
    }
