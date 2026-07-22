# P64-L04B — Contrat Approfondi anytime et borné

Date : 2026-07-22
Statut : `implemented-core`, `automated-validated`

## 1. Objectif borné

P64-L04B rend l’effort `deep` utile même lorsque ses lanes supplémentaires
n’aboutissent pas. Le solve minimal exécute d’abord le préfixe `normal`, conserve
son meilleur plan certifié comme incumbent, puis tente uniquement les trois lanes
propres à `deep` sous une deadline commune.

Le lot ne modifie ni le schéma projet, ni les dimensions physiques, jeux,
tolérances ou defaults, ni les formes P45, ni la finalisation, la CAD IR ou la
scène Fusion.

## 2. Préfixes et budgets

Les lanes restent ordonnées et monotones :

- `quick` : lanes 1 à 3 ;
- `normal` : lanes 1 à 6, dont `quick` est un préfixe ;
- `deep` : préfixe `normal`, puis lanes 7 à 9.

Les caps historiques par lane restent inchangés :

| Profil de lane | États | Essais | Temps de garde par lane |
| --- | ---: | ---: | ---: |
| Rapide | 256 | 15 000 | 5 000 ms |
| Normal | 1 500 | 75 000 | 12 000 ms |
| Approfondi | 5 000 | 250 000 | 30 000 ms |

Une enveloppe supplémentaire `max_deep_extension_elapsed_ms = 30_000` borne
l’ensemble des lanes 7 à 9. Chaque lane Deep reçoit le minimum entre son cap
historique et le temps restant. Cette enveloppe commence après production du
préfixe Normal ; elle ne multiplie donc plus 30 s par lane supplémentaire.

## 3. Incumbent et sélection

Le meilleur plan certifié du préfixe Normal devient l’incumbent initial. Une
lane Deep ne le remplace que si son tuple de classement nommé est strictement
meilleur. Une égalité conserve l’incumbent afin d’éviter un changement gratuit
de placement.

Le tuple reste, dans l’ordre : volume du groupe, vide interne, hauteur,
empreinte, fragmentation, contacts maximisés et support minimal maximisé. Aucun
score total opaque ou nouveau top 3 moteur n’est introduit. Les frontières de
chaque phase restent présentes dans la provenance.

Si Normal ne trouve aucun plan, Deep peut toujours fournir le premier incumbent.
Si aucune phase ne trouve de plan, le résultat reste honnêtement
`no_solution_within_budget`.

## 4. Deadline, arrêt et annulation

La deadline Deep est coopérative : elle est vérifiée avant chaque lane, transmise
au beam comme temps restant et revérifiée avant la certification de nouveaux
candidats. À expiration :

- un incumbent certifié est retourné avec `solution_found` ;
- sans incumbent, le résultat reste `no_solution_within_budget` ;
- la raison d’arrêt distingue explicitement ces deux cas.

Une annulation de validité (`stale_or_cancelled`) est différente d’une deadline.
Elle peut signifier que la source a changé pendant le calcul ; elle reste donc
fail-closed et ne retourne pas l’ancien incumbent. L04C pourra exposer une
annulation utilisateur seulement lorsqu’elle portera une sémantique coopérative
distincte et sûre.

## 5. Observabilité

La provenance du plan ou de l’échec expose au minimum :

- le budget Normal et le budget Deep ;
- la deadline commune et le temps écoulé de l’extension ;
- les lanes prévues, tentées et terminées ;
- le digest et le profil de l’incumbent initial ;
- la phase ayant fourni le plan sélectionné ;
- l’amélioration ou la conservation de l’incumbent ;
- la raison d’arrêt et l’état deadline/annulation ;
- les sources et digests des frontières locales des deux phases.

Une exécution limitée par horloge n’est pas présentée comme déterministe. Le
certificat commun reste autoritaire avant tout retour matérialisable.

## 6. Acceptation automatisée

1. les préfixes et caps historiques restent monotones ;
2. les lanes Deep partagent une seule deadline de 30 s ;
3. une expiration après un succès Normal retourne ce succès et jamais
   `no_solution_within_budget` ;
4. une amélioration Deep peut remplacer l’incumbent, une égalité le conserve ;
5. une expiration sans incumbent reste honnête ;
6. une annulation stale reste `stale_or_cancelled` ;
7. budgets, temps, lanes, incumbent et arrêt sont observables ;
8. aucun solve de finalisation, corps, CAD ou scène n’est déclenché ;
9. le cas dense 11 × 34 ne reçoit aucune nouvelle revendication.

`fusion-validated: false`, `print-validated: false`.
