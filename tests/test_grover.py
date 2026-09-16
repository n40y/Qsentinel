# tests/test_grover.py

from quantum.grover import grover

result = grover('101')
print(f"Cible      : {result['target']}")
print(f"Trouvé     : {result['top_result']}")
print(f"Probabilité: {result['top_probability']*100:.1f}%")
print(f"Succès     : {result['found']}")
print(f"Itérations : {result['n_iterations']}")
print(f"Counts     : {result['counts']}")
