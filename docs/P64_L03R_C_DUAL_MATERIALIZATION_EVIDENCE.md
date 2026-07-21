# P64-L03R-C — Preuve de matérialisation duale et scène courante

Date : 2026-07-21

## Résultat

P64-L03R-C est `implemented-core`, `implemented-fusion-bridge`,
`implemented-fusion-ui` et `automated-validated`. Le cycle explicite consomme
maintenant le `minimal_layout` certifié de L03R-B. Ce plan peut produire une CAD
IR et une scène Fusion avant toute finalisation, sans étendre les enveloppes ni
distribuer le volume résiduel.

La finalisation reste un artefact distinct et optionnel. Aucune méthode de
finition réelle n'est ajoutée dans C : une tentative sans politique explicite
échoue honnêtement et conserve le plan minimal courant.

`fusion-validated: false`, `print-validated: false`.

## Portée livrée

- `staged_calculation.py` orchestre deux artefacts nommés : `minimal_layout` et
  `finalized_plan` ; le premier est sélectionné par défaut pour matérialiser.
- Le calcul global appelle `solve_minimal_layout` avec les frontières et digests
  exacts issus de L01/L02 ; une dépendance locale modifiée rend le plan stale.
- `partition_cad.py` accepte une sélection d'artefact explicite et construit la
  CAD IR depuis le plan reçu sans relancer le solveur historique.
- Le bridge Fusion transmet `artifact_kind` et refuse toute sélection absente,
  obsolète ou non certifiée.
- La palette expose deux suites : matérialiser les volumes minimaux maintenant,
  ou choisir plus tard une méthode de finition.
- Une édition locale ne lance ni solve global, ni finalisation, ni mutation de
  scène.

## Identité exacte de l'artefact et de la CAD IR

La sélection et la scène transportent ensemble :

- `artifact_kind` ;
- `artifact_digest` ;
- `partition_plan_digest` ;
- `cad_ir_digest` ;
- `source_revision`.

Le digest CAD couvre la géométrie complète et l'identité source, en excluant
uniquement son propre champ récursif. L'adaptateur Fusion le recalcule avant de
construire un plan de génération. Une CAD IR modifiée après certification est
refusée.

Une scène n'est affichée comme courante que si les cinq champs correspondent à
l'artefact et à la CAD IR courants. Un ancien digest ou une ancienne révision ne
peut plus masquer l'action `Mettre à jour la scène`.

## Remplacement borné de la scène Fusion

Le bridge écrit et valide d'abord la nouvelle CAD IR, puis inspecte la scène.
Il choisit la création ou la régénération à partir de la propriété observée, pas
du libellé du bouton.

Le remplacement est refusé avant toute suppression si la scène contient
plusieurs racines BGIG, des objets BGIG ambigus ou des objets seulement
ressemblants mais non tagués. Une régénération acceptée supprime uniquement la
racine possédée par BGIG. Les objets utilisateur non BGIG restent hors de cette
portée. Après génération, le bridge vérifie de nouveau la racine, le nombre de
corps et l'identité exacte ; un texte de succès ne suffit jamais.

## UX progressive

Après `Calculer l'agencement minimal`, la palette indique explicitement :

- que le plan minimal est certifié ;
- que les volumes restent à leurs dimensions minimales ;
- que le résiduel n'est pas distribué ni imprimé ;
- que `Matérialiser les volumes minimaux` est disponible avant finition ;
- que `Finaliser le volume` est une branche optionnelle dont les méthodes
  arriveront dans P64-F01.

Après matérialisation puis édition, l'ancienne scène reste visible mais passe à
`désynchronisée`. Après un nouveau calcul, l'action primaire devient `Mettre à
jour la scène`. Les détails de méthode, budget, provenance et arrêt restent
secondaires et repliés.

## Fixtures contractuelles couvertes

- fixture 11 : matérialisation minimale acceptée avant finalisation ;
- fixture 12 : échec de finalisation, plan minimal conservé et matérialisable ;
- fixture 13 : nouvelle révision, ancienne identité CAD désynchronisée ;
- fixture 14 : ancien digest incapable de masquer la mise à jour de scène ;
- fixture 15 : scène ambiguë bloquée avant suppression ou génération ;
- fixture 16 : synchronisation locale sans solve, finalisation ou scène ;
- fixture 17 : contraintes de plateaux et réservations conservées par le plan ;
- fixture 18 : cas dense 11 × 34 honnêtement inchangé.

Le registre Fusion simulé couvre aussi la préservation d'une occurrence
utilisateur non taguée lors d'un effacement BGIG borné.

## Validation automatisée

Les validations de clôture couvrent :

- orchestration staged et identité CAD ;
- construction CAD historique et sélection minimale explicite ;
- bridge projet, synchronisation de scène, DOM et présentation résultat ;
- registre et plan de génération Fusion simulés ;
- suite complète `unittest` ;
- Ruff, `compileall`, frontière `adsk` du cœur et `git diff --check`.

Résultats de clôture :

- 185/185 tests du préparateur L03R-V : staged, CAD, bridge projet,
  synchronisation, DOM, résultat et squelette Fusion ;
- 79/79 tests `test_fusion_palette_*.py` ;
- 5/5 tests de continuité P66 et 3/3 de transport de résultat ;
- 625/625 tests de la suite complète ;
- Ruff vert sur les modules cœur/bridge modifiés et sur les erreurs critiques
  des adaptateurs/tests modifiés ; le scan Ruff global conserve des constats
  historiques hors scope ;
- `compileall`, frontière `adsk`, parse PowerShell et dry-run du préparateur
  0.1.57 verts ;
- `git diff --check` exécuté à la clôture Git.

Le SHA intégré est consigné par le marqueur d'installation et dans le rapport
Git de la mission. La gate humaine suivante porte uniquement sur l'observation
Fusion.

## Limites

- C ne fournit aucune transformation de finition, cale, remplissage ou réserve
  utile ; P64-F01 reste verrouillé.
- Aucun solveur historique public, budget, tolérance, valeur physique, default,
  schéma projet, jeu ou géométrie de cavité n'est modifié.
- P45 conserve les variantes et formes locales ; P64 ne les redéfinit pas.
- La scène n'est pas déclarée observée dans Fusion par les tests simulés.
- Le cas dense 11 × 34 reste `no_solution_within_budget` ; aucune nouvelle
  solvabilité ou impossibilité n'est revendiquée.
- La fixture historique P66 à huit bacs avec réservations hautes reste construite
  par son preflight historique, mais le nouveau portefeuille minimal Normal la
  refuse dans son budget avec `TOP_INSET_WITHOUT_SUPPORTING_BODY`. Le bridge
  n'émet alors aucune CAD IR ; C ne masque ni ne corrige ce résultat de solveur.

## Suite

P64-L03R-V devient la prochaine gate humaine. Le script
`scripts/fusion/prepare_p64_l03r_v_corrective_test.ps1` prépare le package
0.1.57, vérifie les runtimes et laisse seulement les observations dans Fusion :
plan minimal non rempli, matérialisation avant finition, stale visible,
remplacement sans doublon et objet utilisateur préservé.

Une gate positive ne vaudra ni calibration physique ni validation d'impression.
P64-F01A02 reste verrouillé jusqu'à cette preuve et ses dépendances.
