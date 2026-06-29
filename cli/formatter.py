# cli/formatter.py

# cli/formatter.py (lignes 1-10)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from typing import Dict, List, Any
from asciichartpy import plot
import numpy as np


console = Console()

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

# Affiche un titre avec un style spécial.
def print_title(title: str) -> None:
    console.print(f"\n[bold cyan]{EMOJIS['info']} {title}[/bold cyan]")


# Affiche une section avec une ligne de séparation.
def print_section(title: str) -> None:
    console.print(f"\n[bold white on blue]{title}[/bold white on blue]")


# Affiche une erreur en rouge.
def print_error(message: str) -> None:
    console.print(f"[{COLORS['danger']}]{EMOJIS['danger']} {message}[/{COLORS['danger']}]")


# Affiche un avertissement en vert.
def print_success(message: str) -> None:
    console.print(f"[{COLORS['safe']}]{EMOJIS['safe']} {message}[/{COLORS['safe']}]")


# Affiche un avertissement en orange.
def print_warning(message: str) -> None:
    console.print(f"[{COLORS['warning']}]{EMOJIS['warning']} {message}[/{COLORS['warning']}]")


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

    # Ajouter les colonnes
    table.add_column("Propriété", style="cyan", width=20)
    table.add_column("Valeur", style="white", width=40)
    table.add_column("Statut", justify="center", width=10)

    # Remplir le tableau
    host = tls.get("host", "Inconnu")
    port = tls.get("port", 0)
    table.add_row("Hôte", f"{host}:{port}", EMOJIS["info"])

    tls_versions = tls.get("tls_versions", [])
    table.add_row(
        "Versions TLS",
        ", ".join(tls_versions) if tls_versions else "Aucune",
        EMOJIS["safe"] if "TLS 1.3" in tls_versions else EMOJIS["warning"],
    )

    key_algo = tls.get("key_algorithm", "Inconnu")
    key_size = tls.get("key_size", 0)
    status = (
        EMOJIS["danger"]
        if key_algo in ["RSA", "EC", "DH", "DSA"]
        else EMOJIS["safe"]
    )
    table.add_row("Algorithme de clé", f"{key_algo} ({key_size} bits)", status)

    cert_sig = tls.get("cert_signature", "Inconnu")
    table.add_row("Signature du certificat", cert_sig, EMOJIS["info"])

    cipher_suites = tls.get("cipher_suites", [])
    if cipher_suites:
        # Afficher les 5 premières cipher suites
        suites_str = ", ".join(cipher_suites[:5])
        if len(cipher_suites) > 5:
            suites_str += f" (+{len(cipher_suites) - 5} autres)"
        table.add_row("Cipher Suites", suites_str, EMOJIS["info"])
    else:
        table.add_row("Cipher Suites", "Aucune", EMOJIS["danger"])

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


# Affiche les temps de cassage classique dans un tableau.
def format_classical_time(classical: Dict[str, Any]) -> None:
    if not classical:
        print_error("Aucune estimation classique disponible.")
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

    # Grover
    grover_impact = quantum.get("grover_impact", {})
    if grover_impact:
        for key, value in grover_impact.items():
            status = (
                f"[{COLORS['danger']}]{EMOJIS['danger']}[/{COLORS['danger']}]"
                if "cassable" in value
                else f"[{COLORS['safe']}]{EMOJIS['safe']}[/{COLORS['safe']}]"
            )
            table.add_row("Grover", f"{key}: {value}", status)

    # Shor
    shor_estimate = quantum.get("shor_estimate", {})
    if shor_estimate:
        table.add_row(
            "Shor",
            f"{shor_estimate.get('algo', 'Inconnu')} {shor_estimate.get('key_size', 0)} bits",
            shor_estimate.get("time_readable", "N/A"),
        )

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


# Affiche une comparaison graphique entre classique et quantique.
def format_comparison(classical: Dict[str, Any], quantum: Dict[str, Any]) -> None:
    if not classical or not quantum:
        print_warning("Impossible de comparer : données manquantes.")
        return

    # Extraire les données
    classical_algo = classical.get("classique", {}).get("algo", "Inconnu")
    classical_time = classical.get("classique", {}).get("temps_classique", "N/A")
    quantum_time = quantum.get("shor_estimate", {}).get("time_readable", "N/A")

    # Créer un tableau de comparaison
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

    # Ajouter les lignes
    table.add_row(
        "Algorithme",
        classical_algo,
        quantum.get("shor_estimate", {}).get("algo", "Inconnu"),
        "-",
    )
    table.add_row(
        "Taille de clé",
        str(classical.get("classique", {}).get("key_size", 0)) + " bits",
        str(quantum.get("shor_estimate", {}).get("key_size", 0)) + " bits",
        "-",
    )
    table.add_row(
        "Temps estimé",
        classical_time,
        quantum_time,
        f"[{COLORS['info']}]{EMOJIS['time']} ~1000x plus rapide[/{COLORS['info']}]",
    )

    console.print(table)

    # Graphique ASCII (simplifié)
    console.print("\n[bold]Graphique de comparaison (échelle logarithmique)[/bold]")
    console.print(
        f"Classique:  [red]{'▰' * 50}[/red] {classical_time}\n"
        f"Quantique:  [green]{'▰' * (5 if 'heure' in quantum_time else 10)}[/green] {quantum_time}"
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
        algo_type = "Classique" if name in ["bsgs", "rsa"] else "Quantique" if name in ["grover", "shor"] else "PQC"
        time = data.get("time_seconds", "N/A")
        ops = data.get("ops", data.get("n_iterations", "N/A"))
        status = (
            f"[{COLORS['safe']}]{EMOJIS['safe']} Rapide[/{COLORS['safe']}]"
            if time < 1
            else f"[{COLORS['warning']}]{EMOJIS['warning']} Lent[/{COLORS['warning']}]"
        )
        table.add_row(
            name.upper(),
            algo_type,
            f"{time:.4f}" if isinstance(time, float) else str(time),
            str(ops),
            status,
        )

    console.print(table)


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

    # 2. Temps de cassage classique
    classical = results.get("classical", {})
    if classical:
        print_section(f"{EMOJIS['classical']} Temps de cassage classique")
        format_classical_time(classical)

    # 3. Temps de cassage quantique
    quantum = results.get("quantum", {})
    if quantum:
        print_section(f"{EMOJIS['quantum']} Temps de cassage quantique")
        format_quantum_time(quantum)

    # 4. Comparaison
    if classical and quantum:
        print_section("⚖️ Comparaison Classique vs Quantique")
        format_comparison(classical, quantum)

    # 5. Recommandations
    recommendations = results.get("recommendations", {})
    if recommendations:
        print_section(f"{EMOJIS['pqc']} Recommandations Post-Quantiques")
        format_recommendations(recommendations)

    # 6. Score
    score = results.get("score", 0)
    if score:
        print_section("📊 Score de Robustesse")
        format_score(score)

    console.print("\n" + "=" * 80 + "\n")
    
    
    
#============================================================================#

# Affiche un graphique ASCII comparant les temps classique et quantique.
# Utilise une échelle logarithmique pour les temps.
def plot_comparison(classical: Dict[str, Any], quantum: Dict[str, Any]) -> None:
    if not classical or not quantum:
        print_warning("Impossible de tracer le graphique : données manquantes.")
        return

    # Extrait les données
    classical_algo = classical.get("classique", {}).get("algo", "Inconnu")
    classical_time_str = classical.get("classique", {}).get("temps_classique", "0 secondes")
    quantum_time_str = quantum.get("shor_estimate", {}).get("time_readable", "0 secondes")


    # Convertit les temps en secondes (approximation)
    def time_to_seconds(time_str: str) -> float:
        if "secondes" in time_str:
            return float(time_str.split()[0])
        elif "minutes" in time_str:
            return float(time_str.split()[0]) * 60
        elif "heures" in time_str:
            return float(time_str.split()[0]) * 3600
        elif "jours" in time_str:
            return float(time_str.split()[0]) * 86400
        elif "ans" in time_str:
            return float(time_str.split()[0]) * 3.15e7
        elif "milliards d'années" in time_str:
            return float(time_str.split()[0]) * 3.15e16
        else:
            return 1.0  # Valeur par défaut

    classical_sec = time_to_seconds(classical_time_str)
    quantum_sec = time_to_seconds(quantum_time_str)

    # Échelle logarithmique (base 10)
    log_classical = np.log10(classical_sec) if classical_sec > 0 else 0
    log_quantum = np.log10(quantum_sec) if quantum_sec > 0 else 0

    # Prépare les données pour asciichartpy
    data = {
        "Classique": [log_classical],
        "Quantique": [log_quantum],
    }

    # Configure le graphique
    config = {
        "height": 10,
        "colors": [("red", "green")],  # Classique = rouge, Quantique = vert
        "axis": True,
        "title": f"Comparaison {classical_algo} (échelle log10)",
    }

    # Affiche le graphique
    console.print("\n[bold]📈 Graphique de comparaison (échelle logarithmique)[/bold]")
    console.print(plot(data, config))

    # Légende
    console.print(
        f"[red]Classique:[/red] {classical_time_str} "
        f"| [green]Quantique:[/green] {quantum_time_str}"
    )

    # Calcule l'accélération
    if classical_sec > 0 and quantum_sec > 0:
        speedup = classical_sec / quantum_sec
        console.print(
            f"[bold]Accélération:[/bold] [cyan]{speedup:.0f}x plus rapide[/cyan]"
        )


# Affiche un graphique ASCII des résultats des benchmarks.
def plot_benchmark_results(benchmarks: Dict[str, Any]) -> None:
    if not benchmarks:
        print_warning("Aucun benchmark disponible pour le graphique.")
        return

    # Extrait les temps (en secondes)
    labels = []
    times = []
    for name, data in benchmarks.items():
        time_sec = data.get("time_seconds", 0)
        if time_sec > 0:
            labels.append(name.upper())
            times.append(np.log10(time_sec) if time_sec > 0 else 0)

    if not times:
        print_warning("Aucun temps valide pour le graphique.")
        return

    # Prépare les données pour asciichartpy
    data = [times]
    config = {
        "height": 10,
        "colors": [("cyan",)],
        "axis": True,
        "title": "Temps d'exécution des benchmarks (échelle log10)",
        "labels": labels,
    }

    console.print("\n[bold]📊 Graphique des benchmarks[/bold]")
    console.print(plot(data, config))
