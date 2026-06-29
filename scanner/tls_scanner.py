from sslyze.scanner.scanner import Scanner
from sslyze.scanner.models import ServerScanRequest
from sslyze.plugins.scan_commands import ScanCommand
from sslyze.server_setting import ServerNetworkLocation, ServerNetworkConfiguration
from sslyze.errors import ServerHostnameCouldNotBeResolved
from .vuln_db import QUANTUM_VULNERABLE



# Scan la configuration TLS d'un serveur et retourne un dict avec les algorithmes détectés et leur vulnérabilitée quantique.
def scan_tls(host: str, port: int=443, verbose: bool=False) -> dict:
    result = {
        "host": host, 
        "port": port,
        "tls_versions": [],
        "cipher_suites": [],
        "key_algorithm": None,
        "key_size": None,
        "cert_signature": None,
        "quantum_vulnerable": [],
        "errors": [],
    }
    
    try:
        server_location = ServerNetworkLocation(hostname=host, port=port)
        scan_request = ServerScanRequest(
            server_location=server_location,
            scan_commands={
                ScanCommand.TLS_1_0_CIPHER_SUITES,
                ScanCommand.TLS_1_1_CIPHER_SUITES,
                ScanCommand.TLS_1_2_CIPHER_SUITES,
                ScanCommand.TLS_1_3_CIPHER_SUITES,
                ScanCommand.CERTIFICATE_INFO,
            },
        )
        
        scanner = Scanner()
        scanner.queue_scans([scan_request])
        
        for scan_result in scanner.get_results():
            if scan_result.scan_status.value != "COMPLETED":
                result["errors"].append("Scan non complété")
                return result
        
            # --- Versions TLS et cipher suites ---
            for command in [
                ScanCommand.TLS_1_0_CIPHER_SUITES,
                ScanCommand.TLS_1_1_CIPHER_SUITES,
                ScanCommand.TLS_1_2_CIPHER_SUITES,
                ScanCommand.TLS_1_3_CIPHER_SUITES,
            ]:
                
                attempt = getattr(scan_result.scan_result, command.value, None)
                
                if attempt and attempt.result and attempt.result.accepted_cipher_suites:
                    version = command.value.replace("_cipher_suites", "").replace("_", ".")
                    result['tls_versions'].append(version)
                    
                    for cs in attempt.result.accepted_cipher_suites:
                        result["cipher_suites"].append(cs.cipher_suite.name)
                    if verbose:
                        print(f"  [{version}] {len(attempt.result.accepted_cipher_suites)} cipher suites acceptées")
            
            
            # -- Certificat --
            cert_attempt = getattr(scan_result.scan_result, "certificate_info", None)
            if cert_attempt and cert_attempt.result:
                cert = cert_attempt.result.certificate_deployments[0].received_certificate_chain[0]
                pub_key = cert.public_key()
                result["cert_signature"] = cert.signature_algorithm_oid.dotted_string
                result["key_algorithm"] = type(pub_key).__name__
                
                try:
                    result["key_size"] = pub_key.key_size
                except AttributeError:
                    result["key_size"] = None
                
                if verbose:
                    print(f" [CERT] {result['key_algorithm']} {result['key_size']} bits")
                    
            
            # -- Évaluation vulnérabilité quantique --
            algo = result["key_algorithm"]
            
            if algo:
                for known in QUANTUM_VULNERABLE:
                    if known.upper() in algo.upper():
                        result["quantum_vulnerable"].append({
                            "algo": known,
                            "vulnerable": QUANTUM_VULNERABLE[known],
                        })
    
    
    except ServerHostnameCouldNotBeResolved:
        result["errors"].append(f"Impossible de résoudre le host: {host}")
    except Exception as e:
        result["errors"].append(str(e))
        
    return result
