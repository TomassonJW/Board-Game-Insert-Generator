# Fusion Smoke Test Automation

Derniere mise a jour : 2026-07-08

## Objectif

Les validations Fusion restent humaines, mais leur preparation ne doit plus etre
un travail manuel PowerShell pour Thomas.

Pour toute future gate Fusion, Codex doit preparer le smoke test depuis le depot
autant que l'environnement local le permet :

- verifier le commit courant ;
- generer les CAD IR temporaires quand le test en a besoin ;
- installer l'add-in courant dans le dossier Fusion AddIns ;
- ecrire les settings UI locaux utiles ;
- verifier que l'add-in installe contient les marqueurs attendus ;
- fournir seulement les actions restantes a realiser dans Fusion.

Thomas ne doit recevoir de blocs PowerShell a executer manuellement que si
l'infrastructure bloque Codex.

## Scripts

Les scripts vivent dans `scripts/fusion/`.

### `install_addin.ps1`

Installe l'add-in courant depuis le repo vers :

```text
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\BoardGameInsertGenerator
```

Le script resout le repo root, verifie `fusion_addin/BoardGameInsertGenerator`,
supprime l'ancienne copie installee, copie l'add-in courant, affiche le commit
courant et verifie les marqueurs de commande UI attendus.

### `check_installed_addin.ps1`

Verifie que l'add-in installe existe et contient les marqueurs attendus.

### `prepare_smoke_test.ps1`

Prepare un smoke test CAD IR depuis une configuration exemple :

```powershell
scripts/fusion/prepare_smoke_test.ps1 `
  -ConfigPath examples/simple_asset_product_scene.json `
  -GenerationMode compact_only
```

Le script exporte une CAD IR dans `%TEMP%`, installe l'add-in, ecrit
`bgig_ui_settings.json` avec `input_mode = cad_ir_file`, puis affiche les actions
Fusion restantes.

### `prepare_quick_parametric_test.ps1`

Prepare le smoke test P12-M004V sans JSON source :

```powershell
scripts/fusion/prepare_quick_parametric_test.ps1
```

Le script installe l'add-in, ecrit `bgig_ui_settings.json` en
`quick_parametric_box`, puis precharge les valeurs :

- box `120 x 80 x 30` ;
- grid `4 x 4 x 3` ;
- wall/floor `1.2` ;
- clearances `0.4` / `0.3` ;
- print profile `draft`.

## Dry run

Tous les scripts de preparation acceptent `-DryRun`.

`-DryRun` doit etre utilise pour verifier la syntaxe, les chemins et le resume
sans modifier `%APPDATA%`.

## Permissions AppData

Si Codex ne peut pas ecrire dans `%APPDATA%`, il doit s'arreter et rapporter :

```text
Local AppData write blocked. Use Local/Handoff or approve filesystem write.
```

Dans ce cas, Codex ne doit pas pretendre que l'add-in est installe et ne doit pas
continuer vers une validation Fusion.

## P12-M004V

Le smoke test courant se prepare par :

```powershell
scripts/fusion/prepare_quick_parametric_test.ps1
```

Actions restantes dans Fusion :

1. Ouvrir Fusion 360 et un document Assembly-compatible.
2. Lancer `BoardGameInsertGenerator` ou cliquer `Generate Board Game Insert`.
3. Verifier `Input mode = quick_parametric_box` et `Action = generate`.
4. Generer, rouvrir BGIG, verifier que toutes les valeurs sont restaurees.
5. Changer `box_inner_x_mm` a `160`, passer en `Action = regenerate`, lancer.
6. Verifier que la scene est remplacee sans doublon.
7. Rouvrir BGIG et verifier que `160` est toujours present.
8. Lancer `clear_bgig_scene`.
9. Verifier que les objets non BGIG sont preserves.

Statut attendu apres preparation : `manual_validation_required`, car seule
l'execution dans Fusion valide le comportement reel.
