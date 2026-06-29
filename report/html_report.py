# report/html_report.py

from jinja2 import Environment, FileSystemLoader
from os import path


def generate_report(results: dict, output: str) -> None:

    env = Environment(loader=FileSystemLoader(path.dirname(__file__)))
    template = env.get_template("report_template.html")

    tls = results.get("tls", {})
    classical = results.get("classical", {})
    quantum = results.get("quantum", {})
    recommendations = results.get("recommendations", {})
    score = results.get("score", 0)

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

    with open(output, "w") as f:
        f.write(html)
