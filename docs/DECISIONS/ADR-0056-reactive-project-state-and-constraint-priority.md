# ADR-0056 - Etat projet reactif et priorite des contraintes

## Statut

Proposee le 2026-07-12 apres la revue produit P60. Validation humaine requise
avant P61.

## Date

2026-07-12

## Cartes liees

- P60-R - Realignement produit apres revue Fusion
- P61 - Etat reactif et architecture de palette
- P66 - Acceptance V0.1 revisee

## Contexte

La palette P60 invalide le dernier calcul des qu une valeur source change, mais
ne recalcule pas les dimensions derivees et ne distingue pas assez clairement
le projet courant, l ancien plan et la scene Fusion materialisee. Une personne
peut donc modifier la boite puis continuer a voir une proposition devenue
obsolete, sans comprendre quelles valeurs seront conservees au prochain calcul.

Les dimensions finales de conteneur melangent aussi intention, contrainte dure
et valeur calculee. Une valeur proposee par l utilisateur doit pouvoir guider le
solveur sans rendre toute autre adaptation impossible.

## Options

1. Verrouiller les mesures apres le premier calcul.
2. Recalculer et materialiser automatiquement apres chaque edition.
3. Separer les etats et recalculer seulement les derives rapides, puis demander
   une action explicite pour le solveur et Fusion.

## Decision proposee

Retenir l option 3.

Le projet expose quatre etats lies par des digests :

- `source` : mesures, contenus et intentions utilisateur ;
- `derived` : minima, hauteur de conception, reservations et diagnostics
  rapides ;
- `solved` : proposition complete ou partielle issue du solveur ;
- `materialized` : scene Fusion issue d un plan resolu precis.

Une edition recalcule `derived`, marque `solved` comme obsolete et conserve
l ancien apercu grise. Elle ne modifie jamais automatiquement la scene Fusion.
Le recalcul global puis la mise a jour Fusion restent explicites.

Les contraintes suivent cet ordre : limites physiques, contenus, minima de
fabrication, verrous utilisateur, cibles utilisateur, preferences, valeurs
derivees. Chaque dimension finale de conteneur accepte `Auto`, `Cible` ou
`Fixe`. Un echec identifie la contrainte dure responsable et ne conseille pas
generiquement d agrandir la boite si une autre organisation est possible.

## Consequences

### Positives

- Les mesures d origine restent modifiables sans ambiguite.
- La scene Fusion n est jamais modifiee silencieusement.
- Les cibles de taille restent souples, les verrous restent prouvables.
- Les tests peuvent couvrir chaque transition et chaque digest.

### Negatives

- Le schema et le bridge doivent transporter les statuts et digests.
- L interface doit representer explicitement un plan obsolete.
- Le solveur doit expliquer les conflits de contraintes, pas seulement echouer.

## Alternatives refusees

- Figer la boite apres calcul : trop contraignant pour l exploration normale.
- Regenerer Fusion a chaque frappe : lent, surprenant et dangereux pour le
  document courant.

## Validation attendue

- Tests purs des transitions et priorites.
- Test DOM de l apercu obsolete.
- Observation Fusion : edition, recalcul, puis mise a jour volontaire sans
  doublon et sans toucher aux objets non BGIG.
