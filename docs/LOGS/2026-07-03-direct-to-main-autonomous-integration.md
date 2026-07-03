# 2026-07-03 - Direct-to-main autonomous integration

## Contexte

La politique precedente autorisait Codex a utiliser une pull request standard
apres une mission reussie. Cette strategie a cree un faux blocage pour la PR #8 :
la mission etait testee et integree proprement, mais la PR est devenue une etape
inutile alors que la branche etait fast-forward depuis `origin/main`.

## Decision humaine

Thomas autorise explicitement Codex a modifier la politique Git BGIG vers
`Direct-to-main autonomous integration`, a committer cette documentation, a
pousser directement `main` vers `origin/main` et a fermer la PR #8 si elle devient
obsolete.

## Regle active

Apres une mission reussie, Codex doit integrer directement dans `main` et pousser
`main` vers `origin/main` quand :

- les tests pertinents passent ;
- `git diff --check` passe ;
- le workspace est propre ;
- la branche est basee sur `origin/main` ;
- l'integration est fast-forward ou non conflictuelle ;
- aucune vraie gate humaine n'est atteinte.

Les pull requests sont reservees aux replis : protection de branche, review
humaine imposee, refus de push direct, conflit, divergence non triviale,
authentification absente ou mission risquee/structurante.

## Impact

- La PR #8 doit etre rendue obsolete si le push direct `main` reussit.
- Les futures missions autonomes repartent de `origin/main` apres integration.
- Les gates produit et architecture restent obligatoires.
- La gate active apres P4-M004/P4-M006 reste le choix du prochain perimetre Fusion
  ou du retour au coeur Python.