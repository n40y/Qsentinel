# cli/__init__.py

from .formatter import (
    print_title,
    print_section,
    print_error,
    print_success,
    print_warning,
    format_tls_results,
    format_ssh_results,
    format_classical_time,
    format_quantum_time,
    format_recommendations,
    format_score,
    format_comparison,
    format_benchmark_results,
    print_summary,
    plot_benchmark_results,
)
from .progress import run_with_progress

# main.py importe plot_comparison — c'est format_comparison
plot_comparison = format_comparison
