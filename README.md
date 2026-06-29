# Qsentinel ⚛️🛡️

**Qsentinel** est un outil d'audit de robustesse cryptographique conçu pour évaluer la vulnérabilité des configurations réseau (TLS) face aux futures menaces du calcul quantique, tout en guidant la transition vers la cryptographie post-quantique (PQC).

L'outil analyse les flux réels pour cartographier le niveau de risque et estimer géométriquement les écarts de temps de cassage entre les superordinateurs classiques et les algorithmes quantiques de rupture (Shor et Grover).

## 🚀 Fonctionnalités

* **Scanner TLS Intégré :** Audit dynamique des versions TLS et extraction automatique des suites de chiffrement (*cipher suites*) acceptées et des métadonnées du certificat serveur.
* **Modélisation des Menaces Quantiques :**
    * **Impact Shor :** Évaluation de la rupture des clés asymétriques (RSA, ECC, DH) et calcul du passage d'une complexité classique exponentielle à une résolution quantique polynomiale.
    * **Impact Grover :** Analyse de l'affaiblissement du chiffrement symétrique (ex: AES-128 vs AES-256) par réduction quadratique de l'espace des clés.
* **Laboratoire Quantique (Simulation & Hardware) :** Exécution et benchmark de circuits quantiques (Qiskit) en simulation locale ou directement sur les processeurs physiques d'IBM Quantum via le cloud.
* **Moteur de Recommandation PQC :** Orientation vers les standards de transition post-quantique validés par le NIST (CRYSTALS-Kyber pour l'encapsulation de clés, CRYSTALS-Dilithium pour la signature).
* **Rapports Clairs :** Génération automatique d'un rapport HTML synthétique pour visualiser immédiatement les points de rupture.

## 🛠️ Architecture du Projet
