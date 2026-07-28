# P64-L09U-R6-V — preuve humaine KO 0.1.77

Date : 2026-07-28.

Verdict : `human-KO`, `do-not-run`.

`fusion-validated=false`, `print-validated=false`.

## Acquis humains conservés

- La profondeur des cavités est correcte, y compris sur les
  micro-chevauchements.
- Les parties sous et hors plateau restent accessibles.
- La continuité entre plateau amovible et cavité reste directe, sans matière
  intermédiaire.
- Les cavités conservent identité, X/Y, orientation et profondeur.
- Calcul, finalisation et matérialisation restent rapides sur les cas observés.
- Le chemin BRep transitoire, le rendu progressif, le rollback et la respiration
  Fusion restent acquis.

Ces acquis doivent rester couverts par les régressions R7.

## Défaut A — placement automatique et parois canoniques

Les empreintes automatiques des plateaux et livrets ne respectent pas encore la
géométrie finale des conteneurs :

- une découpe de livret peut ne laisser qu'environ `0,4 mm` de paroi ;
- le minimum canonique attendu est `1,2 mm` sur toute paroi externe ou
  séparation interne utile ;
- le placement longe arbitrairement des frontières au lieu de favoriser une
  encoche utile et centrée au-dessus de la matière et des cavités ;
- une empreinte peut arriver gratuitement au bord de la boîte ;
- deux zones plates séparées ne certifient pas chacune leur distance minimale
  au bord et aux autres zones.

Le livret de `CasLimite02+` illustre le défaut de bord. Toute position qui laisse
un fragment de matière inférieur à `1,2 mm` doit être rejetée ou déplacée sur
une autre position automatique certifiée.

## Défaut B — empilement forcé et matérialisation

Le cas `CasLimite02++` force le recouvrement :

- plateau `140 × 160 × 4 mm`, rotation `0°`, `stack_order=0` ;
- livret `110 × 155 × 2 mm`, rotation `90°`, `stack_order=1` ;
- boîte `240 × 180 × 70 mm`, hauteur utile `69,8 mm`.

Le calcul, la finalisation et la matérialisation aboutissent, mais la scène
Fusion présente :

- des micro-encoches fines et aléatoires ;
- une encoche d'environ `0,5–0,6 mm` de large et `6 mm` de profondeur ;
- des plaques ou volumes supplémentaires au-dessus des conteneurs ;
- des surplombs ;
- un ordre local de pile inversé.

La règle produit est : dans une pile automatique, la plus petite empreinte
orientée est en dessous et la plus grande au-dessus. L'ancien `stack_order` ne
peut pas inverser silencieusement cette règle.

## Journal humain autoritaire

Journal lu sans écriture :

`C:\Users\janko\Documents\BGIG\projects\dev-action-logs\session-ms4ljsbf-u6mhrv7t\events.jsonl`

Snapshot final :

`snapshots/project-2b13e6422419f47e88a9cf87b1705117d1dd1b8088b42a97e531cb56f73ed395.bgig.json`

Faits des événements 43 à 65 :

- digest projet final :
  `98b85b20f4d813d9b7a17fa0a7e229dac8bb5e0f6e59b92469020fc05ef4e960` ;
- calcul : `2759 ms` de recherche, réponse complète vers `2809 ms`,
  `solution_found` ;
- finalisation : `2192 ms`, réponse complète vers `2250 ms`, certificat final
  annoncé réussi ;
- matérialisation : environ `1098 ms`, `scene_synchronized`.

Le pipeline annonce donc un succès complet pour une scène humainement fausse.

## Replay instrumenté initial

Les deux projets ont été relus sans écriture.

| Projet | SHA-256 avant | SHA-256 après | Pipeline actuel |
|---|---|---|---|
| `CasLimite02+` | `5E84FE6F5C0B3E5F046201D442C414504DD95D4DB8E711169A2624485466D7DC` | identique | calcul, finalisation et CAD IR réussis |
| `CasLimite02++` | `83E9E90A6BFD86B18D3A157077A0E63DC2F543DDAB626ADB2151E269E01D9743` | identique | calcul, finalisation et CAD IR réussis |

Le replay de `CasLimite02++` expose la première divergence :

1. le plan minimal conserve l'ordre historique : plateau `level=0`, livret
   `level=1` ;
2. le score automatique minimise le nombre de recouvrements avant de regarder
   le centrage utile ;
3. le certificat de paroi ne couvre que les enveloppes de cavités, pas le bord
   de boîte, les frontières des corps finalisés ni les fragments créés par les
   intersections ;
4. la finalisation accepte alors des coupes de prise de
   `0,5 × 4,88 × 6 mm`, `0,5 × 22,24 × 6 mm` et
   `0,5 × 1,18 × 6 mm` ;
5. la CAD IR transmet ces coupes au plan Fusion.

Le BRep reproduit donc un contrat amont déjà faux. Le correctif ne doit pas être
limité au rendu Fusion.

## Décision 0,1 mm à formaliser

Le replay publie encore des coordonnées et dimensions dérivées comme `78,88`,
`22,24`, `4,88` et `1,18 mm`. Elles démontrent que la résolution produit n'est
pas encore canonique au dixième.

La grille produit `0,1 mm` doit être décidée par ADR et propagée séparément de
l'epsilon numérique interne. Aucune valeur physique n'est modifiée par cette
décision.

## Suite R7

R7 doit :

1. formaliser le classement des positions automatiques, les enveloppes de paroi
   finales et l'ordre automatique des piles ;
2. adopter la grille produit `0,1 mm` par ADR ;
3. recertifier une position contre la géométrie finale sans déplacement
   silencieux ;
4. refuser toute micro-encoche ou paroi résiduelle inférieure au minimum ;
5. conserver l'ordre et les intervalles exacts jusqu'au plan Fusion ;
6. ajouter des régressions publiques anonymisées de bout en bout ;
7. préparer une nouvelle candidate, sans promouvoir de validation Fusion.

La candidate 0.1.77 ne doit plus être exécutée.
