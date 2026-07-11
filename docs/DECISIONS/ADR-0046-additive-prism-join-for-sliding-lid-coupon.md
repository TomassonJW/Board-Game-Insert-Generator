# ADR-0046 - Primitive additive join pour le coupon coulissant

## Statut

`accepted` - extension limitee derivate de ADR-0045, le 2026-07-11.

## Contexte

Le capot coulissant doit etre une seule piece physique avec deux glissieres
laterales. Le pipeline Fusion savait creer un bloc et enlever des volumes, mais
creer les glissieres comme trois blocs separes aurait ete un faux resultat
produit.

## Decision

Ajouter l'operation CAD IR `join_rectangular_prism`, uniquement pour joindre un
prisme rectangulaire local a un corps rectangulaire deja cree. La premiere
utilisation est le capot P34 : une plaque rectangulaire et deux glissieres
laterales descendantes, avec un recouvrement de joint de 0.1 mm.

L'operation est refusee si elle sort de l'enveloppe XY de la plaque ou ne la
recouvre pas en Z. Elle ne cree ni boolean general, ni forme libre, ni
composite metier global.

## Consequences

- la CAD IR reste resolue par le coeur Python et sans import Fusion ;
- Fusion execute une extrusion `Join` ciblee sur le body du capot ;
- le coupon reste distinct de la boite rangee et contient exactement deux
  pieces : bac et capot ;
- le smoke Fusion humain doit verifier que les deux glissieres sont soudees au
  capot, puis l'impression doit verifier la glisse reelle.

## Alternatives refusees

- trois pieces non jointes : pas un capot fiable, donc trompeur ;
- rail abstrait sans geometrie : insuffisant pour le smoke demande par P34-M002 ;
- primitive composite ou boolean generique : trop large pour le premier coupon.

## Suivi

`scripts/fusion/prepare_p34_sliding_lid_coupon_test.ps1` prepare la CAD IR,
l'add-in et les reglages locaux. La validation reste humaine dans Fusion, puis
physique par coupon imprime.
