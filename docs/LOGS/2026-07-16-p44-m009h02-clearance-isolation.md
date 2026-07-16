# P44-M009H02 - Isolation des jeux et defaults cohérents

Date : 2026-07-16

Une revue Fusion plus poussée révoque la validation fonctionnelle 0.1.32 : les
champs globaux historiques et les defaults par rôle divergeaient, tandis que
les cartes pouvaient afficher une valeur effective antérieure au dernier
recalcul silencieux.

Le package 0.1.33 synchronise les deux représentations et affiche l’effectif du
dernier objet dérivé de même id. Il conserve la cascade et la règle pairwise de
l’ADR-0063. Les tests ajoutés prouvent un override inférieur isolé sur deux
assets et deux gaps distincts sur trois conteneurs. « Hauteur de conception »
est maintenant visiblement grisée, sans changement de calcul.

Automated-validated : 476 tests et syntaxe JavaScript passent. fusion-validated:
false ; print-validated: false. Prochaine preuve : P44-M009H02V.
