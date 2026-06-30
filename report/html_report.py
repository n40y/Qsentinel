# report/html_report.py

"""
Assemble les résultats du pipeline QuantumSentinel (scanner, algo,
quantum, crypto) et génère le rapport HTML final à partir du template
Jinja2 existant, en y injectant les données des graphiques Chart.js.
"""

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from .scorer import score
from .chart_data import prepare_classical_vs_quantum, prepare_grover_distribution


# Point d'entrée appelé par main.py.
def generate_report(results: dict, output: str) -> None:
    """
    results : dict produit par le pipeline (scan_target + estimate_classical_time
               + estimate_quantum_time + get_pqc_recommendation), de la forme :
               {
                   "host": ..., "port": ...,
                   "tls": {...}, "ssh": {...},
                   "classical": {"classique": {...}, "quantique": {...}, ...},
                   "quantum": {...},          # peut contenir grover_demo
                   "recommendations": {...},  # asymmetric / symmetric / hash
               }
    output  : chemin du fichier HTML à écrire (ex: "report.html")
    """
    tls = results.get("tls", {}) or {}
    classical = results.get("classical", {}) or {}
    quantum = results.get("quantum", {}) or {}
    recommendations = results.get("recommendations", {}) or {}

    pqc_score = score(results)

    # --- Données des graphiques Chart.js ---
    chart_classical_vs_quantum = prepare_classical_vs_quantum(
        classical.get("classique", {}),
        classical.get("quantique_estimation", {}),
    )

    grover_demo = quantum.get("grover_demo", {}) if isinstance(quantum, dict) else {}
    chart_grover = prepare_grover_distribution(
        grover_demo.get("counts", {}),
        grover_demo.get("target", ""),
    )

    # --- Rendu Jinja2 ---
    templates_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report_template.html")

    html = template.render(
        host=tls.get("host", results.get("host", "?")),
        port=tls.get("port", results.get("port", "?")),
        score=pqc_score,

        key_algorithm=tls.get("key_algorithm", "N/A"),
        key_size=tls.get("key_size", "N/A"),
        cert_signature=tls.get("cert_signature", "N/A"),
        tls_versions=tls.get("tls_versions", []),
        cipher_suites=tls.get("cipher_suites", []),

        classical=classical,
        quantum=quantum,
        recommendations=recommendations,

        chart_classical_vs_quantum=chart_classical_vs_quantum,
        chart_grover=chart_grover,
    )

    Path(output).write_text(html, encoding="utf-8")
