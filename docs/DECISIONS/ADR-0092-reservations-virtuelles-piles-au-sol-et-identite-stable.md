# ADR-0092 - reservations virtuelles, piles au sol et identite stable

Date : 2026-07-26

## Statut

`accepted`, `implemented`, `automated-validated`, gate Fusion humaine requise.

## Contexte

La gate `0.1.68` a montre quatre defauts lies :

- le calcul complexe avec plateau ne trouvait plus de disposition pour
  `CasLimite01` ;
- une cavite orientee pouvait etre reconstruite depuis un axe brut et perdre
  son minimum ;
- le repli composite repartait d'une fermeture continue deja partiellement
  modifiee ;
- le rafraichissement de la jauge traversait le pont Fusion pendant un calcul
  natif et pouvait sembler gele.

ADR-0089 interdit deja de fabriquer un support en allongeant un conteneur. Les
plateaux et livrets doivent reserver du volume sans devenir des corps
utilisateur.

## Decision

1. Un plateau ou livret est represente pendant le calcul par un prisme virtuel
   superieur interdit. Il n'est ni materialise, ni finalise comme conteneur.
2. Pour les cas d'au moins douze participants avec reservation superieure, une
   voie bornee construit des piles legales depuis les enveloppes minimales,
   puis range leurs bases sur le fond. Le certificat BGIG commun reste
   obligatoire.
3. Aucune dimension minimale source ne peut diminuer. Les cavites sont toujours
   reconstruites dans l'orientation canonique avant ajout d'une compensation
   locale d'encastrement.
4. Si la fermeture continue ne suffit pas, la fermeture composite repart des
   placements minimaux certifies d'origine, jamais d'une tentative partielle
   echouee.
5. Les unions CAD des annexes precedent les coupes plateau/livret. Une coupe ne
   concerne que les corps finaux qui atteignent le plan reserve et chevauchent
   son empreinte.
6. La progression visible est locale a la palette. Le worker envoie un seul
   evenement de fin a Fusion ; aucun polling du pont Python n'est periodique.
7. Le budget contractuel appartient a l'identite deterministe. La limite de
   temps restante avant la deadline globale est une contrainte d'execution
   separee, transmise par `wall_clock_cap_ms`.
8. Une finition reussit uniquement avec un `finalized_plan` courant,
   recertifie et `printable_residual_volume_mm3=0`.

## Consequences

- `CasLimite01` peut conserver tous les minima, placer les 18 conteneurs sous
  les reservations et fermer tout le volume imprimable.
- `CasLimite02` conserve sa cavite de cartes debout et applique ensuite
  l'encastrement exact sur le corps final.
- Le solveur reste borne et fail-closed ; une limite de budget reste
  `no_solution_within_budget`.
- Les plateaux ne creent aucun composant utilisateur supplementaire.
- Une meme geometrie produit une meme identite fonctionnelle quand la limite
  murale n'a pas interrompu la recherche.
- La gate Fusion reste necessaire pour confirmer la reactivite Qt/HTML et la
  materialisation reelle.

## Alternatives rejetees

- Allonger un conteneur jusqu'au plateau : interdit par ADR-0089.
- Materialiser le plateau comme un conteneur utilisateur : faux pour le modele
  produit et pour le nombre de composants.
- Finaliser d'abord une geometrie partielle puis y appliquer les encastrements :
  les minima et les cibles de coupe peuvent diverger.
- Continuer le repli composite depuis une croissance continue echouee : cette
  base peut ne plus etre une partition decoupable.
- Interroger Python toutes les secondes depuis la palette : le pont peut etre
  bloque par le calcul natif.
- Inclure les millisecondes restantes dans l'identite du budget : deux calculs
  geometriquement identiques obtiennent alors des digests differents.

## Validation

- Regressions dediees : piles au sol, cavite orientee, CAD, worker, transport
  Fusion, DOM, fermeture rectangulaire et composite.
- Rejeux locaux exacts `CasLimite01` et `CasLimite02` : calcul, finition et CAD
  complets, minima conserves, residuel nul.
- Suite complete : `910/910` en `329.251 s`, un test SCIP natif ignore sous
  Python 3.10.
- Aucun benchmark ou holdout solveur execute.
- `fusion-validated=false`, `print-validated=false`.
