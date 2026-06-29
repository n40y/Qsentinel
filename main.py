# main.py

from scanner import scan_target
from algo import estimate_classical_time
from quantum import estimate_quantum_time
from crypto import get_pqc_recommendation
from report.html_report import generate_report
from report.scorer import score
from cli import (
    print_title,
    print_section,
    print_error,
    print_success,
    print_summary,
    plot_comparison,
    plot_benchmark_results,
    run_with_progress,
)
from argparse import ArgumentParser
import sys


def main():
    parser = ArgumentParser(
        description="Qsentinel — Auditeur de robustesse cryptographique post-quantique",
        formatter_class=lambda prog: ArgumentParser(prog).help,
    )
    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Cible à auditer (ex: google.com ou 192.168.1.1)",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=443,
        help="Port à scanner (défaut: 443 pour TLS, 22 pour SSH)",
    )
    parser.add_argument(
        "-o", "--output",
        default="report.html",
        help="Fichier de sortie du rapport (défaut: report.html)",
    )
    parser.add_argument(
        "--no_quantum",
        action="store_true",
        help="Désactiver la simulation quantique (mode rapide)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Afficher les détails d'exécution",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Exécuter des benchmarks sur les algorithmes",
    )
    parser.add_argument(
        "--demo-qpe",
        action="store_true",
        help="Démonstration de Quantum Phase Estimation (QPE)",
    )

    args = parser.parse_args()

    # Affichage initial
    print_title("🚀 Qsentinel - Audit Cryptographique Post-Quantique")
    console.print(f"[bold]Cible:[/bold] {args.target}:{args.port}")
    console.print(f"[bold]Rapport:[/bold] {args.output}")
    console.print(
        f"[bold]Mode quantique:[/bold] {'[red]désactivé[/red]' if args.no_quantum else '[green]activé[/green]'}"
    )
    console.print()

    try:
        results = {}

        # Étape 0: Démonstration QPE (optionnelle)
        if args.demo_qpe:
            from quantum.qpe import demo_qpe
            demo_qpe()
            console.print()
            return  # On quitte après la démo

        # Étape 1: Scan TLS ou SSH
        print_section(f"🔍 Scan en cours sur {args.target}:{args.port}...")
        results = scan_target(args.target, args.port, args.verbose)

        # Vérifier si le scan a réussi
        if not results.get("tls") and not results.get("ssh"):
            print_error(f"Aucun résultat pour {args.target}:{args.port}. Vérifiez la cible et le port.")
            sys.exit(1)

        if args.verbose:
            if results.get("tls"):
                print_success(f"Scan TLS terminé pour {args.target}:{args.port}")
            if results.get("ssh"):
                print_success(f"Scan SSH terminé pour {args.target}:{args.port}")

        # Étape 2: Estimation classique
        print_section("💻 Estimation des temps de cassage classique...")
        results["classical"] = estimate_classical_time(results)
        if args.verbose:
            print_success("Estimation classique terminée")

        # Étape 3: Estimation quantique
        if not args.no_quantum:
            print_section("🔮 Estimation des temps de cassage quantique...")
            results["quantum"] = estimate_quantum_time(results)
            if args.verbose:
                print_success("Estimation quantique terminée")
        else:
            results["quantum"] = {}

        # Étape 4: Recommandations PQC
        print_section("🔒 Génération des recommandations PQC...")
        results["recommendations"] = get_pqc_recommendation(results)
        if args.verbose:
            print_success("Recommandations générées")

        # Étape 5: Score
        print_section("📊 Calcul du score de robustesse...")
        results["score"] = score(results)
        if args.verbose:
            print_success(f"Score calculé: {results['score']}/100")

        # Étape 6: Génération du rapport HTML
        print_section("📄 Génération du rapport HTML...")
        generate_report(results, args.output)
        print_success(f"Rapport généré: {args.output}")

        # Étape 7: Benchmarks (optionnel)
        if args.benchmark:
            print_section("⚡ Exécution des benchmarks...")
            from algo.benchmark import run_benchmark
            benchmarks = run_with_progress(
                "Benchmarks",
                run_benchmark,
                "Exécution des tests de performance..."
            )
            results["benchmarks"] = benchmarks
            plot_benchmark_results(benchmarks)

        # Affichage final du résumé
        print_section("📋 Résumé des résultats")
        print_summary(results)

        # Afficher le graphique de comparaison (si données disponibles)
        if results.get("classical") and results.get("quantum"):
            plot_comparison(results["classical"], results["quantum"])

    except Exception as e:
        print_error(f"Erreur critique: {e}")
        if args.verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    main()
