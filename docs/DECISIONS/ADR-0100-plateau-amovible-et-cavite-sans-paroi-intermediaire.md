# ADR-0100 — Plateau amovible et cavité sans paroi intermédiaire

## Statut

Acceptée par la clarification humaine de Thomas le 2026-07-28.

Cette décision corrige le raccord vertical entre une réservation supérieure et
une cavité qu'elle recouvre. Elle ne vaut ni validation Fusion, ni validation
d'impression.

## Contexte

La gate 0.1.74 montre que les cavités sont conservées et calibrées, mais
enfermées sous une dalle. ADR-0099 imposait une séparation verticale égale à
la paroi canonique entre le dessous de l'encastrement et le sommet de la
cavité. Cette séparation est incorrecte pour un plateau amovible qui sert
lui-même de fermeture fonctionnelle.

La paroi canonique reste nécessaire autour des empreintes et le fond canonique
reste nécessaire sous la cavité. Elle ne doit pas être insérée entre deux
vides qui doivent communiquer.

## Décision

### 1. La cavité est finalisée avant l'effet du plateau

Le conteneur et sa cavité sont d'abord résolus comme sans réservation :

- dimensions et profondeur calibrées inchangées ;
- X/Y et orientation inchangés ;
- sommet sur la face fonctionnelle finale ;
- surplus Z uniquement sous la cavité ;
- fond restant certifié.

Cette formulation décrit l'ordre logique et le résultat géométrique. Elle
n'impose pas une nouvelle feature Fusion paramétrique.

### 2. L'encastrement local abaisse ensuite le sommet de cavité

Si une découpe locale réelle du propriétaire recouvre la cavité :

- le sommet final de la cavité coïncide exactement avec le dessous de la
  découpe locale responsable ;
- l'abaissement reprend l'intervalle Z déjà résolu du plateau ou livret,
  y compris ses jeux existants ;
- la profondeur de cavité ne change pas ;
- aucune valeur physique nouvelle n'est introduite.

La seule empreinte globale du plateau ne suffit pas à classer une cavité
`below_top_inset`. Un conteneur plus bas, qui ne porte aucune coupe de ce
plateau, garde sa cavité ouverte sur sa propre face fonctionnelle locale. Cette
règle interdit de descendre une cavité sous une coupe qui n'existe pas dans son
corps.

### 3. Aucune matière intermédiaire n'est imprimée

L'interface est un vide continu :

```text
sommet de cavité == dessous de découpe locale
séparation imprimée intermédiaire == 0 mm
```

Le plateau amovible ferme la cavité lorsqu'il est présent. Après retrait du
plateau, la cavité est directement accessible. Le plateau reste virtuel dans
le moteur et ne devient ni corps utilisateur, ni support artificiel.

### 4. Les parois et fonds canoniques restent ailleurs

La séparation nulle concerne uniquement l'interface verticale entre deux
vides qui se recouvrent réellement en XY.

Restent certifiés :

- le fond sous la cavité ;
- les parois latérales de la cavité ;
- les bandes de matière entre empreintes disjointes ;
- les zones d'appui restantes du plateau ;
- les coupes et intervalles locaux de chaque réservation.

### 5. La continuité est prouvée de bout en bout

Le résultat final, l'aperçu, la CAD IR et le plan Fusion portent :

- l'identité de la réservation et de sa région locale responsable ;
- l'identité de la coupe réelle portée par le même propriétaire ;
- le sommet de cavité et le dessous de découpe ;
- `top_separation_mm=0` ;
- `intermediate_material_thickness_mm=0` ;
- `top_interface_kind=direct_void_to_removable_top_inset` ;
- une preuve explicite de continuité du vide.

Tout artefact sous plateau qui ne respecte pas ces égalités est refusé avant
Fusion.

## Compatibilité

Cette ADR supersède uniquement :

- ADR-0099 §3 pour la séparation verticale sous une réservation recouvrante ;
- ADR-0093 §4 lorsqu'elle était interprétée comme une paroi entre une cavité et
  la découpe qui la recouvre.

Restent inchangés :

- le calibre figé et l'ancrage Z déterministe d'ADR-0099 ;
- les parois XY autour des vides voisins ;
- les réservations locales et leurs paliers ;
- le BRep transitoire, les booléens groupés et le rollback ;
- `fusion-validated=false`, `print-validated=false` avant la nouvelle gate.

## Alternatives refusées

- Conserver la paroi intermédiaire canonique.
- Allonger la cavité jusqu'au plateau.
- Laisser la cavité à son ancien Z puis découper toute la hauteur du corps.
- Transformer le plateau en corps imprimé.
- Inventer un jeu ou une épaisseur spéciale pour masquer le raccord.
