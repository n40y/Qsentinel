# quantum/ibm_runner.py

from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit.tools.monitor import job_monitor


# Exécute un circuit quantique sur IBM Quantum
def run_on_ibm(qc, shots=1024, backend_name=None):
    try:
        IBMQ.load_account()
        provider = IBMQ.get_provider(hub='ibm-q')
        
        if backend_name:
            backend = provider.get_backend(backend_name)
        else:
            backend = least_busy(provider.backends(
                filters=lambda x: x.configuration().n_qubits >= qc.num_qubits and not x.configuration().simulator
            ))
        
        job = backend.run(qc, shots=shots)
        job_monitor(job)
        result = job.result()
        
        return result
    
    
    except Exception as e:
        print(f"Erreur IBM Quantum : {e}")
        return None
