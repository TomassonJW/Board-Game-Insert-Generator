# P64-L07E — preuve d'intégration produit HiGHS

Date : 2026-07-23

Statut : `done`, `implemented-core`, `implemented-fusion-bridge`,
`automated-validated`, `product-gain-demonstrated`.

`fusion-validated: false`

`print-validated: false`

## 1. Décision

HiGHS 1.15.1 est intégré seul comme proposition supplémentaire du portefeuille
minimal. OR-Tools n'a gagné aucune famille distincte. SCIP et LAFF restent
`benchmark-only`. Aucun deuxième ou troisième moteur n'est donc justifié.

Le holdout L07 n'a été ni rouvert, ni rejoué, ni utilisé pour régler le runtime
produit.

Décision d'architecture :
`docs/DECISIONS/ADR-0082-highs-offline-product-lane.md`.

## 2. Gate produit avant changement

La comparaison a utilisé les cinq régressions ouvertes que HiGHS et BGIG
pouvaient tous deux recevoir fidèlement, avec un thread, 1 024 Mio et 3 s :

| Cas | HiGHS | BGIG | Relation |
| --- | --- | --- | --- |
| `multi-cavity-normal` | solution certifiée | solution certifiée | HiGHS meilleur |
| `simple-quick` | solution certifiée | solution certifiée | HiGHS meilleur |
| `variant-dead-end-quick` | `bounded_unknown` | `no_solution_within_budget` | non comparable |
| `variant-unsolved-quick` | `bounded_unknown` | `no_solution_within_budget` | non comparable |
| `real-18-containers-20-contents-normal` | `bounded_unknown` | `bounded_unknown` | non comparable |

Résultat :

- solutions certifiées : égalité ;
- vérité fonctionnelle : égalité ;
- qualité : 2 victoires HiGHS, 0 défaite, 0 égalité ;
- fragmentation résiduelle : 0 au lieu de 5 sur les deux solutions communes ;
- temps total observé : 1,308987 s pour HiGHS, 4,077502 s pour BGIG ;
- décision : `product_gain_demonstrated=true`.

Preuve compacte :
`tests/fixtures/p64_l07e_highs_product_gate.v1.json`.

Après câblage, la même gate rejouée par la lane produit finale avec le seed
scellé 640708 conserve les cinq statuts, les deux gains et zéro perte. Elle
effectue cinq appels externes, obtient deux propositions recertifiées et
n'ouvre aucun holdout. Digest fonctionnel :
`7596b00d83f38a5caa0b77367201b506dffdb6374ca68c6e8d719f3388e4cb7b`.

## 3. Binaire retenu

Source : release officielle HiGHS 1.15.1, archive Windows x86_64 MIT.

| Élément | Octets | SHA-256 |
| --- | ---: | --- |
| archive officielle | 5 517 021 | `26302d9024f307e09128a45a58898917287351dcf754c55aebc07742237f78bf` |
| `highs.exe` | 906 752 | `4ff24abf4cfdd5f4e87e73edf6886d1b9333c13c388b328466ca15a502b4c46d` |
| `highs.dll` | 10 392 576 | `722dfd5eb66e1de2fe306d8e6e9c68085ca1b454c04e1860dd22f636557e6de5` |

Le digest annoncé par l'API de release officielle et le digest téléchargé sont
identiques. Le lancement local répond :

`HiGHS version 1.15.1 Githash 04024d7`.

Le paquet redistribué compte huit fichiers et 11 307 594 octets. Il contient :

- exécutable et DLL ;
- licence MIT HiGHS ;
- avis tiers ;
- licences CLI11, pdqsort et zstr ;
- manifest `ARTIFACT.json` avec tailles, empreintes et contrat hors ligne.

L'inventaire PE32+ ne trouve aucun import différé. `highs.exe` charge la DLL
embarquée `highs.dll`, les bibliothèques système Windows, Universal CRT et
le runtime Visual C++ 14 (`MSVCP140`, `VCRUNTIME140`, `VCRUNTIME140_1`).
Les trois DLL Microsoft sont présentes sur le poste de validation en version
`14.44.35211.0`. Aucun installateur n'a été lancé. Une machine qui ne fournit
pas ce runtime échoue fermée vers le solveur BGIG interne.

## 4. Équivalence CLI

Le tournoi utilisait l'API Python isolée. Le produit utilise le CLI officiel
pour ne pas dépendre de l'ABI Python embarquée dans Fusion.

La sonde d'équivalence vérifie :

- 3/3 contrôles exacts ;
- 8/8 statuts de régression identiques ;
- 0 différence sur les axes de qualité ;
- digest :
  `3ea1e213bf26cdc667e7f23abdc6ca0b8d730956af857005f24e177c858bed63`.

## 5. Câblage produit

`highs_product_solver.py` :

- vérifie l'exécutable et la DLL par SHA-256 ;
- traduit seulement le sol rectangulaire T0/T1 représentable ;
- écrit un modèle LP et des options dans un répertoire temporaire local ;
- lance directement `highs.exe`, sans shell ni réseau ;
- borne le temps, la mémoire, les threads et l'annulation ;
- parse strictement la solution ;
- ne publie jamais directement une solution produit.

`minimal_layout_solver.py` :

- appelle HiGHS une seule fois avant les lanes internes ;
- recertifie toute proposition avec le certificat BGIG commun ;
- ajoute la proposition au même classement lexicographique ;
- exécute ensuite toutes les lanes internes inchangées ;
- conserve l'appel unique dans le préfixe Normal d'Approfondi ;
- transporte la provenance HiGHS jusque dans le résultat anytime final ;
- répond avec le portefeuille interne si HiGHS est absent ou invalide.

`palette_project.py` configure uniquement le binaire embarqué sur Windows. Sur
Mac, la lane reste non configurée et BGIG continue seul. Le package Fusion passe
à 0.1.60.

## 6. Limites explicites

La lane HiGHS produit couvre :

- un seul niveau à Z = 0 ;
- rectangles orthogonaux ;
- rotation Z 0/90 degrés ;
- 64 participants au maximum ;
- dimensions exactes au millième de millimètre.

Elle refuse :

- réservation haute ;
- dimension non représentable ;
- formes T2 à T4 ;
- empilement, support complexe ou pose arbitraire.

Une infaisabilité du modèle de sol devient `bounded_unknown`. Elle ne prouve
jamais l'impossibilité générale du projet.

## 7. Fallback testé

Les cas suivants ont été testés :

- runtime non configuré : sortie historique sans provenance externe ;
- exécutable ou DLL absent ;
- empreinte différente ;
- erreur de processus ou de fichier ;
- timeout ou mémoire ;
- solution invalide ;
- certificat BGIG refusé.

Dans tous ces cas, les lanes internes restent disponibles. Un runtime corrompu
est visible comme `invalid_runtime`, n'est jamais sélectionné et n'altère pas la
solution interne.

## 8. Validations

Validations propres à L07E :

- compilation Python ciblée : OK ;
- lancement du vrai binaire 1.15.1 : OK ;
- tests produit HiGHS : 5/5 ;
- tests de preuve L07E : 2/2 ;
- tests de reprise nullable du runner L07D : 2/2 ;
- gate du runtime intégré : 5 cas, 2 gains, 0 perte, 0 changement de statut ;
- équivalence CLI : 3 contrôles et 8 régressions, 0 différence ;
- package staging 0.1.60 : runtime complet et vrai binaire démarré ;
- Ruff ciblé et compilation Python ciblée : OK ;
- garde documentaire : 2/2 ; alignement Fusion-only : 6/6 ;
- suite complète : 765/765 en 228,071 s ;
- diff-check : exécuté dans la clôture Git.

## 9. Ce qui n'est pas revendiqué

- aucune validation dans Fusion 360 ;
- aucune validation d'impression ;
- aucune amélioration du cas dense 11 × 34 ;
- aucune nouvelle forme ;
- aucun changement de certificat, tolérance, géométrie, CAD, scène ou valeur
  physique ;
- aucune supériorité générale au-delà de la portée mesurée.
