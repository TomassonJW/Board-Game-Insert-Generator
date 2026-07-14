# P44 - Contrat d’orthotypographie française de l’interface

Date : 2026-07-14
Statut : `accepted-product-requirement`, `planned`
Capability : `C-FUSION-UI`, `C-QUALITY`
Surface : palette embarquée Fusion 360 uniquement.

## 1. Exigence

Les textes visibles par l’utilisateur doivent employer un français correctement
accentué et ponctué. Les caractères UTF-8 utiles sont autorisés et attendus :
`é`, `è`, `ê`, `ë`, `à`, `â`, `ù`, `û`, `î`, `ï`, `ô`, `ç` et `œ`.

Exemples de libellés attendus : `Éléments du jeu`, `Réglages`,
`Aperçu`, `Épaisseur`, `Quantité`, `À plat` et `Boîte`.

## 2. Séquencement

- dès P44-M003, tout nouveau libellé ou message utilisateur respecte ce contrat ;
- P44-M003 corrige les textes qu’il touche, sans lancer une réécriture générale ;
- P44-M006 réalise la passe exhaustive sur les libellés, aides, messages,
  placeholders et diagnostics historiques de la palette ;
- P44-V vérifie le rendu réel dans Fusion sur Windows.

## 3. Frontière technique

Les identifiants stables, clés JSON, enums, attributs `data-*`, noms de fichiers,
protocoles de bridge et marqueurs de tests restent ASCII quand leur contrat
l’exige. Le texte humain ne doit pas servir d’identifiant technique.

Les sources UI restent en UTF-8 sans BOM. La palette conserve
`<meta charset="utf-8">` et les échanges JSON ne doivent produire ni mojibake
(`Ã`, `Â`), ni caractère de remplacement (`�`).

## 4. Preuves attendues

- tests DOM sur plusieurs libellés accentués représentatifs ;
- test d’absence des signatures de mojibake dans la palette ;
- roundtrip d’un nom utilisateur tel que `Éléments d’été — boîte à dés` ;
- syntaxe JavaScript, transport Qt et bridge inchangés ;
- observation humaine Fusion à largeur normale et étroite.

Cette exigence ne modifie ni schéma, solveur, tolérance, géométrie, CAD IR,
scène Fusion ou validation d’impression.
