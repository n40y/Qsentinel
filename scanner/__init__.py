# scanner/__init__.py

from .tls_scanner import scan_tls
from .ssh_scanner import scan_ssh


def scan_target(host: str, port: int = 443, verbose: bool = False) -> dict:
    # Point d'entrée du module scanner. Retourne les résultats de l'audit.
    
    results = {
        "host": host,
        "port": port,
        "tls":  None,
        "ssh":  None,
    }
    
    # le port 8443 est destiné à un usage spécialisé, ou pour du TLS obsolète.
    if port in (443, 8443):
        results["tls"] = scan_tls(host, port, verbose)
    
    if port == 22:
        results["ssh"] = scan_ssh(host,verbose)
    
    return results
