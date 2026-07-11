import { type ChangeEvent, useEffect, useMemo, useState } from 'react'
import { ApiError, createExport, generatePortfolio, loadStarters } from './api'
import { isComposerDraft, type DraftIssue, summarizeDraft, validateDraft } from './validation'
import { proposalExplanation, scoreExplanation } from './proposal_copy'
import type {
  AssetDraft,
  CandidateDraft,
  ComposerDraft,
  Dimension,
  EngineModule,
  Portfolio,
  ReservationDraft,
  StarterTemplate,
  Variant,
} from './types'

type StepId = 'box' | 'contents' | 'organisation' | 'proposals' | 'prepare'

const studioSteps: Array<{ id: StepId; title: string; helper: string }> = [
  { id: 'box', title: 'La boîte', helper: 'Mesure l’espace disponible.' },
  { id: 'contents', title: 'Le contenu', helper: 'Ajoute ce qui doit être rangé.' },
  { id: 'organisation', title: 'L’organisation', helper: 'Protège les éléments fixes.' },
  { id: 'proposals', title: 'Les idées', helper: 'Compare les compromis.' },
  { id: 'prepare', title: 'La suite', helper: 'Conserve une décision claire.' },
]

const scoreLabels: Record<string, string> = {
  compactness: 'Compacité',
  free_space: 'Espace libre',
  accessibility: 'Accès',
  printability: 'Imprimabilité',
  simplicity: 'Simplicité',
  coverage: 'Couverture',
}

const defaultDimension = (): Dimension => ({ x: 30, y: 30, z: 20 })

export default function App() {
  const [draft, setDraft] = useState<ComposerDraft>()
  const [portfolio, setPortfolio] = useState<Portfolio>()
  const [selectedVariantId, setSelectedVariantId] = useState<string>()
  const [activeStep, setActiveStep] = useState<StepId>('box')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('Chargement de ton atelier…')
  const [error, setError] = useState<string>()
  const [issues, setIssues] = useState<DraftIssue[]>([])
  const [starters, setStarters] = useState<StarterTemplate[]>([])
  const [showStarterPicker, setShowStarterPicker] = useState(false)

  useEffect(() => {
    void loadStarters()
      .then((catalog) => {
        if (!catalog.length) throw new Error('Aucun modèle local n’est disponible.')
        setStarters(catalog)
        setDraft(cloneDraft(catalog[0].draft))
        setMessage('Projet de départ chargé. Commence par vérifier les mesures de la boîte.')
      })
      .catch((reason: unknown) => setError(formatError(reason)))
  }, [])

  const selectedVariant = useMemo(
    () => portfolio?.variants.find((variant) => variant.id === selectedVariantId),
    [portfolio, selectedVariantId],
  )

  const assetOwners = useMemo(() => {
    const owners: Record<string, string[]> = {}
    for (const candidate of draft?.candidates ?? []) {
      for (const assetId of candidate.asset_ids) owners[assetId] = [...(owners[assetId] ?? []), candidate.id]
    }
    return owners
  }, [draft])

  const readiness = useMemo(() => draft ? summarizeDraft(draft) : undefined, [draft])
  const currentStep = studioSteps.find((step) => step.id === activeStep) ?? studioSteps[0]

  async function handleGenerate() {
    if (!draft) return
    const localIssues = validateDraft(draft)
    if (localIssues.length) {
      setIssues(localIssues)
      setError(undefined)
      setMessage(`${localIssues.length} point(s) sont à corriger avant de demander des idées au moteur.`)
      return
    }
    setBusy(true)
    setError(undefined)
    setIssues([])
    try {
      const result = await generatePortfolio(draft)
      setPortfolio(result)
      setSelectedVariantId(result.recommended_variant_id ?? undefined)
      setActiveStep('proposals')
      setMessage(result.recommended_variant_id
        ? `${result.variants.length} organisations ont été comparées. La recommandation est prête à être lue.`
        : 'Aucune organisation complète n’a été trouvée : ajuste les contraintes indiquées.')
    } catch (reason) {
      setError(formatError(reason))
    } finally {
      setBusy(false)
    }
  }

  async function handleExport() {
    if (!draft || !selectedVariant) return
    setBusy(true)
    setError(undefined)
    try {
      const bundle = await createExport(draft, selectedVariant.id)
      downloadJson(`${safeFileName(draft.project_name)}-decision.json`, bundle.selection)
      downloadJson(`${safeFileName(draft.project_name)}-preparation-technique.json`, bundle.cad_ir)
      setMessage('Le dossier de préparation contient des bacs ouverts à vérifier dans Fusion. Il ne confirme ni impression, ni mesure.')
    } catch (reason) {
      setError(formatError(reason))
    } finally {
      setBusy(false)
    }
  }

  function updateDraft(mutator: (value: ComposerDraft) => ComposerDraft) {
    setDraft((current) => (current ? mutator(current) : current))
    setPortfolio(undefined)
    setSelectedVariantId(undefined)
    setIssues([])
  }

  function chooseStarter(starter: StarterTemplate) {
    setDraft(cloneDraft(starter.draft))
    setPortfolio(undefined)
    setSelectedVariantId(undefined)
    setActiveStep('box')
    setIssues([])
    setError(undefined)
    setShowStarterPicker(false)
    setMessage(`Modèle « ${starter.title} » chargé. Vérifie ses mesures avant de chercher une organisation.`)
  }
  function updateAsset(index: number, update: Partial<AssetDraft>) {
    updateDraft((current) => ({
      ...current,
      assets: current.assets.map((asset, position) => position === index ? { ...asset, ...update } : asset),
    }))
  }

  function updateAssetDimension(index: number, axis: keyof Dimension, value: number) {
    updateDraft((current) => ({
      ...current,
      assets: current.assets.map((asset, position) => position === index
        ? { ...asset, dimensions_mm: { ...asset.dimensions_mm, [axis]: value } }
        : asset),
    }))
  }

  function updateCandidate(index: number, update: Partial<CandidateDraft>) {
    updateDraft((current) => ({
      ...current,
      candidates: current.candidates.map((candidate, position) => position === index ? { ...candidate, ...update } : candidate),
    }))
  }

  function updateCandidateDimension(index: number, axis: keyof Dimension, value: number) {
    updateDraft((current) => ({
      ...current,
      candidates: current.candidates.map((candidate, position) => position === index
        ? { ...candidate, size_mm: { ...candidate.size_mm, [axis]: value } }
        : candidate),
    }))
  }

  function updateReservation(index: number, update: Partial<ReservationDraft>) {
    updateDraft((current) => ({
      ...current,
      reservations: current.reservations.map((reservation, position) => position === index ? { ...reservation, ...update } : reservation),
    }))
  }

  function lockSelectedProposal() {
    if (!draft || !selectedVariant) return
    const lockedModules = selectedVariant.solution.solved_plan.modules
      .filter((module) => Boolean(module.metadata?.auto_placed))
      .map(toLockedModule)
    if (!lockedModules.length) {
      setError('Cette idée ne contient aucun emplacement automatique à conserver.')
      return
    }
    updateDraft((current) => ({ ...current, manual_modules: lockedModules, candidates: [] }))
    setMessage('Cette organisation est conservée comme positions fixes. Tu peux ensuite l’enregistrer ou reprendre les réglages experts.')
  }

  async function importDraft(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    try {
      const incoming = JSON.parse(await file.text()) as unknown
      if (!isComposerDraft(incoming)) throw new Error('Ce fichier ne correspond pas à un projet BGIG Studio compatible.')
      const importedIssues = validateDraft(incoming)
      setDraft(incoming)
      setPortfolio(undefined)
      setSelectedVariantId(undefined)
      setActiveStep('box')
      setIssues(importedIssues)
      setMessage(importedIssues.length
        ? `Projet « ${incoming.project_name} » importé : ${importedIssues.length} point(s) sont à compléter.`
        : `Projet « ${incoming.project_name} » importé. Tu peux l’explorer.`)
      setError(undefined)
    } catch (reason) {
      setError(formatError(reason))
    } finally {
      event.target.value = ''
    }
  }

  if (!draft || !readiness) {
    return <main className="loading-shell"><div className="loading-card"><span className="orb" /><p>{error ?? 'Connexion à ton atelier local…'}</p></div></main>
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">B</span><span>BGIG <strong>Studio</strong></span></div>
        <div className="topbar-actions">
          <button className="button quiet" onClick={() => setShowStarterPicker((visible) => !visible)} disabled={!starters.length}>Changer de modèle</button>
          <label className="button quiet"><span>Importer</span><input type="file" accept="application/json" onChange={importDraft} /></label>
          <button className="button secondary" onClick={() => downloadJson(`${safeFileName(draft.project_name)}-projet.json`, draft)}>Sauvegarder</button>
          <button className="button primary" onClick={() => void handleGenerate()} disabled={busy}>{busy ? 'Recherche…' : 'Explorer des idées'}</button>
        </div>
      </header>

      {showStarterPicker && <section className="starter-gallery" aria-label="Modèles de démarrage"><div className="starter-gallery-heading"><div><p className="eyebrow">Nouveau point de départ</p><h2>Choisis un jeu proche du tien</h2><p>Chaque modèle reste local et modifiable. Il sert seulement à démarrer plus vite.</p></div><button className="text-button" onClick={() => setShowStarterPicker(false)}>Fermer</button></div><div className="starter-grid">{starters.map((starter) => <article key={starter.id} className="starter-card"><span className="starter-icon">▦</span><h3>{starter.title}</h3><p>{starter.description}</p><div className="starter-highlights">{starter.highlights.map((highlight) => <span key={highlight}>{highlight}</span>)}</div><button className="button secondary" onClick={() => chooseStarter(starter)}>Utiliser ce modèle</button></article>)}</div></section>}

      <section className="studio-intro">
        <div>
          <p className="eyebrow">Atelier de rangement</p>
          <h1>{draft.project_name || 'Nouveau projet'}</h1>
          <p>Un espace pour organiser ta boîte, comprendre les compromis, puis préparer la suite sans termes techniques ni fausse promesse d’impression.</p>
        </div>
        <ManufacturingStatus selectedVariant={selectedVariant} />
      </section>

      {error && <section className="notice error" aria-live="assertive"><strong>À corriger</strong><span>{error}</span></section>}
      {issues.length > 0 && <section className="notice error" aria-live="polite"><strong>À compléter</strong><ul className="issue-list">{issues.map((issue, index) => <li key={`${issue.path}-${index}`}><b>{issue.path}</b> — {issue.message}</li>)}</ul></section>}
      <section className="notice" aria-live="polite"><strong>Dans ton atelier</strong><span>{message}</span></section>

      <nav className="studio-steps" aria-label="Étapes de conception">
        {studioSteps.map((step, index) => <button key={step.id} type="button" className={step.id === activeStep ? 'active' : ''} onClick={() => setActiveStep(step.id)}><span>{String(index + 1).padStart(2, '0')}</span><b>{step.title}</b><small>{step.helper}</small></button>)}
      </nav>

      <section className="studio-workspace">
        <StudioBoxPreview draft={draft} selectedVariant={selectedVariant} readiness={readiness} />
        <section className="studio-editor" aria-labelledby="current-step-title">
          <div className="step-heading"><span className="step-index">{String(studioSteps.findIndex((step) => step.id === activeStep) + 1).padStart(2, '0')}</span><div><p className="eyebrow">Étape active</p><h2 id="current-step-title">{currentStep.title}</h2><p>{currentStep.helper}</p></div></div>
          {activeStep === 'box' && <section className="editor-card"><div className="card-intro"><h3>Mesure l’intérieur, pas la boîte extérieure</h3><p>Les chiffres ci-dessous mettent à jour la vue à gauche immédiatement. Utilise les dimensions réellement disponibles une fois le couvercle fermé.</p></div><div className="form-grid box-grid"><TextField label="Nom du projet" value={draft.project_name} onChange={(value) => updateDraft((current) => ({ ...current, project_name: value }))} wide /><NumberField label="Largeur interne" value={draft.box.inner_dimensions_mm.x} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, x: value } } }))} /><NumberField label="Profondeur interne" value={draft.box.inner_dimensions_mm.y} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, y: value } } }))} /><NumberField label="Hauteur interne" value={draft.box.inner_dimensions_mm.z} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, z: value } } }))} /><NumberField label="Hauteur réellement exploitable" value={draft.box.usable_height_mm} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, usable_height_mm: value } }))} /><NumberField label="Marge sous le couvercle" value={draft.box.lid_clearance_mm} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, lid_clearance_mm: value } }))} /></div><div className="live-note"><span>↺</span><div><strong>Aperçu vivant</strong><p>Cette vue représente l’espace et les positions connues. Elle ne représente pas encore des bacs imprimables.</p></div></div></section>}

          {activeStep === 'contents' && <section className="editor-card"><div className="card-heading"><div><h3>Ce qui doit vraiment trouver sa place</h3><p>Indique le type, la quantité et l’encombrement d’un élément. Les dimensions peuvent rester approximatives au départ.</p></div><button className="button secondary" onClick={() => updateDraft((current) => ({ ...current, assets: [...current.assets, newAsset(current.assets.length + 1)] }))}>+ Ajouter un élément</button></div><div className="table-wrap"><table><thead><tr><th>Élément</th><th>Type</th><th>Qté</th><th>Largeur</th><th>Profondeur</th><th>Hauteur</th><th>Priorité</th><th /></tr></thead><tbody>{draft.assets.map((asset, index) => <tr key={asset.id}><td><TextInput value={asset.name} onChange={(value) => updateAsset(index, { name: value })} /></td><td><select value={asset.kind} onChange={(event) => updateAsset(index, { kind: event.target.value as AssetDraft['kind'] })}>{assetKinds.map((value) => <option key={value} value={value}>{kindLabel(value)}</option>)}</select></td><td><NumberInput value={asset.quantity.count} onChange={(value) => updateAsset(index, { quantity: { ...asset.quantity, count: value } })} /></td><td><NumberInput value={asset.dimensions_mm.x} onChange={(value) => updateAssetDimension(index, 'x', value)} /></td><td><NumberInput value={asset.dimensions_mm.y} onChange={(value) => updateAssetDimension(index, 'y', value)} /></td><td><NumberInput value={asset.dimensions_mm.z} onChange={(value) => updateAssetDimension(index, 'z', value)} /></td><td><select value={asset.containment_intent} onChange={(event) => updateAsset(index, { containment_intent: event.target.value as AssetDraft['containment_intent'] })}><option value="store">Ranger</option><option value="protect">Protéger</option><option value="separate">Séparer</option><option value="access_first">Accès rapide</option></select></td><td><button className="icon-button" aria-label={`Supprimer ${asset.name}`} onClick={() => updateDraft((current) => ({ ...current, assets: current.assets.filter((_, position) => position !== index) }))}>×</button></td></tr>)}</tbody></table></div><div className="step-actions"><button className="button primary" onClick={() => setActiveStep('organisation')}>Continuer vers l’organisation</button></div></section>}
          {activeStep === 'organisation' && <section className="editor-card"><div className="card-intro"><h3>Garde visibles les contraintes qui comptent</h3><p>La plupart des jeux démarrent avec un modèle et quelques mesures. Les réglages ci-dessous servent lorsque tu dois protéger un livret, un plateau ou contrôler précisément les emplacements.</p></div><details className="expert-disclosure"><summary><span>Réservations fixes</span><small>Livret, plateau, bac existant…</small></summary><div className="disclosure-content"><div className="subpanel-heading"><p>Ces volumes ne seront pas déplacés par les propositions.</p><button className="text-button" onClick={() => updateDraft((current) => ({ ...current, reservations: [...current.reservations, newReservation(current.reservations.length + 1, current.layers[0]?.id ?? 'base')] }))}>+ Ajouter une réservation</button></div>{draft.reservations.length === 0 && <p className="empty-copy">Aucune réservation : la boîte est entièrement disponible.</p>}{draft.reservations.map((reservation, index) => <ReservationEditor key={reservation.id} reservation={reservation} layers={draft.layers.map((layer) => layer.id)} onChange={(update) => updateReservation(index, update)} onDelete={() => updateDraft((current) => ({ ...current, reservations: current.reservations.filter((_, position) => position !== index) }))} />)}</div></details><details className="expert-disclosure"><summary><span>Réglages des bacs envisagés</span><small>Pour guider le moteur, pas pour dessiner une pièce.</small></summary><div className="disclosure-content"><div className="subpanel-heading"><p>Un candidat décrit l’encombrement souhaité d’un futur bac.</p><button className="text-button" onClick={() => updateDraft((current) => ({ ...current, candidates: [...current.candidates, newCandidate(current.candidates.length + 1, current.layers[0]?.id ?? 'base')] }))}>+ Ajouter un bac envisagé</button></div>{draft.candidates.length === 0 && <p className="empty-copy">Aucun réglage avancé. Une décision conservée apparaîtra ici comme position fixe.</p>}{draft.candidates.map((candidate, index) => <CandidateEditor key={candidate.id} candidate={candidate} assets={draft.assets} assetOwners={assetOwners} layers={draft.layers.map((layer) => layer.id)} onChange={(update) => updateCandidate(index, update)} onDimensionChange={(axis, value) => updateCandidateDimension(index, axis, value)} onDelete={() => updateDraft((current) => ({ ...current, candidates: current.candidates.filter((_, position) => position !== index) }))} />)}</div></details>{draft.manual_modules.length > 0 && <div className="lock-strip"><strong>{draft.manual_modules.length} position(s) conservée(s)</strong><span>Elles restent fixes pour la prochaine recherche.</span><button className="text-button" onClick={() => updateDraft((current) => ({ ...current, manual_modules: [] }))}>Tout libérer</button></div>}<div className="step-actions"><button className="button primary" onClick={() => void handleGenerate()} disabled={busy}>{busy ? 'Recherche…' : 'Voir les idées possibles'}</button></div></section>}

          {activeStep === 'proposals' && <section className="editor-card"><div className="card-heading"><div><h3>Choisis un compromis, pas une boîte noire</h3><p>Chaque idée explique ce qu’elle privilégie. Les scores aident à comparer ; ils ne remplacent ni une mesure réelle, ni une impression.</p></div><label className="preference">Ce qui compte le plus<select value={draft.preference} onChange={(event) => updateDraft((current) => ({ ...current, preference: event.target.value as ComposerDraft['preference'] }))}><option value="balanced">Un bon équilibre</option><option value="compact">Prendre le moins de place</option><option value="accessible">Accéder facilement au matériel</option><option value="print_simple">Rester simple à fabriquer</option></select></label></div>{!portfolio && <div className="empty-state"><div className="empty-illustration">✦</div><h3>Prêt à comparer</h3><p>Quand tes mesures sont cohérentes, le moteur peut te proposer plusieurs organisations.</p><button className="button primary" onClick={() => void handleGenerate()} disabled={busy}>{busy ? 'Recherche…' : 'Explorer les idées'}</button></div>}{portfolio && <><div className="portfolio-summary"><span>{portfolio.variants.length} idées comparées</span><span>·</span><span>Priorité : {preferenceLabel(portfolio.preference.id)}</span></div><div className="variant-grid">{portfolio.variants.map((variant) => <VariantCard key={variant.id} variant={variant} active={selectedVariantId === variant.id} onSelect={() => { setSelectedVariantId(variant.id); setActiveStep('prepare') }} />)}</div><details className="limits"><summary>Ce que ces idées ne valident pas encore</summary><ul>{portfolio.limits.map((limit) => <li key={limit}>{limit}</li>)}</ul></details></>}</section>}
          {activeStep === 'prepare' && <section className="editor-card prepare-card"><div className="card-intro"><h3>{selectedVariant ? 'Ton organisation est choisie' : 'Choisis d’abord une idée'}</h3><p>{selectedVariant ? `« ${proposalExplanation(selectedVariant.policy_id).title} » est retenue. Tu peux l’enregistrer comme décision, le téléchargement prépare des bacs ouverts à vérifier dans Fusion.` : 'Reviens à l’étape “Les idées” pour sélectionner une organisation.'}</p></div><div className="manufacturing-path" aria-label="Étapes de fabrication"><div className="active"><span>1</span><strong>À explorer</strong><small>Organisation numérique choisie</small></div><div><span>2</span><strong>À vérifier dans Fusion</strong><small>Après la génération de vrais bacs</small></div><div><span>3</span><strong>À imprimer et mesurer</strong><small>Validation physique nécessaire</small></div></div>{selectedVariant && <div className="prepare-actions"><button className="button secondary" disabled={busy} onClick={lockSelectedProposal}>Conserver cette organisation</button><button className="button primary" onClick={() => downloadJson(`${safeFileName(draft.project_name)}-projet.json`, draft)}>Sauvegarder le projet</button></div>}<details className="technical-download"><summary>Mode expert : télécharger le dossier de préparation</summary><p>Ce téléchargement contient les bacs ouverts et leur dossier technique. Il ne lance aucune scène Fusion et ne valide ni impression ni mesure.</p><button className="button quiet" disabled={!selectedVariant || busy} onClick={() => void handleExport()}>Télécharger le dossier technique</button></details></section>}
        </section>
      </section>
    </main>
  )
}

function ManufacturingStatus({ selectedVariant }: { selectedVariant?: Variant }) {
  return <div className="manufacturing-status"><span className="status-dot" /><div><strong>{selectedVariant ? 'À explorer' : 'Projet en préparation'}</strong><small>{selectedVariant ? 'Des bacs ouverts peuvent être préparés, puis vérifiés dans Fusion.' : 'Ajoute les mesures pour commencer.'}</small></div></div>
}

function StudioBoxPreview({ draft, selectedVariant, readiness }: { draft: ComposerDraft; selectedVariant?: Variant; readiness: ReturnType<typeof summarizeDraft> }) {
  const width = Math.max(1, draft.box.inner_dimensions_mm.x)
  const depth = Math.max(1, draft.box.inner_dimensions_mm.y)
  const plan = selectedVariant?.solution.solved_plan
  const reservations = plan ? plan.reservations : draft.reservations
  const modules = plan ? plan.modules : draft.manual_modules
  const capacity = Math.max(0, width * depth * Math.max(0, draft.box.usable_height_mm))
  const listedVolume = draft.assets.reduce((sum, asset) => sum + Math.max(0, asset.dimensions_mm.x * asset.dimensions_mm.y * asset.dimensions_mm.z * asset.quantity.count), 0)
  const estimatedFill = capacity > 0 ? Math.min(100, Math.round((listedVolume / capacity) * 100)) : 0
  return <aside className="box-preview-panel" aria-label="Aperçu vivant de la boîte"><div className="preview-heading"><div><p className="eyebrow">Vue vivante</p><h2>Ta boîte, maintenant</h2></div><span className="preview-tag">Plan 2D</span></div><div className="box-canvas"><svg viewBox={`0 0 ${width} ${depth}`} role="img" aria-label="Vue de dessus de la boîte"><rect width={width} height={depth} className="box-fill" />{reservations.map((entry) => <rect key={entry.id} x={entry.origin_mm.x} y={depth - entry.origin_mm.y - entry.size_mm.y} width={entry.size_mm.x} height={entry.size_mm.y} className="reservation-fill" />)}{modules.map((module) => <g key={module.id}><rect x={module.origin_mm.x} y={depth - module.origin_mm.y - module.size_mm.y} width={module.size_mm.x} height={module.size_mm.y} rx={Math.min(module.size_mm.x, module.size_mm.y) * .04} className={module.locked ? 'module-fill locked' : 'module-fill'} /><text x={module.origin_mm.x + 3} y={depth - module.origin_mm.y - 4}>{module.name}</text></g>)}</svg>{modules.length === 0 && <div className="canvas-empty"><span>+</span><p>Les emplacements apparaîtront ici quand tu choisiras une idée.</p></div>}</div><div className="preview-legend"><span><i className="legend-reservation" />À garder libre</span><span><i className="legend-module" />Organisation choisie</span></div><div className="preview-metrics"><div><span>Espace utile</span><strong>{formatVolume(capacity)}</strong><small>{formatDimension(draft.box.inner_dimensions_mm)}</small></div><div><span>Contenu déclaré</span><strong>{draft.assets.length} élément{draft.assets.length > 1 ? 's' : ''}</strong><small>{estimatedFill}% du volume estimé</small></div><div><span>Préparation</span><strong>{readiness.issues.length ? 'À compléter' : 'Prêt à explorer'}</strong><small>{readiness.reservation_count} zone(s) protégée(s)</small></div></div><p className="preview-disclaimer">Cet aperçu reste une carte de rangement. Son export prépare des bacs ouverts ; Fusion puis une impression réelle restent à vérifier.</p></aside>
}
function VariantCard({ variant, active, onSelect }: { variant: Variant; active: boolean; onSelect: () => void }) {
  const explanation = proposalExplanation(variant.policy_id)
  return <article className={`variant-card ${active ? 'active' : ''}`}><div className="variant-card-header"><div><span className={`pill ${variant.recommended ? 'recommended' : ''}`}>{variant.recommended ? 'Recommandée' : variant.pareto ? 'Alternative solide' : 'Alternative'}</span><h3>{explanation.title}</h3></div><button className="select-button" onClick={onSelect}>{active ? 'Choisie' : 'Choisir'}</button></div><p className="variant-intent">{explanation.intent}</p><LayoutPreview variant={variant} /><div className="variant-advice"><div><strong>Bien si tu veux</strong><span>{explanation.choose_if}</span></div><div><strong>À surveiller</strong><span>{explanation.watch_for}</span></div></div><div className="score-line"><strong>{formatScore(variant.weighted_score)}</strong><span>selon ta priorité</span></div><div className="score-grid">{Object.entries(variant.subscores).map(([key, score]) => <div key={key}><span>{scoreLabels[key] ?? key}</span><small>{scoreExplanation(key)}</small><meter min="0" max="1" value={score} /><b>{formatScore(score)}</b></div>)}</div><details className="engine-note"><summary>Détails pour expert</summary><ul>{variant.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></details></article>
}

function LayoutPreview({ variant }: { variant: Variant }) {
  const plan = variant.solution.solved_plan
  const layer = plan.layers[0]
  const width = Math.max(1, plan.box.inner_dimensions_mm.x)
  const height = Math.max(1, plan.box.inner_dimensions_mm.y)
  const reservations = plan.reservations.filter((entry) => entry.layer_id === layer?.id)
  const modules = plan.modules.filter((entry) => entry.layer_id === layer?.id)
  return <div className="layout-preview"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Plan de la proposition ${variant.policy_id}`}><rect width={width} height={height} className="box-fill" />{reservations.map((entry) => <rect key={entry.id} x={entry.origin_mm.x} y={height - entry.origin_mm.y - entry.size_mm.y} width={entry.size_mm.x} height={entry.size_mm.y} className="reservation-fill" />)}{modules.map((module) => <g key={module.id}><rect x={module.origin_mm.x} y={height - module.origin_mm.y - module.size_mm.y} width={module.size_mm.x} height={module.size_mm.y} className={module.locked ? 'module-fill locked' : 'module-fill'} /><text x={module.origin_mm.x + 3} y={height - module.origin_mm.y - 4}>{module.name}</text></g>)}</svg><span>{layer ? `Niveau · ${layer.id}` : 'Vue de dessus'}</span></div>
}

function ReservationEditor({ reservation, layers, onChange, onDelete }: { reservation: ReservationDraft; layers: string[]; onChange: (update: Partial<ReservationDraft>) => void; onDelete: () => void }) {
  return <div className="compact-editor"><div className="compact-top"><TextInput value={reservation.id} onChange={(value) => onChange({ id: value })} /><select value={reservation.kind} onChange={(event) => onChange({ kind: event.target.value as ReservationDraft['kind'] })}><option value="rulebook">Livret</option><option value="board">Plateau</option><option value="existing_tray">Bac existant</option><option value="generic">Réserve</option></select><select value={reservation.layer_id} onChange={(event) => onChange({ layer_id: event.target.value })}>{layers.map((layer) => <option key={layer}>{layer}</option>)}</select><button className="icon-button" aria-label="Supprimer la réservation" onClick={onDelete}>×</button></div><DimensionEditor label="Origine" value={reservation.origin_mm} onChange={(value) => onChange({ origin_mm: value })} /><DimensionEditor label="Taille" value={reservation.size_mm} onChange={(value) => onChange({ size_mm: value })} /></div>
}

function CandidateEditor({ candidate, assets, assetOwners, layers, onChange, onDimensionChange, onDelete }: { candidate: CandidateDraft; assets: AssetDraft[]; assetOwners: Record<string, string[]>; layers: string[]; onChange: (update: Partial<CandidateDraft>) => void; onDimensionChange: (axis: keyof Dimension, value: number) => void; onDelete: () => void }) {
  function toggleAsset(assetId: string, checked: boolean) {
    const assetIds = checked ? Array.from(new Set([...candidate.asset_ids, assetId])) : candidate.asset_ids.filter((current) => current !== assetId)
    onChange({ asset_ids: assetIds })
  }

  return <div className="compact-editor"><div className="compact-top"><TextInput value={candidate.name} onChange={(value) => onChange({ name: value })} /><select value={candidate.allowed_layers[0] ?? ''} onChange={(event) => onChange({ allowed_layers: [event.target.value] })}>{layers.map((layer) => <option key={layer}>{layer}</option>)}</select><label className="check"><input type="checkbox" checked={candidate.allow_xy_rotation} onChange={(event) => onChange({ allow_xy_rotation: event.target.checked })} /> Rotation</label><button className="icon-button" aria-label="Supprimer le bac envisagé" onClick={onDelete}>×</button></div><div className="candidate-details"><DimensionEditor label="Dimensions" value={candidate.size_mm} onChange={(value) => { onDimensionChange('x', value.x); onDimensionChange('y', value.y); onDimensionChange('z', value.z) }} /><div className="asset-picker"><div className="asset-picker-heading"><span>Éléments associés</span><small>{candidate.asset_ids.length ? `${candidate.asset_ids.length} sélectionné(s)` : 'Aucun élément'}</small></div>{assets.map((asset) => { const checked = candidate.asset_ids.includes(asset.id); const usedByOther = (assetOwners[asset.id] ?? []).some((ownerId) => ownerId !== candidate.id); return <label key={asset.id} className={`asset-option ${usedByOther ? 'assigned-elsewhere' : ''}`}><input type="checkbox" checked={checked} disabled={usedByOther && !checked} onChange={(event) => toggleAsset(asset.id, event.target.checked)} /><span>{asset.name}</span>{usedByOther && !checked && <small>Déjà associé ailleurs</small>}</label> })}</div></div></div>
}
function DimensionEditor({ label, value, onChange }: { label: string; value: Dimension | { x: number; y: number; z: number }; onChange: (value: Dimension) => void }) {
  return <div className="dimension-editor"><span>{label}</span><NumberInput value={value.x} onChange={(next) => onChange({ ...value, x: next })} /><NumberInput value={value.y} onChange={(next) => onChange({ ...value, y: next })} /><NumberInput value={value.z} onChange={(next) => onChange({ ...value, z: next })} /></div>
}

function TextField({ label, value, onChange, wide = false }: { label: string; value: string; onChange: (value: string) => void; wide?: boolean }) {
  return <label className={`field ${wide ? 'wide' : ''}`}><span>{label}</span><TextInput value={value} onChange={onChange} /></label>
}

function NumberField({ label, value, suffix, onChange }: { label: string; value: number; suffix?: string; onChange: (value: number) => void }) {
  return <label className="field"><span>{label}</span><div className="number-with-suffix"><NumberInput value={value} onChange={onChange} />{suffix && <i>{suffix}</i>}</div></label>
}

function TextInput({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return <input value={value} onChange={(event) => onChange(event.target.value)} />
}

function NumberInput({ value, onChange }: { value: number; onChange: (value: number) => void }) {
  return <input type="number" min="0" step="0.1" value={Number.isFinite(value) ? value : 0} onChange={(event) => onChange(Number(event.target.value))} />
}

function cloneDraft(draft: ComposerDraft): ComposerDraft {
  return JSON.parse(JSON.stringify(draft)) as ComposerDraft
}

function newAsset(index: number): AssetDraft {
  return { id: `asset-${index}`, name: 'Nouvel élément', kind: 'other', quantity: { count: 1, grouping: 'single' }, dimensions_mm: defaultDimension(), containment_intent: 'store', dimension_confidence: 'approximate' }
}

function newCandidate(index: number, layerId: string): CandidateDraft {
  return { id: `module-${index}`, name: 'Nouveau bac', size_mm: defaultDimension(), allowed_layers: [layerId], allow_xy_rotation: true, priority: 0, asset_ids: [] }
}

function newReservation(index: number, layerId: string): ReservationDraft {
  return { id: `reservation-${index}`, kind: 'generic', origin_mm: { x: 0, y: 0, z: 0 }, size_mm: defaultDimension(), layer_id: layerId }
}

function toLockedModule(module: EngineModule) {
  return { id: module.id, name: module.name, origin_mm: module.origin_mm, size_mm: module.size_mm, layer_id: module.layer_id ?? 'base', locked: true }
}

function downloadJson(fileName: string, value: unknown) {
  const blob = new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  anchor.click()
  URL.revokeObjectURL(url)
}

function safeFileName(value: string) {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/gi, '-').replace(/(^-|-$)/g, '') || 'bgig-project'
}

function formatScore(value: number) { return `${Math.round(value * 100)}%` }
function formatVolume(value: number) { return `${Math.round(value / 1000).toLocaleString('fr-FR')} cm³` }
function formatDimension(value: Dimension) { return `${value.x} × ${value.y} × ${value.z} mm` }
function formatError(reason: unknown) {
  if (reason instanceof ApiError) {
    if (reason.code === 'DRAFT_INVALID') return `Le projet a un point à corriger : ${reason.message}`
    if (reason.code === 'ENGINE_REJECTED') return `Le moteur refuse ce projet : ${reason.message}`
  }
  return reason instanceof Error ? reason.message : 'Une erreur inconnue est survenue.'
}
function preferenceLabel(preference: string) { return ({ balanced: 'Un bon équilibre', compact: 'Compacité', accessible: 'Accès facile', print_simple: 'Simplicité de fabrication' } as Record<string, string>)[preference] ?? preference }
function kindLabel(kind: AssetDraft['kind']) { return ({ cards: 'Cartes', tokens: 'Jetons', dice: 'Dés', meeples: 'Figurines', other: 'Autre' } as Record<AssetDraft['kind'], string>)[kind] }
const assetKinds: AssetDraft['kind'][] = ['cards', 'tokens', 'dice', 'meeples', 'other']