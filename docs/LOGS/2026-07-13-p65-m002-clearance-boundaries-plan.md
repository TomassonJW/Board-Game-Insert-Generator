# P65-M002 - Plan des jeux boite et inter-conteneurs

Date : 2026-07-13
Statut : planned, ready, docs-only

Le retour Fusion demande de ne plus confondre le jeu contre la boite et le jeu
entre conteneurs. Le plan conserve le fond a Z=0, reutilise la marge superieure
existante pour la frontiere Z de boite et ajoute seulement un champ de perimetre
X-Y. La compatibilite copie l ancien jeu X-Y quand ce champ manque.

La mission est adaptee a Terra tres elevee si elle reste atomique et respecte les
cas d acceptation de NEXT_ACTIONS. Terra ne doit ni inventer un jeu inferieur, ni
changer les defaults, ni ajouter supports/cales, ni ouvrir la refonte UX.