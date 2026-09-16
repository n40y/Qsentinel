# scanner/__init__.py

from .tls_scanner import scan_tls
from .ssh_scanner import scan_ssh


def scan_target(host: str, port: int = 443, verbose: bool = False) -> dict:
    """
    Point d'entrée du module scanner. Retourne les résultats de l'audit.
    """

    results = {
        "host": host,
        "port": port,
        "tls": None,
        "ssh": None,
    }
    
    if port == 22:
        results["ssh"] = scan_ssh(host, verbose)
    else:
        # tout port non-SSH est traité comme TLS/HTTPS (443, 8443, ou un port
        # custom comme ceux utilisés par badssl.com pour ses tests spécifiques)
        results["tls"] = scan_tls(host, port, verbose)
        
    return results