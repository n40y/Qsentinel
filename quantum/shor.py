
# quantum/shor.py

from qiskit import QuantumCircuit, execute
from qiskit_aer import Aer
from qiskit.algorithms import Shor
from qiskit.utils import QuantumInstance

from math import gcd
from random import randint


def shor_factorize(n, shots=1024):
    if n % 2 == 0:
        return 2
    if n == 1:
        return 1
    
    # trouver un nombre tel que gcd(a, n) = 1
    a = randint(2, n - 1)
    while gcd(a, n) != 1:
        a = randint(2, n - 1)
        
    backend = Aer.get_backend('qasm_simulator')
    quantum_instance = QuantumInstance(backend, shots=shots)
    shor = Shor(quantum_instance=quantum_instance)
    result = shor.factor(n)
    
    if result.facotrs:
        return result.factors[0][0]
    return None
