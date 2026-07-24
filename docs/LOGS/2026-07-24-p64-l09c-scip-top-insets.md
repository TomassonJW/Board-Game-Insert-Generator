# 2026-07-24 — P64-L09C réservations supérieures SCIP

- Suppression du refus global `top_inset_reservations_not_supported`.
- Encodage entier exact des zones et des profils variante/orientation.
- Disjonction SCIP : hors empreinte, sous le plan d'appui ou support exact au
  sommet ; au moins un support par réservation.
- Protection de l'épaisseur de fond et de la profondeur des cavités.
- Désactivation du remplissage hybride lorsque des réservations sont présentes.
- Worker canonique et copie embarquée alignés ; artefact rescelle, archive native
  inchangée.
- Test natif CPython 3.14 / SCIP : solution trouvée en une invocation.
- Aucun benchmark, holdout, Fusion interactif ni impression.
- Mission suivante : P64-F01B, boucle bornée de fermeture et réparation.
