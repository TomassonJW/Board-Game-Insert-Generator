# HiGHS embarqué

BGIG distribue le binaire officiel Windows x86-64 de HiGHS 1.15.1 pour la lane
produit optionnelle décidée par P64-L07E.

Le runtime est local, hors ligne et isolé dans un sous-processus. Son absence,
une empreinte incorrecte, un échec ou une limite atteinte déclenchent le
fallback vers le solveur BGIG.

Le binaire dépend d'Universal CRT et du runtime Visual C++ 14 déjà présents
sur Windows (`MSVCP140`, `VCRUNTIME140`, `VCRUNTIME140_1`). BGIG ne les
installe pas. Si le chargeur Windows ne les trouve pas, la lane externe reste
indisponible et le solveur interne continue.

La version, les tailles, les empreintes et la source officielle sont verrouillées
dans `1.15.1/windows-x86_64/ARTIFACT.json`. Les licences et avis nécessaires
sont distribués dans le même dossier.
