# P44-M009H05 - En-tête conteneur et mode global

Date : 2026-07-16

La revue Fusion 0.1.35 confirme la compacité H04 mais demande une séparation nette entre résumé à gauche et contrôles à droite. Elle révèle aussi que le sélecteur global est recréé sur Auto, même lorsque les cartes sont en Cible, Fixe ou dans un état mixte.

Le package 0.1.36 distribue la ligne en deux groupes, remonte la commande globale dans l’en-tête Conteneurs, expose Mixte lorsque nécessaire et applique Auto, Cible ou Fixe aux trois axes de tous les conteneurs. Aucun contrat métier ou CAD ne change.

Validation : 475 tests, syntaxe JavaScript, DOM, transport Qt, compileall et frontière adsk : OK. fusion-validated: false ; print-validated: false. Prochaine preuve : P44-M009H05V.
