# report/html_report.py

from jinja2 import Environement, FileSystemLoader
from os import path

# Génère un rapport html à partir des données obtenues
def generate_report(results: dict, output: str) -> None:
    
    env = Environment(loader=FileSystemLoader(path.dirname(__file__)))
    template = env.get_template("report_template.html")
    
     # Prépare les données pour le template
    tls = results.get("tls", {})
    classical = results.get("classical", {})
    quantum = results.get("quantum", {})
    recommendations = results.get("recommendations", {})
    score = results.get("score", 0)

    # Rend le template
    html = template.render(
        host=tls.get("host", "Inconnu"),
        port=tls.get("port", 0),
        tls_versions=tls.get("tls_versions", []),
        cipher_suites=tls.get("cipher_suites", []),
        key_algorithm=tls.get("key_algorithm", "Inconnu"),
        key_size=tls.get("key_size", 0),
        cert_signature=tls.get("cert_signature", "Inconnu"),
        classical=classical,
        quantum=quantum,
        recommendations=recommendations,
        score=score,
    )

    # Écrit le rapport
    with open(output, "w") as f:
        f.write(html)
