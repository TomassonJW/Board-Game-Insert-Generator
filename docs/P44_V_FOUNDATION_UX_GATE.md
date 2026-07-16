# P44-V — Gate globale de fondation UX

Statut : `human-fusion-check-required`.

## Déclencheur

P44-M001 à P44-M009 sont terminées selon leurs contrats. P44-V observe le package produit 0.1.40, référence `92f07c8`; P44-VP ne modifie que la préparation documentaire.

## Portée validable

ADR-0062 : palette Fusion seule, quatre espaces cohérents, édition stable, conteneurs/éléments liés, cycle document local, réglages lisibles, aperçu priorisé et matérialisation explicite.

Preuves de support : densité/cartes `2f78a99`, conteneurs `80c1a6c`, navigation `7b71d01`, création `b8cf884`, document `d82def6`, réglages `7c76ba0`, saisie/aperçu `92f07c8`. Elles ne remplacent pas l’observation globale actuelle.

## Préparation Codex

```powershell
.\scripts\fusion\prepare_p44_v_foundation_ux_test.ps1 -RepoRoot (Get-Location).Path
```

## Vérification humaine Fusion

1. Parcourir Boîte, Conteneurs, Réglages et Aperçu : le chemin novice reste compréhensible sans diagnostics experts.
2. À largeur habituelle, réduite puis large : lisibilité, absence de chevauchement et contrôles essentiels stables.
3. Au clavier, remplacer rapidement trois champs : focus, sélection, scroll et volets restent stables ; aucun ancien `Résolu` ne subsiste.
4. Créer/modifier des conteneurs, repli global/individuel et Auto/Cible/Fixe global : identité et contrôles restent lisibles, sans scène automatique.
5. Importer ou créer cinquante conteneurs avec éléments : palette utilisable et en-têtes accessibles.
6. Ouvrir et enregistrer sous un projet historique : héritages, overrides compatibles et hauteur dérivée restent cohérents.
7. Avec une scène BGIG existante, confirmer qu’aucune saisie, sauvegarde, vérification ou prévisualisation ne la modifie ; seul `Matérialiser dans Fusion` peut le faire.

## Retour attendu

`P44-V Fusion OK 0.1.40 - package 92f07c8`

Pour un KO : scénario, largeur ou nombre de conteneurs, action, attendu et observé.

## Non-revendications

Aucune forme P45, valeur physique, géométrie imprimée ou impression : `print-validated: false`.
