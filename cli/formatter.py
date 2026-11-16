# cli/formatter.py

import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from typing import Dict, List, Any, Optional
from asciichartpy import plot
import asciichartpy
import numpy as np

# --- Couleurs et styles ---
COLORS = {
    "safe": "green",
    "warning": "orange1",
    "danger": "red",
    "info": "blue",
    "title": "bold cyan",
    "header": "bold white on blue",
}

# --- Emojis ---
EMOJIS = {
    "safe": "✅",
    "warning": "⚠️",
    "danger": "❌",
    "info": "ℹ️",
    "quantum": "🔮",
    "classical": "💻",
    "pqc": "🔒",
    "time": "⏳",
}

# --- Seuils et classifications ---
FAST_THRESHOLD_S = 1.0

# Préfixes des types de clé vulnérables à Shor (le scanner renvoie par ex. "ECPublicKey").
QUANTUM_VULNERABLE_KEY_ALGOS = ("RSA", "EC", "ED", "DH", "DSA")

# Versions de protocole considérées comme dépréciées (format normalisé "tls.1.0").
DEPRECATED_TLS = {"ssl.2.0", "ssl.3.0", "tls.1.0", "tls.1.1"}

BENCH_TYPES = {
    "bsgs": "Classique",
    "rsa": "Classique",
    "grover": "Quantique",
    "shor": "Quantique",
    "kyber": "PQC",
    "dilithium": "PQC",
}

# OID de signature de certificat -> nom lisible.
CERT_SIG_NAMES = {
    "1.2.840.10045.4.3.2": "ECDSA-SHA256",
    "1.2.840.10045.4.3.3": "ECDSA-SHA384",
    "1.2.840.10045.4.3.4": "ECDSA-SHA512",
    "1.2.840.113549.1.1.11": "RSA-SHA256",
    "1.2.840.113549.1.1.12": "RSA-SHA384",
    "1.2.840.113549.1.1.13": "RSA-SHA512",
}

console = Console()


# --- Fonctions d'affichage de base ---
def print_title(title: str) -> None:
    """Affiche un titre avec un style spécial."""
    console.print(f"\n[bold cyan]{EMOJIS['info']} {title}[/bold cyan]")

def print_section(title: str) -> None:
    """Affiche une section avec une ligne de séparation."""
    console.print(f"\n[bold white on blue]{title}[/bold white on blue]")

def print_error(message: str) -> None:
    """Affiche une erreur en rouge."""
    console.print(f"[{COLORS['danger']}]{EMOJIS['danger']} {message}[/{COLORS['danger']}]")

def print_success(message: str) -> None:
    """Affiche un succès en vert."""
    console.print(f"[{COLORS['safe']}]{EMOJIS['safe']} {message}[/{COLORS['safe']}]")

def print_warning(message: str) -> None:
    """Affiche un avertissement en orange."""
    console.print(f"[{COLORS['warning']}]{EMOJIS['warning']} {message}[/{COLORS['warning']}]")


# --- Fonctions utilitaires ---

# Retourne True si le type de clé (ex. "ECPublicKey", "RSA") est vulnérable à Shor.
def _is_quantum_vulnerable_key(key_algo: str) -> bool:
    name = str(key_algo).upper()
    return any(name.startswith(prefix) for prefix in QUANTUM_VULNERABLE_KEY_ALGOS)


# Ajoute une ligne listant jusqu'à max_items éléments (sans doublons).
def _add_list_row(table: Table, label: str, items: List[str], max_items: int = 5) -> None:
    items = list(dict.fromkeys(items or []))
    if not items:
        table.add_row(label, "Aucun", EMOJIS["danger"])
        return
    text = ", ".join(items[:max_items])
    if len(items) > max_items:
        text += f" (+{len(items) - max_items} autres)"
    table.add_row(label, text, EMOJIS["info"])


# --- Fonctions de formatage des résultats ---

# Affiche les résultats du scan TLS dans un tableau.
def format_tls_results(tls: Dict[str, Any]) -> None:
    if not tls:
        print_error("Aucun résultat TLS disponible.")
        return

    table = Table(
        title="[bold]Configuration TLS[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Propriété", style="cyan", width=20)
    table.add_column("Valeur", style="white", width=40)
    table.add_column("Statut", justify="center", width=10)

    host = tls.get("host", "Inconnu")
    port = tls.get("port", 0)
    table.add_row("Hôte", f"{host}:{port}", EMOJIS["info"])

    tls_versions = tls.get("tls_versions", [])
    versions = {v.lower().replace(" ", ".") for v in tls_versions}  # "TLS 1.3" -> "tls.1.3"
    if versions & DEPRECATED_TLS:
        versions_status = EMOJIS["warning"]
    elif "tls.1.3" in versions:
        versions_status = EMOJIS["safe"]
    else:
        versions_status = EMOJIS["warning"]
    table.add_row(
        "Versions TLS",
        ", ".join(tls_versions) if tls_versions else "Aucune",
        versions_status,
    )

    key_algo = tls.get("key_algorithm", "Inconnu")
    key_size = tls.get("key_size", 0)
    status = EMOJIS["danger"] if _is_quantum_vulnerable_key(key_algo) else EMOJIS["safe"]
    table.add_row("Algorithme de clé", f"{key_algo} ({key_size} bits)", status)

    cert_sig = tls.get("cert_signature", "Inconnu")
    table.add_row("Signature du certificat", CERT_SIG_NAMES.get(cert_sig, cert_sig), EMOJIS["info"])

    _add_list_row(table, "Cipher Suites", tls.get("cipher_suites", []))

    quantum_vuln = tls.get("quantum_vulnerable", [])
    if quantum_vuln:
        vuln_str = ", ".join([v["algo"] for v in quantum_vuln])
        table.add_row(
            "Vulnérabilités quantiques",
            vuln_str,
            f"[{COLORS['danger']}]{EMOJIS['danger']} Vulnérable[/{COLORS['danger']}]",
        )
    else:
        table.add_row(
            "Vulnérabilités quantiques",
            "Aucune",
            f"[{COLORS['safe']}]{EMOJIS['safe']} Sécurisé[/{COLORS['safe']}]",
        )

    console.print(table)

def format_ssh_results(ssh: Dict[str, Any]) -> None:
    """Affiche les résultats du scan SSH dans un tableau."""
    if not ssh:
        print_error("Aucun résultat SSH disponible.")
        return

    table = Table(
        title="[bold]Configuration SSH[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Propriété", style="cyan", width=20)
    table.add_column("Valeur", style="white", width=40)
    table.add_column("Statut", justify="center", width=10)

    host = ssh.get("host", "Inconnu")
    port = ssh.get("port", 0)
    table.add_row("Hôte", f"{host}:{port}", EMOJIS["info"])

    ssh_version = ssh.get("ssh_version", "Inconnu")
    table.add_row("Version SSH", ssh_version, EMOJIS["info"])

    _add_list_row(table, "Algorithmes de clé", ssh.get("host_key_algorithms", []))
    _add_list_row(table, "Algorithmes de chiffrement", ssh.get("encryption_algorithms", []))
    _add_list_row(table, "Algorithmes MAC", ssh.get("mac_algorithms", []))
    _add_list_row(table, "Algorithmes KEX", ssh.get("kex_algorithms", []))

    quantum_vuln = ssh.get("quantum_vulnerable", [])
    if quantum_vuln:
        vuln_str = ", ".join([v["algo"] for v in quantum_vuln])
        table.add_row(
            "Vulnérabilités quantiques",
            vuln_str,
            f"[{COLORS['danger']}]{EMOJIS['danger']} Vulnérable[/{COLORS['danger']}]",
        )
    else:
        table.add_row(
            "Vulnérabilités quantiques",
            "Aucune",
            f"[{COLORS['safe']}]{EMOJIS['safe']} Sécurisé[/{COLORS['safe']}]",
        )

    console.print(table)


# Affiche les temps de cassage classique dans un tableau.
def format_classical_time(classical: Dict[str, Any]) -> None:
    if not classical:
        print_error("Aucune estimation classique disponible.")
        return

    has_data = False
    for algo, data in classical.items():
        if isinstance(data, dict) and data.get("algo"):
            has_data = True
            break

    if not has_data:
        print_error("Aucune estimation classique valide disponible.")
        return

    table = Table(
        title="[bold]Temps de cassage classique[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Algorithme", style="cyan", width=15)
    table.add_column("Taille de clé (bits)", justify="center", width=20)
    table.add_column("Opérations estimées", justify="right", width=25)
    table.add_column("Temps estimé", justify="center", width=20)

    for algo, data in classical.items():
        if isinstance(data, dict):
            table.add_row(
                data.get("algo", "Inconnu"),
                str(data.get("key_size", 0)),
                data.get("ops_estimees", "N/A"),
                data.get("temps_classique", "N/A"),
            )

    console.print(table)


# Affiche les temps de cassage quantique dans un tableau.
def format_quantum_time(quantum: Dict[str, Any]) -> None:
    if not quantum:
        print_error("Aucune estimation quantique disponible.")
        return

    table = Table(
        title="[bold]Temps de cassage quantique[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Algorithme", style="cyan", width=15)
    table.add_column("Impact", justify="center", width=30)
    table.add_column("Temps estimé", justify="center", width=20)

    grover_impact = quantum.get("grover_impact", {})
    if isinstance(grover_impact, dict) and grover_impact:
        for key, value in grover_impact.items():
            status = (
                f"[{COLORS['danger']}]{EMOJIS['danger']}[/{COLORS['danger']}]"
                if "cassable" in str(value)
                else f"[{COLORS['safe']}]{EMOJIS['safe']}[/{COLORS['safe']}]"
            )
            table.add_row("Grover", f"{key}: {value}", status)
    else:
        table.add_row("Grover", "Aucun impact détecté", "[white]N/A[/white]")

    shor_estimate = quantum.get("shor_estimate", {})
    if isinstance(shor_estimate, dict) and shor_estimate:
        table.add_row(
            "Shor",
            f"{shor_estimate.get('algo', 'Inconnu')} {shor_estimate.get('key_size', 0)} bits",
            shor_estimate.get("time_readable", "N/A"),
        )
    else:
        table.add_row("Shor", "Aucune estimation disponible", "[white]N/A[/white]")

    console.print(table)


# Affiche les recommandations dans un tableau.
def format_recommendations(recommendations: Dict[str, Any]) -> None:
    if not recommendations:
        print_warning("Aucune recommandation disponible.")
        return

    table = Table(
        title="[bold]Recommandations Post-Quantiques[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Type", style="cyan", width=15)
    table.add_column("Actuel", justify="center", width=20)
    table.add_column("Recommandation", justify="center", width=25)
    table.add_column("Raison", width=30)

    for category, recs in recommendations.items():
        for rec in recs:
            table.add_row(
                category.capitalize(),
                rec.get("current", "N/A"),
                rec.get("recommendation", "N/A"),
                rec.get("reason", "N/A"),
            )

    console.print(table)


# Affiche le score de robustesse avec une barre de couleur.
def format_score(score: int) -> None:
    score = max(0, min(100, int(score)))

    if score >= 80:
        color = COLORS["safe"]
        emoji = EMOJIS["safe"]
        status = "Excellente robustesse"
    elif score >= 50:
        color = COLORS["warning"]
        emoji = EMOJIS["warning"]
        status = "Robustesse moyenne"
    else:
        color = COLORS["danger"]
        emoji = EMOJIS["danger"]
        status = "Faible robustesse"

    score_bar = f"[{color}]{'█' * (score // 2)}[/{color}][white]{'█' * (50 - score // 2)}[/white]"
    console.print(
        Panel(
            f"[bold]{emoji} Score de robustesse: {score}/100[/bold]\n"
            f"[white]{status}[/white]\n\n"
            f"{score_bar} {score}%",
            title="[bold]Score Global[/bold]",
            border_style=color,
        )
    )


# Affiche les résultats des benchmarks dans un tableau.
def format_benchmark_results(benchmarks: Dict[str, Any]) -> None:
    if not benchmarks:
        print_warning("Aucun benchmark disponible.")
        return

    table = Table(
        title="[bold]Résultats des Benchmarks[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Algorithme", style="cyan", width=15)
    table.add_column("Type", justify="center", width=10)
    table.add_column("Temps (s)", justify="right", width=10)
    table.add_column("Opérations", justify="right", width=15)
    table.add_column("Statut", justify="center", width=10)

    for name, data in benchmarks.items():
        if not isinstance(data, dict):
            continue

        algo_type = data.get("type") or BENCH_TYPES.get(name.lower(), "Autre")
        time = data.get("time_seconds", "N/A")
        ops = data.get("ops", data.get("n_iterations", "N/A"))

        if isinstance(time, (int, float)):
            time_str = f"{time:.4f}"
            status = (
                f"[{COLORS['safe']}]{EMOJIS['safe']} Rapide[/{COLORS['safe']}]"
                if time < FAST_THRESHOLD_S
                else f"[{COLORS['warning']}]{EMOJIS['warning']} Lent[/{COLORS['warning']}]"
            )
        else:
            time_str = str(time)
            status = "[white]N/A[/white]"

        table.add_row(
            name.upper(),
            algo_type,
            time_str,
            str(ops),
            status,
        )

    console.print(table)


# Unités de temps (les plus grandes d'abord, "milliard" doit passer avant "année")
_TIME_UNITS = [
    (r"milliards?", 3.15e16),
    (r"millions?", 3.15e13),
    (r"\bans?\b|ann[ée]es?", 3.15e7),
    (r"jours?", 86400),
    (r"heures?", 3600),
    (r"minutes?", 60),
    (r"secondes?", 1),
]


# Convertit une chaîne de temps en secondes. Retourne None si non exploitable.
def time_to_seconds(time_str: str) -> Optional[float]:
    if not time_str or time_str == "N/A":
        return None
    s = time_str.lower().strip()
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?(?:e[+-]?\d+)?", s)
    if not m:
        return None
    value = float(m.group().replace(",", "."))
    for pattern, factor in _TIME_UNITS:
        if re.search(pattern, s):
            return value * factor
    return value  # nombre brut, supposé en secondes


# Calcule le rapport classique / quantique. Retourne None si impossible.
def compute_speedup(classical_sec: Optional[float], quantum_sec: Optional[float]) -> Optional[float]:
    if not classical_sec or not quantum_sec or quantum_sec <= 0:
        return None
    return classical_sec / quantum_sec


# Choisit l'estimation classique à comparer : la clé "classique" si son temps est exploitable,
# sinon la première entrée dont le temps est exploitable.
def _pick_classical(classical: Dict[str, Any]) -> Dict[str, Any]:
    candidates = []
    preferred = classical.get("classique")
    if isinstance(preferred, dict):
        candidates.append(preferred)
    candidates += [
        d for k, d in classical.items()
        if k != "classique" and isinstance(d, dict) and d.get("algo")
    ]
    for entry in candidates:
        if time_to_seconds(entry.get("temps_classique", "N/A")) is not None:
            return entry
    return candidates[0] if candidates else {}


# Affiche une comparaison complète (tableau + graphique ASCII) entre les temps de cassage classique et quantique.
def format_comparison(classical: Dict[str, Any], quantum: Dict[str, Any]) -> None:
    if not classical or not quantum:
        print_warning("Impossible de comparer : données manquantes.")
        return

    c = _pick_classical(classical)
    q = quantum.get("shor_estimate", {})

    classical_algo = c.get("algo", "Inconnu")
    classical_time_str = c.get("temps_classique", "N/A")
    quantum_time_str = q.get("time_readable", "N/A")

    classical_sec = time_to_seconds(classical_time_str)
    quantum_sec = time_to_seconds(quantum_time_str)
    speedup = compute_speedup(classical_sec, quantum_sec)

    speedup_cell = (
        f"[{COLORS['info']}]{EMOJIS['time']} ~{speedup:,.0f}x plus rapide[/{COLORS['info']}]"
        if speedup
        else "[white]N/A[/white]"
    )

    # 1. Tableau de comparaison
    table = Table(
        title="[bold]Comparaison Classique vs Quantique[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white on blue",
    )

    table.add_column("Critère", style="cyan", width=20)
    table.add_column(f"{EMOJIS['classical']} Classique", justify="center", width=30)
    table.add_column(f"{EMOJIS['quantum']} Quantique", justify="center", width=30)
    table.add_column("Accélération", justify="center", width=20)

    table.add_row("Algorithme", classical_algo, q.get("algo", "Inconnu"), "-")
    table.add_row(
        "Taille de clé",
        f"{c.get('key_size', 0)} bits",
        f"{q.get('key_size', 0)} bits",
        "-",
    )
    table.add_row("Temps estimé", classical_time_str, quantum_time_str, speedup_cell)
    console.print(table)

    # 2. Graphique ASCII avec asciichartpy
    if classical_sec and quantum_sec:
        data = [
            [np.log10(classical_sec)] * 2,
            [np.log10(quantum_sec)] * 2,
        ]
        config = {
            "height": 10,
            "colors": [asciichartpy.red, asciichartpy.green],
        }

        console.print(f"\n[bold]📈 Comparaison {classical_algo} (échelle log10)[/bold]")
        console.print(plot(data, config))
        console.print(
            f"[red]Classique:[/red] {classical_time_str} | "
            f"[green]Quantique:[/green] {quantum_time_str}"
        )
        if speedup:
            console.print(f"[bold]Accélération:[/bold] [cyan]{speedup:,.0f}x plus rapide[/cyan]")
    else:
        print_warning("Graphique impossible : temps non exploitables.")


# Affiche un graphique ASCII des résultats des benchmarks.
def plot_benchmark_results(benchmarks: Dict[str, Any]) -> None:
    if not benchmarks:
        print_warning("Aucun benchmark disponible pour le graphique.")
        return

    labels = []
    times = []
    for name, data in benchmarks.items():
        if not isinstance(data, dict):
            continue
        time_sec = data.get("time_seconds", 0)
        if isinstance(time_sec, (int, float)) and time_sec > 0:
            labels.append(name.upper())
            times.append(np.log10(time_sec))

    if not times:
        print_warning("Aucun temps valide pour le graphique.")
        return

    data = [times]
    config = {
        "height": 10,
        "colors": [asciichartpy.cyan],
    }
    console.print("\n[bold]📊 Temps d'exécution des benchmarks (échelle log10)[/bold]")
    console.print(plot(data, config))


# Affiche un résumé complet des résultats.
def print_summary(results: Dict[str, Any]) -> None:
    console.print("\n" + "=" * 80)
    print_title("🔍 Rapport Qsentinel - Résumé")
    console.print("=" * 80 + "\n")

    # 1. Configuration TLS
    tls = results.get("tls", {})
    if tls:
        print_section("🌐 Configuration TLS")
        format_tls_results(tls)

    # 2. Configuration SSH
    ssh = results.get("ssh", {})
    if ssh:
        print_section("🔌 Configuration SSH")
        format_ssh_results(ssh)

    # 3. Temps de cassage classique
    classical = results.get("classical", {})
    if classical:
        print_section(f"{EMOJIS['classical']} Temps de cassage classique")
        format_classical_time(classical)

    # 4. Temps de cassage quantique
    quantum = results.get("quantum", {})
    if quantum:
        print_section(f"{EMOJIS['quantum']} Temps de cassage quantique")
        format_quantum_time(quantum)

    # 5. Comparaison
    if classical and quantum:
        print_section("⚖️ Comparaison Classique vs Quantique")
        format_comparison(classical, quantum)

    # 6. Recommandations
    recommendations = results.get("recommendations", {})
    if recommendations:
        print_section(f"{EMOJIS['pqc']} Recommandations Post-Quantiques")
        format_recommendations(recommendations)

    # 7. Benchmarks
    benchmarks = results.get("benchmarks", {})
    if benchmarks:
        print_section("⚡ Résultats des Benchmarks")
        format_benchmark_results(benchmarks)
        plot_benchmark_results(benchmarks)

    # 8. Score (un score de 0 doit aussi s'afficher)
    score = results.get("score")
    if score is not None:
        print_section("📊 Score de Robustesse")
        format_score(score)

    console.print("\n" + "=" * 80 + "\n")
