# P64-L09S-V 0.1.66 - preuve de KO humain

- Date d'observation : 2026-07-26
- Verdict : `human-KO`
- Package : `0.1.66`
- Politique : `do-not-run`
- Validation impression : `print-validated=false`

## Observation humaine

Sur le projet complexe recent avec plateaux et elements retournes, la recherche approfondie s'arretait apres environ deux secondes et ne trouvait pas de plan. Certains volumes semblaient aussi rabotes alors que leurs minima ne doivent jamais changer.

## Preuve extraite des journaux

- le budget public de `180 s` etait bien transmis ;
- la finition quittait en environ une seconde apres ses partitions guillotine ;
- le projet contenait 28 conteneurs ;
- le conteneur 011 avait un minimum source de `76 x 76 x 31.8 mm` ;
- la variante selectionnee declarait `53.6 x 76 x 31.8 mm` ;
- la perte de volume externe etait d'environ 29,5 % avec une fausse certification ;
- trois finitions conservaient `printable_residual_remains`, sans `finalized_plan`, tandis que l'UI annoncait un succes.

## Causes

1. Le reagencement interne oubliait que l'enveloppe source etait un plancher par axe.
2. La finalisation moderne essayait deux variantes de partition guillotine sans repli exploratoire reel.
3. L'ancienne fermeture continue n'etait plus appelee et ne traitait pas les prismes reserves superieurs.

## Decision de reprise

Le package `0.1.66` est rejete. Le correctif `0.1.67` applique ADR-0090, passe la validation automatisee, puis doit etre observe dans Fusion sur le meme cas. Aucun resultat de `0.1.66` ne vaut validation produit.
