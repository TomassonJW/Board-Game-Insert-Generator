# ADR-0078 - Temoin persistant de plan certifie et warm start

## Statut

Acceptee le 2026-07-22 dans P64-L05C, apres le retour humain P64-L04V et les
lots correctifs R1, L05A et L05B automated-validated.

Cette decision amende uniquement l'interdit de persistance implicite formule
par ADR-0071. Le cache reste non normatif et le projet reste l'unique source
utilisateur. fusion-validated: false. print-validated: false.

## Contexte

Un plan minimal peut etre certifie puis enrichi par insertions locales et rester
materialisable, alors qu'une reconstruction depuis zero ne retrouve plus le meme
chemin dans les budgets courants. Un changement Normal -> Approfondi peut aussi
faire perdre un plan Approfondi connu si ce plan n'existe que dans la session.

Conserver la scene Fusion comme preuve serait dangereux : elle peut etre stale,
retouchee manuellement ou issue d'une autre revision. Reutiliser le cache
opportuniste comme verite serait egalement trompeur : un cache peut expirer et
une restitution ne prouve pas qu'une recherche courante a ete executee.

## Options

### A - Persister le cache global comme solution

Simple, mais confond resultat opportuniste, certificat courant et source de
verite. Cette option court-circuite trop facilement la recherche et rend la
provenance ambigue.

### B - Reconstituer un plan depuis la scene Fusion

Permet de reprendre une scene visible, mais deplace la verite metier vers
l'adaptateur et ne garantit ni revision, ni frontieres P45, ni certificat.

### C - Sidecar exact, recertifie comme incumbent

Un artefact local distinct conserve une partition deja certifiee sous une
identite exacte. Au prochain solve compatible, le coeur reconstruit sa geometrie,
rejoue le certificat commun, puis execute quand meme les lanes prevues.

## Decision

Retenir l'option C.

Le schema est `bgig.certified_plan_witness.v1`. L'identite comprend :

- le digest du projet normalise ;
- le jeu exact et ordonne des digests de frontieres P45 ;
- un digest de compatibilite derive de ces deux dependances.

La methode et l'effort ne sont pas des cles directes. En revanche, deux efforts
qui produisent des jeux de frontieres differents conservent deux fichiers
compatibles distincts. Un passage Normal -> Approfondi -> Normal ne detruit donc
aucun temoin d'un autre jeu de frontieres.

Le sidecar est ecrit atomiquement sous `projects/certified-witnesses/` avec le
digest de compatibilite dans son nom. Il contient la partition complete, son
plan digest, le digest de geometrie des placements, les axes de classement, le
producteur et les invariants de reutilisation.

Avant toute reutilisation, le bridge verifie fail-closed le schema, le digest du
witness, ses dependances, le plan, sa geometrie et ses axes. Le solveur reconstruit
ensuite les placements et espaces libres, puis rejoue
`certify_minimal_free_3d_plan` sous les dependances courantes. Un rejet ne produit
aucun incumbent.

Un witness accepte est un incumbent initial, pas une lane et pas un cache hit :

- `lane_count_added = 0` ;
- toutes les lanes courantes restent executees sous leurs caps ;
- le classement commun choisit le meilleur candidat ;
- le certificat final commun est rejoue ;
- la provenance expose charge, rejet, recertification, selection et conservation.

En Approfondi, le prefixe Normal exact reste execute sans witness. Le witness
compatible est injecte seulement dans l'extension Deep, sous sa deadline commune
de 30 000 ms. Il peut donc survivre a un prefixe Normal sans solution sans
modifier le contrat anytime de L04B.

A dependances identiques, un witness corrompu est remplace au prochain solve
certifie. Une geometrie identique conserve le fichier existant pour eviter une
chaine de digests auto-referencee. Entre geometries distinctes, un witness deja
certifie et au moins aussi bien classe n'est pas ecrase par un plan moins bon.

## Invariants

- le projet, jamais le witness, reste la source de verite ;
- aucun plan stale, non certifie, finalise seulement visuellement ou deduit de la
  scene n'est accepte ;
- aucune lane, aucun budget et aucune deadline ne sont ajoutes ou elargis ;
- aucune finalisation, CAD IR ou scene Fusion n'est declenchee ;
- `cache_hit_claimed = false` et `search_continued = true` ;
- P45 reste proprietaire des frontieres locales, P64 du plan global ;
- `stale_or_cancelled` ne devient pas une annulation utilisateur.

## Consequences

### Positives

- un plan certifie connu peut etre retrouve apres redemarrage de session meme si
  les lanes courantes n'en reconstruisent plus le chemin ;
- les changements d'effort ne detruisent plus les temoins d'autres frontieres ;
- la comparaison entre recherche fraiche et incumbent connu reste observable ;
- le comportement est deterministe, local et testable hors Fusion.

### Limites

- un seul meilleur witness est conserve par identite exacte ;
- aucune politique de nettoyage automatique n'est introduite dans L05C ;
- le witness n'apprend aucune heuristique et n'accelere pas encore les lanes ;
- aucune capture du projet personnel n'est importee dans le depot ;
- le corpus, le replay et l'optimisation appartiennent a P64-L05D.

## Alternatives refusees

- presenter le witness comme un cache hit ou une preuve d'impossibilite ;
- ignorer les frontieres P45 ou accepter une dependance approximative ;
- sauter le prefixe Normal ou les lanes Deep ;
- augmenter silencieusement budgets ou deadline ;
- importer la scene Fusion comme plan certifie ;
- auto-modifier le solveur depuis la palette.

## Validation

Contrat : `docs/P64_L05C_CERTIFIED_PLAN_WITNESS_CONTRACT.md`.
Preuve : `docs/P64_L05C_CERTIFIED_PLAN_WITNESS_EVIDENCE.md`.

fusion-validated: false. print-validated: false.
