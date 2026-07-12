# ADR-0053 - Conformite produit avant acceptation V0.1

## Statut

Accepte le 2026-07-12 a la suite du retour produit rejetant l acceptance P43.

## Date

2026-07-12

## Carte liee

- `P52 - Remise a plat de verite V0.1`
- `P53 a P58 - Reprise du chemin critique V0.1`

## Contexte

P43 a ete accepte apres observation d une scene Fusion. Cette preuve etait trop
etroite : elle ne testait ni la surface de saisie utilisable, ni le resultat
produit par defaut. Le jeu temoin pouvait produire vingt pieces tout en passant
ses tests, et la palette Fusion pouvait rester bloquee sur `Chargement...`.

## Options

1. Conserver P43 comme acceptance MVP et traiter les ecarts visibles en V0.1.1.
2. Transformer la palette Fusion en editeur complet de projet.
3. Garder le Studio comme surface de conception principale et exiger une
   conformite produit complete avant une nouvelle acceptance V0.1.

## Decision

Retenir l option 3. Une acceptance V0.1 exige desormais la conformite complete
au `docs/MVP_V01_ACCEPTANCE_CONTRACT.md` : acces, saisie, controle,
construction, qualite du rangement et passage Fusion. La preuve Fusion reste
necessaire mais ne vaut plus a elle seule une acceptance produit.

Le Studio local reste la surface de conception principale conformement a la
vision canonique. Fusion reste l adaptateur de materialisation et d export ; sa
palette doit indiquer ce role clairement et ne jamais se presenter comme un
editeur incomplet.

## Consequences

- P43 est reouvert ; V0.2 et V0.3 restent bloques.
- Les lots P37 a P42 restent des fondations reutilisables, non un MVP accepte.
- Les tests doivent prouver des comportements et non la simple presence de
  libelles dans le code source.
- La qualite des volumes automatiques devient un critere V0.1, pas une retouche
  post-MVP.

## Alternatives refusees

- Option 1 : elle maintiendrait une promesse produit fausse.
- Option 2 : elle dupliquerait l editeur et le moteur dans Fusion, augmenterait
  le cout de maintenance et contredirait la frontiere Studio principal / Fusion
  adaptateur.

## Suivi

P53 a P58 appliquent le contrat. P58 est la seule gate V0.1 qui peut autoriser
le demarrage de V0.2.
