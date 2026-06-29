# scanner/ssh_scanner.py

import paramiko
from paramiko.hostkeys import HostKeys
from typing import Dict, List, Any, Optional
import socket
from .vuln_db import QUANTUM_VULNERABLE


"""
Scan la configuration SSH d'un serveur et retourne un dictionnaire avec :
    - Version SSH
    - Algorithmes de clé (host key)
    - Algorithmes de chiffrement (cipher)
    - Algorithmes de MAC (Message Authentication Code)
    - Vulnérabilités quantiques
    - Erreurs éventuelles
"""
def scan_ssh(host: str, port: int = 22, verbose: bool = False) -> Dict[str, Any]:
    result = {
        "host": host,
        "port": port,
        "ssh_version": None,
        "host_key_algorithms": [],
        "encryption_algorithms": [],
        "mac_algorithms": [],
        "kex_algorithms": [],  # Key Exchange
        "quantum_vulnerable": [],
        "errors": [],
    }

    try:
        # Connexion SSH (sans authentification, juste pour récupérer les infos)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())

        try:
            client.connect(
                hostname=host,
                port=port,
                username="test",  # On n'a pas besoin de s'authentifier
                timeout=5,
                allow_agent=False,
                look_for_keys=False,
                password=None,
            )
        except paramiko.AuthenticationException:
            # C'est normal, on ne veut pas s'authentifier
            pass
        except paramiko.SSHException as e:
            result["errors"].append(f"Erreur SSH: {str(e)}")
            return result
        except socket.timeout:
            result["errors"].append(f"Timeout lors de la connexion à {host}:{port}")
            return result
        except Exception as e:
            result["errors"].append(f"Erreur inattendue: {str(e)}")
            return result

        # Récupérer les informations de la connexion
        transport = client.get_transport()
        if transport:
            # Version SSH
            result["ssh_version"] = transport.remote_version

            # Algorithmes supportés
            if hasattr(transport, "kex_engine"):
                kex = transport.kex_engine
                if kex:
                    # Algorithmes de clé (host key)
                    if hasattr(kex, "host_key_algorithms"):
                        result["host_key_algorithms"] = list(kex.host_key_algorithms)

                    # Algorithmes de chiffrement
                    if hasattr(kex, "encryption_algorithms"):
                        result["encryption_algorithms"] = list(kex.encryption_algorithms)

                    # Algorithmes de MAC
                    if hasattr(kex, "mac_algorithms"):
                        result["mac_algorithms"] = list(kex.mac_algorithms)

                    # Algorithmes de Key Exchange
                    if hasattr(kex, "kex_algorithms"):
                        result["kex_algorithms"] = list(kex.kex_algorithms)

            # Récupérer la clé publique du serveur (host key)
            host_keys = client.get_host_keys()
            if host_keys:
                for hostname, keytypes in host_keys.items():
                    for keytype in keytypes:
                        result["host_key_algorithms"].append(keytype.name)

        # Évaluer les vulnérabilités quantiques
        for algo in result["host_key_algorithms"] + result["kex_algorithms"]:
            for known in QUANTUM_VULNERABLE:
                if known.upper() in algo.upper():
                    result["quantum_vulnerable"].append({
                        "algo": known,
                        "vulnerable": QUANTUM_VULNERABLE[known],
                        "context": "SSH",
                    })
                    break  # Éviter les doublons

        if verbose:
            print(f"  [SSH] Version: {result['ssh_version']}")
            print(f"  [SSH] Host Key Algorithms: {result['host_key_algorithms']}")
            print(f"  [SSH] Encryption Algorithms: {result['encryption_algorithms']}")
            print(f"  [SSH] MAC Algorithms: {result['mac_algorithms']}")
            print(f"  [SSH] KEX Algorithms: {result['kex_algorithms']}")

    except paramiko.SSHException as e:
        result["errors"].append(f"Erreur SSH: {str(e)}")
    except socket.error as e:
        result["errors"].append(f"Erreur de connexion: {str(e)}")
    except Exception as e:
        result["errors"].append(f"Erreur inattendue: {str(e)}")

    return result
