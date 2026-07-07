# ADR-0026 - Fusion generated scene root ownership

Date : 2026-07-07

Statut : acceptee pour implementation, validation Fusion manuelle requise.

## Contexte

Les smoke tests P12-UI-M002V3 a V5 ont montre que corriger seulement les
occurrences visibles ne suffisait pas. `generate`, `regenerate` et
`clear_bgig_scene` pouvaient encore laisser des esquisses, gabarits ou objets BGIG
accumules dans l'arbre Fusion.

Le probleme est un modele d'ownership incomplet : BGIG ne doit pas supprimer une
scene en poursuivant des bodies, sketches ou composants disperses. Une generation
BGIG doit avoir un owner unique, supprimable et clairement tague.

## Verification API Autodesk

Verification effectuee le 2026-07-07 dans la documentation officielle Autodesk
Fusion API :

- `Occurrences.addNewComponent(transform)` cree un nouveau `Component` et une
  `Occurrence` qui le reference. Source :
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrences_addNewComponent.htm
- `Occurrence.deleteMe()` supprime l'occurrence du design et supprime aussi le
  composant si c'est la derniere occurrence qui le reference. Source :
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrence_deleteMe.htm
- `Attributes.add(groupName, name, value)` ajoute ou met a jour un attribut sur
  l'entite parent. Source :
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Attributes_add.htm

La page officielle `addExistingComponent` n'a pas ete retrouvee de maniere fiable
pendant ce run, mais le comportement reste celui deja utilise et valide
manuellement dans P7/P11/P12 : creer une occurrence liee d'un `Component` existant.

## Decision

BGIG adopte une strategie d'ownership par occurrence racine unique :

- chaque generation cree une occurrence racine `BGIG Generated Scene` ;
- cette occurrence est taguee avec `bgig:role = scene_root` ;
- tous les objets BGIG generes sont crees dans le `Component` de cette occurrence
  racine ;
- `clear_bgig_scene` supprime d'abord les occurrences racines taguees via
  `deleteMe()` ;
- le nettoyage d'objets legacy hors racine est limite aux entites explicitement
  taguees BGIG ;
- les objets utilisateur non BGIG ne sont jamais cibles ;
- `generate` refuse si une racine BGIG ou un objet BGIG tague existe deja ;
- `regenerate` valide la nouvelle generation, nettoie la scene BGIG, refuse de
  continuer si des objets BGIG tagues restent, puis genere une scene propre.

## Consequences

- Le chemin normal de suppression devient une operation racine, pas une chasse
  aux sous-objets.
- Les anciennes entites taguees `BGIG` restent reconnues comme legacy BGIG pour
  cleanup conservateur.
- Les objets non tagues, meme s'ils ressemblent a BGIG, ne sont pas supprimes.
- La validation Fusion P12-UI-M002V6 doit verifier generate, regenerate, clear et
  l'absence d'accumulation apres plusieurs runs.

## Alternatives refusees

1. Continuer a supprimer bodies/sketches individuellement.
   Refuse : trop fragile dans l'arbre Fusion et source probable des restes.
2. Revenir aux copies independantes de bodies.
   Refuse : contraire a la vision produit Component + occurrences liees.
3. Supprimer par nom/prefixe sans tag.
   Refuse : risque de supprimer des objets utilisateur.
