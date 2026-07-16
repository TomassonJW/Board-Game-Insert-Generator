# P44-M007 - Calcul adaptatif et Aperçu priorisé

Date : 2026-07-16

P44-M007 ferme le dernier lot code de la fondation UX P44 autorisé avant sa gate Fusion dédiée. Le package 0.1.37 conserve le cœur Python, le bridge, le solveur, les valeurs physiques et la scène inchangés.

La palette enchaîne maintenant une validation dérivée à 350 ms et un solve complet à 1 500 ms de stabilité. Les réponses dépassées sont rejetées par révision source et par dernière identité de requête. Le fallback manuel devient `Recalculer maintenant` ; `Vérifier` quitte le parcours normal.

L’Aperçu commence par son statut et ses projections réelles, puis affiche alertes et détails. `Matérialiser dans Fusion` reste unique et strictement explicite. `Hauteur de conception` reste dérivée, grisée et non éditable.

Preuves : 477 tests, syntaxe JavaScript, tests ciblés, parse PowerShell, suite complète, compileall, exemple CLI, frontière adsk et dry-run du préparateur de gate passés. P44-M007V est préparée pour le package 0.1.37. fusion-validated: false ; print-validated: false.
