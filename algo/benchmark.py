# algo/benchmark.py

import time
from algo.bsgs import bsgs, benchmark_bsgs
from algo.rsa_naive import factorize
from quantum.grover import grover
from quantum.shor import shor_factorize
from crypto.kyber_demo import kyber_demo
from crypto.dilithium_demo import dilithium_demo


# Exécute des benchmarks sur les algorithmes classiques et quantiques
def run_benchmark():
    results = {}

    # Benchmark BSGS (classique)
    print("[*] Benchmark BSGS...")
    g, h, p = 2, 10, 1019  # Exemple simple
    bsgs_result = benchmark_bsgs(g, h, p)
    results["bsgs"] = bsgs_result

    # Benchmark RSA (classique)
    print("[*] Benchmark RSA (factorisation)...")
    n = 15  # 3 * 5 (très simple)
    start = time.time()
    factors = factorize(n)
    rsa_time = time.time() - start
    results["rsa"] = {
        "n": n,
        "factors": factors,
        "time_seconds": rsa_time,
    }

    # Benchmark Shor (quantique)
    print("[*] Benchmark Shor...")
    n = 15
    start = time.time()
    shor_result = shor_factorize(n, shots=1024)
    results["shor"] = {
        "n": n,
        "factor": shor_result,
        "time_seconds": time.time() - start,
    }

    # Benchmark Grover (quantique)
    print("[*] Benchmark Grover...")
    target = "1101"
    start = time.time()
    grover_result = grover(target, shots=1024)
    grover_result["time_seconds"] = time.time() - start
    results["grover"] = grover_result

    # Benchmark Kyber (PQC)
    print("[*] Benchmark Kyber...")
    start = time.time()
    kyber_result = kyber_demo()
    kyber_result["time_seconds"] = time.time() - start
    results["kyber"] = kyber_result

    # Benchmark Dilithium (PQC)
    print("[*] Benchmark Dilithium...")
    start = time.time()
    dilithium_result = dilithium_demo()
    dilithium_result["time_seconds"] = time.time() - start
    results["dilithium"] = dilithium_result
    
    return results


# Compare le temps de déchiffrement classique/quantique pour différentes tailles de clés.
def compare_classical_vs_quantum():
    comparisons = []

    # RSA
    for key_size in [1024, 2048, 4096]:
        # Temps classique (estimation)
        from algo.complexity import classic_time_breakable
        classical = classic_time_breakable(key_size, "RSA")
        # Temps quantique (estimation)
        from algo.complexity import quantic_time_breakable
        quantum = quantic_time_breakable(key_size, "RSA")
        comparisons.append({
            "algo": "RSA",
            "key_size": key_size,
            "classical_time": classical["temps_classique"],
            "quantum_time": quantum["temps_quantique"],
            "speedup": f"{float(classical['ops_estimees']) / float(quantum['ops_estimees']):.2e}x plus rapide",
        })

    # ECC
    for key_size in [256, 384, 521]:
        classical = classic_time_breakable(key_size, "ECC")
        quantum = quantic_time_breakable(key_size, "ECC")
        comparisons.append({
            "algo": "ECC",
            "key_size": key_size,
            "classical_time": classical["temps_classique"],
            "quantum_time": quantum["temps_quantique"],
            "speedup": f"{float(classical['ops_estimees']) / float(quantum['ops_estimees']):.2e}x plus rapide",
        })

    return comparisons
