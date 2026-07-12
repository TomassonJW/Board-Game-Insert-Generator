# Next Actions

Derniere mise a jour : 2026-07-12

## Version active

V0.1 - vrai MVP Fusion-only.

ADR-0055 fixe le produit : add-in Fusion 360 unique, palette embarquee comme
interface principale, coeur Python pur comme source de verite, aucun Studio web,
localhost ou Vite au runtime.

## Derniere mission terminee

P55 - contrat executable cavites fixes / enveloppes extensibles, integre dans
origin/main au commit 0ba10d2. Le coeur pur reste valide ; sa route loopback est
historique et n appartient pas au produit Fusion-only.

## Realignement accepte

P54-R remplace la trajectoire Studio principal / Fusion secondaire. La branche
codex/p56-premium-editor et son commit f669b82 sont archives comme tentative web
non integree. Ils ne doivent pas etre merges.

## Prochaine mission prete

P56 - Editeur complet embarque dans Fusion.

Resultat attendu : etendre palette.html et son bridge pour editer bgig.project.v1
dans Fusion, avec six vues, tables dynamiques, mode simple/avance, persistance,
validation et appel au coeur P55. Aucun serveur local ni navigateur externe.

## Releases bloquees

P57 reste bloque par P56. P44 a P50 restent bloques jusqu a P60.

## Gate humaine active

Aucune avant P60. Le prochain retour humain obligatoire est le smoke final du
parcours complet dans Fusion, prepare automatiquement par Codex.

## Fin de chaque mission

Tests pertinents, git diff --check, commit atomique, integration directe dans
main, push, puis mission suivante seulement si ses dependances sont terminees.
