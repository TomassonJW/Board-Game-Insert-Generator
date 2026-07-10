# P28 - Smoke Fusion de selection locale

## Statut

`technical-path-observed`, `product-ux-rejected` — le pont CAD IR a ete observe, mais son message et ses blocs ne constituent pas une experience produit acceptable. La scene ne devient pas `fusion-validated` et l impression reste non validee.

## Objet du test

Le scenario `mixed-box` exporte la variante recommandee `variant:compact_origin:dc7a91d387b5` sous forme de trois enveloppes rectangulaires. Ce ne sont pas encore des bacs finis : aucune cavite, paroi, encoche ou tolerance de fabrication n est ajoutee par P28.

| Element | Origine mm | Taille mm |
| --- | --- | --- |
| Bac cartes | `0, 0, 0` | `72 x 102 x 30` |
| Bac jetons | `72, 0, 0` | `62 x 54 x 22` |
| Bac des | `134, 0, 0` | `48 x 48 x 24` |

La boite de reference `240 x 160 x 60 mm` est non imprimable et sert uniquement au repere.

## Preparation automatique

Codex execute :

```powershell
scripts/fusion/prepare_local_composer_selection_test.ps1
```

Le script exporte les fichiers temporaires dans `%TEMP%`, installe l add-in courant dans le dossier Fusion et precharge `bgig_ui_settings.json`. Il ne lance pas Fusion lui-meme.

## Controle humain restant dans Fusion

1. Ouvrir un nouveau document Assembly-compatible.
2. Lancer `BoardGameInsertGenerator` puis `Run` avec `Action = generate` et `Input mode = cad_ir_file`.
3. Verifier une boite de reference et exactement trois enveloppes compactes, aux dimensions et positions du tableau.
4. Verifier que le rapport ne pretend ni cavites finies ni validation d impression, et affiche `Print validation: false`.
5. Rapporter `P28 Fusion OK` ou `P28 Fusion KO`, avec le texte d erreur ou une capture si possible.

## Criteres d acceptation

- La scene est creee sans recalcul P21 dans Fusion.
- Les trois volumes selectionnes sont presents sans doublon.
- Aucun objet ne se presente comme un bac final ou un STL valide.
- Aucun statut `fusion-validated` ou `print-validated` n est applique avant le retour humain.
## Requalification P29

Le retour utilisateur du 2026-07-11 rejette ce smoke comme demonstration produit :
le dialogue est technique et les trois enveloppes ne sont pas des bacs. Le
protocole est conserve comme preuve de raccord CAD IR seulement. P31 doit le
remplacer par une projection de geometrie fonctionnelle avant toute nouvelle
gate Fusion utilisateur.