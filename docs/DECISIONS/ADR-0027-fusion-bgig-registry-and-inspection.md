# ADR-0027 - Registry Fusion BGIG et inspection read-only

Date : 2026-07-07

## Statut

Acceptee.

## Contexte

Le smoke test humain `P12-UI-M002V6` a ete KO critique : Fusion creait des objets
visibles, mais `generate`, `regenerate` et `clear_bgig_scene` ne les retrouvaient
pas. Le message `clear` indiquait `0` scene et `0` objet BGIG alors que des objets
BGIG etaient visibles. Un chemin Python levait aussi l'erreur
`'non_bgig_objects_preserved'` parce que le reporting de generation n'avait pas un
contrat stable.

Cela montre que le probleme n'est pas seulement la suppression, mais le modele de
propriete et d'observabilite Fusion : tagging incomplet, recherche d'attributs
fragile et absence d'outil de diagnostic interne.

## Verification API Autodesk

Documentation verifiee pendant la correction :

- `Attributes.add(groupName, name, value)` ajoute ou met a jour un attribut sur
  l'entite parente. Les valeurs d'attribut sont des chaines.
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Attributes_add.htm
- Le guide Autodesk des attributes indique que les attributs servent a nommer une
  entite, a la retrouver plus tard et a enregistrer des metadonnees d'add-in.
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Attributes_UM.htm
- `Design.findAttributes(groupName, attributeName)` recherche les attributs dans
  le produit Fusion et peut retourner tous les attributs d'un groupe avec un nom
  d'attribut vide.
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Design_findAttributes.htm
- `Occurrence.deleteMe()` supprime l'occurrence et, si c'est la derniere
  occurrence referencee, le component associe.
  https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Occurrence_deleteMe.htm

## Decision

BGIG introduit un registre interne `BgigFusionRegistry` dans l'add-in Fusion.
Cette couche devient responsable de :

- creer un `scene_id` par generation ;
- taguer les entites BGIG avec le groupe `bgig` ;
- ecrire au minimum `generated_by`, `role`, `scene_id`, `version`, et `module_id`
  quand applicable ;
- retrouver les entites BGIG par `Design.findAttributes("bgig", "")` ;
- retrouver une scene legacy par nom strict `BGIG Generated Scene` si les tags
  sont absents ;
- inspecter la scene courante sans mutation ;
- nettoyer les scenes BGIG via les occurrences racines et `deleteMe()` ;
- valider immediatement apres generation qu'une scene BGIG exactement est
  retrouvable.

Une action UI read-only `inspect_bgig_scene` est ajoutee. Elle ne genere rien et
ne supprime rien. Elle produit un rapport copiable listant occurrences root,
components, bodies, sketches, entites taguees, objets BGIG par nom mais non
tagues et incoherences.

`generate` refuse maintenant une scene existante si le registry trouve une scene
BGIG par attribut, un objet BGIG tague ou un objet strictement BGIG par nom.
`regenerate` valide le plan futur, clear via le registry, regenere, puis revalide
qu'une seule scene BGIG existe. `clear_bgig_scene` passe par le registry et ne
supprime pas d'objets utilisateur non BGIG.

## Consequences

- Le flux Fusion devient diagnostiquable par l'utilisateur avant et apres chaque
  action.
- Le tagging est centralise ; les nouveaux objets BGIG doivent passer par le
  registry ou par le wrapper `_tag_bgig_entity`.
- Les objets BGIG legacy strictement nommes peuvent etre detectes meme si les tags
  ont ete manques par une version precedente.
- La validation Fusion reste manuelle : `P12-UI-M002V7` doit confirmer que
  `inspect`, `generate`, `regenerate` et `clear` fonctionnent dans Fusion.
- Aucune nouvelle geometrie, tolerance, solveur ou fonctionnalite produit n'est
  ajoutee.

## Alternatives refusees

- Continuer les micro-corrections dans `clear_bgig_scene` sans inspection : refuse,
  car cela ne prouve pas ou les objets sont crees ni tagues.
- Revenir aux copies independantes de bodies : refuse, contraire a la strategie
  components/occurrences liees validee par P7.
- Supprimer tous les objets dont le nom contient BGIG sans registry : refuse, trop
  risqu? pour les objets utilisateur.
