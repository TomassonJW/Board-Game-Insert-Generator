# Preuve P64-L09S-F - durcissement de bout en bout et preparation V

- mission: P64-L09S-F
- status: automated-validated
- package_version: 0.1.66
- local_installation_status: pending-post-integration
- fusion-observed=false
- print-validated=false

## Cas limite recent

Le preflight public separe deux preuves :

- contrat exact observe : corps `23.2 x 23.2 x 31.6`, origine Z `21.2`, sommet `52.8`, plan plateau `58.6`, `gap_below_tray_mm=5.8`, `artificial_growth_mm=0` ;
- fixture reproductible de meme enveloppe minimale, boite 200 x 150 x 60, hauteur utile 59,6 et plateau 100 x 80 x 1.

La fixture parcourt : calcul minimal, selection et CAD minimal, finalisation composite, selection de l'artefact final, CAD IR, plan Fusion pur.

## Resultat du preflight sec

- marqueur : `P64_L09SV_PREFLIGHT_OK` ;
- digest : `c590501d8199ed5463655c391757cf8e2e4f3ba7c06ed018a1d1f70b733ec308` ;
- enveloppe minimale : `23.2x23.2x31.6` ;
- gap exact : `5.8` ;
- unions d'annexes : `4` ;
- coupes plateau/prise : `2` ;
- composant utilisateur : `1` ;
- residuel imprimable final : `0` ;
- holdout ouvert : faux ;
- benchmark execute : faux.

Le dry-run du preparateur 0.1.66 passe sans ecriture AppData. Il verifie le manifeste, les gardes ciblees, le preflight, l'installation simulée, les reglages et les marqueurs du package.

## Validation automatisee

- garde F dediee : 5/5 ;
- contrat reservations recentes : 9/9 ;
- fermeture composite : 3/3 ;
- contrat Fusion composite : 2/2 ;
- cycle etage : 19/19 ;
- CAD IR : 14/14 ;
- palette projet : 29/29 ;
- dry-run preparateur : OK ;
- authorized_suite: 826/826 ;
- tests benchmark/holdout/tournament/corpus exclus : 72 ;
- test SCIP natif ignore sous Python 3.10 : 1.

## Frontiere humaine

Apres integration de F, Codex execute le preparateur reel, verifie la version installee, le commit, la fixture et les reglages, puis s'arrete. Thomas realise uniquement les huit observations de `docs/P64_L09S_V_FUSION_GATE_RECIPE.md`.

Aucune observation Fusion et aucune validation d'impression ne sont revendiquees ici.
