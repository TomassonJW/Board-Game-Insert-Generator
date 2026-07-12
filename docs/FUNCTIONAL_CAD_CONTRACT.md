# Contrat de geometrie fonctionnelle V0.1

## But

`bgig.functional_cad_build.v1` transforme le plan complet P41 en pieces CAD
fonctionnelles. C est une etape entre le moteur pur et Fusion : elle ne
recherche pas un nouveau placement et ne valide aucune impression.

## Entrees

- un projet `bgig.project.v1` valide, ou un ancien projet migrable ;
- le plan derive P39 ;
- la reservation P40 ;
- le plan complet P41.

## Sortie

Quand `status` vaut `planned_for_fusion_smoke` :

- `volume_plan` conserve le plan P41 source ;
- `cad_ir` est une scene `cad_ir.v0` lisible par l adaptateur Fusion actuel ;
- `materialization` compte les bacs, cavites, bacs vides, remplissages et
  regions automatiques laissees comme jeu technique ;
- `blockers` est vide.

Quand `status` vaut `impossible`, `cad_ir` vaut `null`. Les blocages expliquent
soit une impossibilite P41, soit une demande exacte qui ne peut pas conserver
les epaisseurs minimales.

## Regles de materialisation

1. Chaque bac place devient un corps imprimable rectangulaire.
2. Chaque logement P39 devient une cavite rectangulaire ouverte par le dessus.
   Sa hauteur atteint le haut du bac afin que la piece reste accessible ; le
   fond minimal reste intact.
3. Les cloisons sont la matiere qui reste entre les cavites : elles ne sont pas
   des corps separes.
4. Les remplissages exacts conserves par P41 sont materialises dans leur forme
   demandee : bac vide, plein ou separateur.
5. Les regions automatiques sont reduites du jeu commun avant materialisation.
   Une region qui ne garde plus de volume utile est classee comme jeu technique.
6. Un support sous plateau peut toucher volontairement la reservation en haut ;
   cela represente une surface de pose, pas une collision.
7. Aucun arrondi, chanfrein, encoche, label, finition, couvercle ou mecanisme
   n est genere dans cette version.

## Surface publique

- Studio local : `POST /api/project-v1/build-cad` ;
- CLI expert :
  `python -m board_game_insert_generator export-project-v1-cad PROJECT --output PATH`.

La CLI ecrit seulement une CAD IR JSON. Elle ne lance ni Fusion, ni un export
STL, ni une impression.

## Validation

- tests du plan complet, des demandes impossibles et des dimensions de cavites ;
- test 50 bacs / 72 familles / 25 elements plats ;
- lecture de la scene par `generation_plan_from_cad_ir` en mode compact ;
- build TypeScript/Vite et route loopback locale ;
- smoke humain Fusion P43 encore requis.
