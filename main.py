## Modules locaux
from scanner import scan_target
from algo import estimate_classical_time
from quantum import estimate_quantum_time
from crypto import get_pqc_recommendation
from report import generate_report

# Modules Python
from argparse import ArgumentParser


def main():
    parser = ArgumentParser("QuantumSentinel — Auditeur de robustesse cryptographique post-quantique")
    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Cibel à auditer (ex: google.com ou 192.168.1.1)'
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=443,
        help='Port TSL à scanner (défaut: 443)'
    )
    parser.add_argument(
        '-o', '--output',
        default='report.html',
        help='Fichier de sortie du rapport (défaut: report.html)'
    )
    parser.add_argument(
        '--no_quantum',
        action='store_true',
        help='Désactiver la simulation quantique (mode rapide)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Afficher les détails d'exécution"
    )
    
    args = parser.parse_args()
    
    print(f"[*] Cible       : {args.target}:{args.port}")
    print(f"[*] Rapport     :  {args.output}")
    print(f"[*] Mode quantique     :  {'désactivé' if args.no_quantum else 'activé'}")
    print()
    
    
    # Pipeline principal — chaque étape sera implémentée dans les phases suivantes
    
    results = scan_target(args.target,args.port, args.verbose)
    print(results)
    
    results['classical'] = estimate_classical_time(results)
    print(results['classical'])
    
    if not args.no_quantum:
        results['quantum'] = estimate_quantum_time(results)
    results['recommendations'] = get_pqc_recommendation(results)
    generate_report(results, args.output)
    
    print(f"\n [+] Rapport généré : {args.output}")
    

if __name__ == '__main__' :
    main()
