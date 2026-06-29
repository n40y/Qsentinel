# crypto/kyber_demo.py

from liboqs import KeyEncapsulation


# Démo de Kyber (Kem post-quantique)
def kyber_demo():
    kem_name = "Kyber512"
    kem = KeyEncapsulation(kem_name)
    
    # Génération des clées
    public_key = kem.generate_keypair()
    ciphertext, shared_secret_sender = kem.encap_secret(public_key)
    
    # Décapsulation
    shared_secret_receiver = kem.decap_secret(ciphertext)
    
    return {
        "algo": kem_name,
        "public_key_size": len(public_key),
        "ciphertext_size": len(ciphertext),
        "shared_secret_size": len(shared_secret_sender),
        "success": shared_secret_sender == shared_secret_receiver,
    }
    
