# P64-L05D2 - Contrat elagage sous ordre explicite

## Objectif

Reduire les evaluations de placement qui ne peuvent pas modifier le prefixe de
participants retenu par une lane dont l'ordre est explicite.

Ce lot est une optimisation interne du beam P64. Il ne change ni portefeuille,
ni lanes, ni ordre, ni classement, ni budget, ni cap, ni deadline Deep.

## Preuve d'equivalence

`_participant_branches` classe les participants ainsi :

- sous ordre explicite, l'index dans cet ordre est la premiere composante de la
  cle ;
- sans ordre explicite, la cle depend du nombre d'options, des axes fixes, du
  volume et de l'identifiant.

Sous ordre explicite, apres avoir trouve
`max_participant_branches` participants possedant au moins une option, tout
participant ulterieur a un index strictement plus grand. Il ne peut donc plus
entrer dans le prefixe retenu. Son evaluation est inutile et peut consommer le
budget d'essais avant que les branches deja trouvees soient avancees.

La boucle peut s'arreter exactement a ce point. Les participants sans option
restent sautes, donc le solveur continue jusqu'a obtenir le quota ou epuiser la
liste.

Sans ordre explicite, aucune coupure anticipee n'est permise : le nombre
d'options participe a la cle et tous les participants restants doivent etre
evalues.

## Invariants

- prefixe de participants selectionne identique hors epuisement de budget ;
- branche de seed inchangee ;
- options et score d'options inchanges ;
- heuristique sans ordre explicite inchangee ;
- compteurs, caps et raisons d'arret restent reels ;
- aucun nouveau budget ou lane ;
- aucun effet sur finalisation, CAD, scene ou Fusion ;
- aucune nouvelle revendication sur le cas dense.

Liberer des essais peut produire davantage d'etats sous les caps existants. Ce
n'est pas une augmentation de budget : le solveur consomme mieux le budget deja
accorde.

## Acceptation

1. test unitaire prouvant deux evaluations, pas quatre, pour un quota de deux
   sous ordre explicite ;
2. meme fixture sans ordre explicite prouvant quatre evaluations ;
3. solution conservee et essais strictement reduits ;
4. gate A/B du corpus complet sans regression fonctionnelle ;
5. gain de travail mesure ;
6. suites beam, solveur minimal et complete vertes ;
7. projet personnel observe uniquement en lecture seule et SHA-256 inchange.

Aucune ADR supplementaire : ADR-0079 gouverne deja la gate et ce changement ne
modifie ni architecture ni comportement public.
