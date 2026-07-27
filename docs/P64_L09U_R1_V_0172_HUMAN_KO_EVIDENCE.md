# P64-L09U-R1-V — preuve du human-KO 0.1.72

## Verdict

Le package 0.1.72 est `human-KO`, `do-not-run`.

`fusion-validated=false`, `print-validated=false`.

## Acquis humains conservés

- BGIG démarre sur un projet vierge.
- Calculer déclenche un calcul explicite.
- `CasLimite01+` et `CasLimite02+` peuvent produire un plan minimal.
- La finalisation peut produire un aperçu.
- Une matérialisation du plan minimal peut aboutir.

Ces acquis ne valident pas la matérialisation du plan final.

## Défauts bloquants observés

### Fidélité

- L'aperçu final BGIG et la scène Fusion n'ont pas la même disposition.
- Des cavités des couches hautes paraissent fortement agrandies ou plus
  profondes que leurs dimensions projet.
- Les cavités ne sont pas réparties de la même manière entre l'aperçu et
  Fusion.

### Fermeture

- `CasLimite01+` sans plateau s'arrête vers 4,5 à 4,6 secondes sur
  `xy_composite_residual_owner_not_found`, avant le plafond normal.
- Le même projet peut finaliser avec son plateau.
- `CasLimite01++` n'obtient pas de plan minimal malgré une disposition connue
  comme logeable.

### Matérialisation

- La matérialisation finale peut prendre de nombreuses minutes.
- Fusion peut afficher « ne répond pas » avec peu d'activité processeur.
- Une exécution a fini après environ quinze minutes.
- Une autre a échoué sur :
  `3 : Combine1 / Compute Failed / ALL_TOOL_BODY_REFERENCE_LOST`.
- La scène obtenue après erreur est incohérente.

## Interprétation corrective

Les faits ont été reproduits hors Fusion sans modifier les projets personnels.
Le diagnostic distingue cinq causes :

1. substitution automatique d'un autre plan minimal pendant la finalisation ;
2. aperçu composite fondé sur un rectangle englobant et un ancien repère de
   cavité ;
3. cellules résiduelles multiples ou jeux Z mal classés ;
4. ordre de pile incapable d'insérer tardivement un support large ;
5. chronologie Fusion dépendante de corps-outils Combine.

ADR-0098 décide le correctif R2. Aucun de ces constats n'autorise à déplacer une
cavité, inventer une valeur physique ou promouvoir une validation Fusion.

## Sources locales protégées

Les projets personnels `CasLimite01+`, `CasLimite01++` et `CasLimite02+` sont
lus uniquement pour des replays exacts. Ils ne sont ni modifiés ni versionnés.
