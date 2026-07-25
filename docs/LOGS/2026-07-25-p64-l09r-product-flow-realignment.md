# 2026-07-25 — Recadrage calcul, finition et progression

## Contexte

Thomas confirme que la chute théorique d'un petit conteneur dans l'ouverture
d'un conteneur inférieur n'est pas un défaut produit à certifier. Il demande de
conserver les plateaux dans SCIP, de privilégier les petits conteneurs sous les
grands, de séparer à nouveau calcul et finition et de rendre l'attente visible.

## Changements

- ADR-0088 accepte le retour sélectif au support par enveloppe.
- La préférence petits-dessous/grands-dessus devient souple, jamais dure.
- Le calcul minimal conserve les réservations et redevient matérialisable.
- La finition devient facultative, indépendante et non destructive.
- Les budgets initiaux sont 3, 10, 20, 60 et 180 secondes, visibles à côté du
  niveau choisi pour le calcul et pour la finition.
- Les trois boutons restent visibles ; la jauge n'apparaît que pendant une
  opération et ne réserve aucun espace au repos.
- P64-L09V 0.1.63 est supersédée sans observation.
- P64-L09R-B à F puis L09R-V deviennent la nouvelle séquence.

## Vérifications

- Mission documentaire : aucun code produit, benchmark ou package Fusion lancé.
- Tests documentaires : 2/2 OK.
- Suite complète : 855/855 en 226,902 s, un test natif ignoré sous Python 3.10.
- git diff --check : OK.

## Impact

P64-L09R-B devient la prochaine mission unique. Les lots P45/P46, modularité,
capacité post-solve, couvercles et horizons P70+ restent séparés.

## Suivi

- Implémenter P64-L09R-B selon le contrat L09R.
- Ne pas exécuter la checklist P64-L09V de l'add-in 0.1.63.
- Préparer une nouvelle gate humaine seulement après L09R-F.
