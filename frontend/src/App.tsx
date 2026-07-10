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
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('Chargement du projet de départ…')
  const [error, setError] = useState<string>()
  const [issues, setIssues] = useState<DraftIssue[]>([])
  const [starters, setStarters] = useState<StarterTemplate[]>([])
  const [showStarterPicker, setShowStarterPicker] = useState(false)

  useEffect(() => {
    void loadStarters()
      .then((catalog) => {
        if (!catalog.length) throw new Error('Aucun modele local est disponible.')
        setStarters(catalog)
        setDraft(cloneDraft(catalog[0].draft))
        setMessage('Projet de depart charge. Modifie les donnees, puis genere des propositions.')
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

  async function handleGenerate() {
    if (!draft) return
    const localIssues = validateDraft(draft)
    if (localIssues.length) {
      setIssues(localIssues)
      setError(undefined)
      setMessage(`${localIssues.length} point(s) sont \u00e0 corriger avant de demander des propositions au moteur.`)
      return
    }
    setBusy(true)
    setError(undefined)
    setIssues([])
    try {
      const result = await generatePortfolio(draft)
      setPortfolio(result)
      setSelectedVariantId(result.recommended_variant_id ?? undefined)
      setMessage(result.recommended_variant_id ? `${result.variants.length} propositions compar\u00e9es. La recommandation est pr\u00eate \u00e0 \u00eatre inspect\u00e9e.` : 'Aucune proposition compl\u00e8te : lis les raisons de refus et ajuste les contraintes.')
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
      downloadJson(`${safeFileName(draft.project_name)}-selection.json`, bundle.selection)
      downloadJson(`${safeFileName(draft.project_name)}-selected-cad-ir.json`, bundle.cad_ir)
      setMessage('La sélection et sa CAD IR ont été téléchargées. Aucune génération Fusion n’a été exécutée.')
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
    setIssues([])
    setError(undefined)
    setShowStarterPicker(false)
    setMessage(`Modele \u00ab ${starter.title} \u00bb charge. Ajuste les mesures reelles avant de generer.`)
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
      setError('Cette proposition ne contient aucun module automatique à verrouiller.')
      return
    }
    updateDraft((current) => ({ ...current, manual_modules: lockedModules, candidates: [] }))
    setMessage('La proposition est figée comme modules verrouillés. Tu peux la sauvegarder ou réintroduire des candidats ensuite.')
  }

  async function importDraft(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    try {
      const incoming = JSON.parse(await file.text()) as unknown
      if (!isComposerDraft(incoming)) throw new Error('Ce fichier ne respecte pas la structure du projet BGIG Local Composer V0.')
      const importedIssues = validateDraft(incoming)
      setDraft(incoming)
      setPortfolio(undefined)
      setSelectedVariantId(undefined)
      setIssues(importedIssues)
      setMessage(importedIssues.length ? `Projet \u00ab ${incoming.project_name} \u00bb import\u00e9 : corrige ${importedIssues.length} point(s) avant la g\u00e9n\u00e9ration.` : `Projet \u00ab ${incoming.project_name} \u00bb import\u00e9. G\u00e9n\u00e8re les propositions pour le v\u00e9rifier.`)
      setError(undefined)
    } catch (reason) {
      setError(formatError(reason))
    } finally {
      event.target.value = ''
    }
  }

  if (!draft || !readiness) {
    return <main className="loading-shell"><div className="loading-card"><span className="orb" /><p>{error ?? 'Connexion au moteur local…'}</p></div></main>
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">B</span><span>BGIG <strong>Studio</strong></span></div>
        <div className="topbar-actions">
          <button className="button secondary" onClick={() => setShowStarterPicker((visible) => !visible)} disabled={!starters.length}>{'Choisir un mod\u00e8le'}</button>
          <label className="button secondary"><span>Importer un projet</span><input type="file" accept="application/json" onChange={importDraft} /></label>
          <button className="button secondary" onClick={() => downloadJson(`${safeFileName(draft.project_name)}-draft.json`, draft)}>Sauvegarder le projet</button>
          <button className="button primary" onClick={() => void handleGenerate()} disabled={busy}>Générer les propositions</button>
        </div>
      </header>

      {showStarterPicker && <section className="starter-gallery" aria-label="Modeles de demarrage"><div className="starter-gallery-heading"><div><p className="eyebrow">Choisir un point de depart</p><h2>{'Pars d un mod\u00e8le, puis mesure ta vraie bo\u00eete'}</h2><p>Chaque modele est local, modifiable et reste une hypothese a verifier dans ta boite.</p></div><button className="text-button" onClick={() => setShowStarterPicker(false)}>Fermer</button></div><div className="starter-grid">{starters.map((starter) => <article key={starter.id} className="starter-card"><h3>{starter.title}</h3><p>{starter.description}</p><div className="starter-highlights">{starter.highlights.map((highlight) => <span key={highlight}>{highlight}</span>)}</div><button className="button secondary" onClick={() => chooseStarter(starter)}>{'Utiliser ce mod\u00e8le'}</button></article>)}</div></section>}

      <section className="hero">
        <div>
          <p className="eyebrow">Concevoir un rangement, pas une scène CAD</p>
          <h1>{draft.project_name || 'Nouveau projet'}</h1>
          <p className="hero-copy">Décris la boîte et ce qu’elle contient. BGIG compare des propositions explicables, puis te laisse exporter une décision — jamais une promesse d’impression.</p>
        </div>
        <div className="hero-status"><span className="status-dot" /> Moteur local connecté · mm · hors Fusion</div>
      </section>

      {error && <section className="notice error" aria-live="assertive"><strong>{'\u00c0 corriger'}</strong><span>{error}</span></section>}
      {issues.length > 0 && <section className="notice error" aria-live="polite"><strong>{'\u00c0 compl\u00e9ter'}</strong><ul className="issue-list">{issues.map((issue, index) => <li key={`${issue.path}-${index}`}><b>{issue.path}</b> {'\u2014'} {issue.message}</li>)}</ul></section>}
      <section className="notice" aria-live="polite"><strong>{'\u00c9tat'}</strong><span>{message}</span></section>

      <nav className="journey" aria-label="Parcours de conception">
        <a href="#box">01 <span>Boîte</span></a><a href="#assets">02 <span>Contenu</span></a><a href="#constraints">03 <span>Contraintes</span></a><a href="#proposals">04 <span>Propositions</span></a><a href="#export">05 <span>Exporter</span></a>
      </nav>

      <section id="box" className="panel split-panel">
        <div><p className="eyebrow">01 · la boîte réelle</p><h2>Définis le volume utile</h2><p>Commence par l’intérieur mesuré. Les tolérances avancées restent disponibles dans les fichiers experts, sans alourdir cette étape.</p></div>
        <div className="form-grid box-grid">
          <TextField label="Nom du projet" value={draft.project_name} onChange={(value) => updateDraft((current) => ({ ...current, project_name: value }))} wide />
          <NumberField label="Largeur interne" value={draft.box.inner_dimensions_mm.x} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, x: value } } }))} />
          <NumberField label="Profondeur interne" value={draft.box.inner_dimensions_mm.y} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, y: value } } }))} />
          <NumberField label="Hauteur interne" value={draft.box.inner_dimensions_mm.z} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, z: value } } }))} />
          <NumberField label="Hauteur exploitable" value={draft.box.usable_height_mm} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, usable_height_mm: value } }))} />
          <NumberField label="Marge couvercle" value={draft.box.lid_clearance_mm} suffix="mm" onChange={(value) => updateDraft((current) => ({ ...current, box: { ...current.box, lid_clearance_mm: value } }))} />
        </div>
      </section>

      <section id="assets" className="panel">
        <div className="panel-heading"><div><p className="eyebrow">02 · le contenu réel</p><h2>Inventorie ce qui doit être rangé</h2><p>Chaque asset reste lisible, mesurable et relié à une intention de rangement.</p></div><button className="button secondary" onClick={() => updateDraft((current) => ({ ...current, assets: [...current.assets, newAsset(current.assets.length + 1)] }))}>+ Ajouter un asset</button></div>
        <div className="table-wrap"><table><thead><tr><th>Nom</th><th>Type</th><th>Qté</th><th>X</th><th>Y</th><th>Z</th><th>Intention</th><th /></tr></thead><tbody>
          {draft.assets.map((asset, index) => <tr key={asset.id}>
            <td><TextInput value={asset.name} onChange={(value) => updateAsset(index, { name: value })} /></td>
            <td><select value={asset.kind} onChange={(event) => updateAsset(index, { kind: event.target.value as AssetDraft['kind'] })}>{assetKinds.map((value) => <option key={value} value={value}>{kindLabel(value)}</option>)}</select></td>
            <td><NumberInput value={asset.quantity.count} onChange={(value) => updateAsset(index, { quantity: { ...asset.quantity, count: value } })} /></td>
            <td><NumberInput value={asset.dimensions_mm.x} onChange={(value) => updateAssetDimension(index, 'x', value)} /></td>
            <td><NumberInput value={asset.dimensions_mm.y} onChange={(value) => updateAssetDimension(index, 'y', value)} /></td>
            <td><NumberInput value={asset.dimensions_mm.z} onChange={(value) => updateAssetDimension(index, 'z', value)} /></td>
            <td><select value={asset.containment_intent} onChange={(event) => updateAsset(index, { containment_intent: event.target.value as AssetDraft['containment_intent'] })}><option value="store">Ranger</option><option value="protect">Protéger</option><option value="separate">Séparer</option><option value="access_first">Accès rapide</option></select></td>
            <td><button className="icon-button" aria-label={`Supprimer ${asset.name}`} onClick={() => updateDraft((current) => ({ ...current, assets: current.assets.filter((_, position) => position !== index) }))}>×</button></td>
          </tr>)}
        </tbody></table></div>
      </section>

      <section id="constraints" className="panel constraints-panel">
        <div className="panel-heading"><div><p className="eyebrow">03 · les contraintes utiles</p><h2>Réserve ce qui ne s’imprime pas, puis définis les bacs possibles</h2><p>Une réservation protège un livret, un plateau ou un bac existant. Un candidat est un module que le moteur peut placer.</p></div></div>
        <div className="constraint-columns">
          <div className="subpanel"><div className="subpanel-heading"><h3>Réservations</h3><button className="text-button" onClick={() => updateDraft((current) => ({ ...current, reservations: [...current.reservations, newReservation(current.reservations.length + 1, current.layers[0]?.id ?? 'base')] }))}>+ Ajouter</button></div>
            {draft.reservations.length === 0 && <p className="empty-copy">Aucune. Ajoute les livrets, plateaux ou volumes non imprimables.</p>}
            {draft.reservations.map((reservation, index) => <ReservationEditor key={reservation.id} reservation={reservation} layers={draft.layers.map((layer) => layer.id)} onChange={(update) => updateReservation(index, update)} onDelete={() => updateDraft((current) => ({ ...current, reservations: current.reservations.filter((_, position) => position !== index) }))} />)}
          </div>
          <div className="subpanel"><div className="subpanel-heading"><h3>Modules candidats</h3><button className="text-button" onClick={() => updateDraft((current) => ({ ...current, candidates: [...current.candidates, newCandidate(current.candidates.length + 1, current.layers[0]?.id ?? 'base')] }))}>+ Ajouter</button></div>
            {draft.candidates.length === 0 && <p className="empty-copy">Aucun candidat actif. Une proposition verrouillée peut être exportée telle quelle.</p>}
            {draft.candidates.map((candidate, index) => <CandidateEditor key={candidate.id} candidate={candidate} assets={draft.assets} assetOwners={assetOwners} layers={draft.layers.map((layer) => layer.id)} onChange={(update) => updateCandidate(index, update)} onDimensionChange={(axis, value) => updateCandidateDimension(index, axis, value)} onDelete={() => updateDraft((current) => ({ ...current, candidates: current.candidates.filter((_, position) => position !== index) }))} />)}
          </div>
        </div>
        {draft.manual_modules.length > 0 && <div className="lock-strip"><strong>{draft.manual_modules.length} module(s) verrouillé(s)</strong><span>Ils restent des obstacles fixes pour toute future génération.</span><button className="text-button" onClick={() => updateDraft((current) => ({ ...current, manual_modules: [] }))}>Déverrouiller tout</button></div>}
      </section>

      <section className="readiness-panel" aria-label="Resume de preparation"><div className="readiness-heading"><div><p className="eyebrow">Avant de generer</p><h2>{'Verifie la pr\u00e9paration du projet'}</h2><p>Ce resume relit ta saisie. Il ne remplace ni le moteur, ni une mesure reelle, ni un test d impression.</p></div><span className={`readiness-badge ${readiness.issues.length ? 'needs-attention' : 'ready'}`}>{readiness.issues.length ? `${readiness.issues.length} point(s) \u00e0 corriger` : 'Pret a explorer'}</span></div><div className="readiness-grid"><div><span>Contenu</span><strong>{readiness.asset_count} asset(s)</strong><small>{readiness.allocated_asset_count}/{readiness.asset_count} associe(s) aux candidats</small></div><div><span>Modules</span><strong>{readiness.candidate_count} candidat(s)</strong><small>{readiness.fixed_module_count} verrouille(s)</small></div><div><span>Contraintes</span><strong>{readiness.reservation_count} reservation(s)</strong><small>{readiness.layer_count} layer(s) declares</small></div></div>{readiness.issues.length > 0 ? <div className="readiness-alert"><strong>{'A completer avant le moteur'}</strong><ul>{readiness.issues.slice(0, 3).map((issue, index) => <li key={`${issue.path}-${index}`}>{issue.path} : {issue.message}</li>)}</ul>{readiness.issues.length > 3 && <small>{`Et ${readiness.issues.length - 3} autre(s) point(s) dans la liste de corrections.`}</small>}</div> : <div className="readiness-ok"><strong>{'Saisie coherente pour demander des propositions'}</strong><span>{readiness.unallocated_asset_names.length ? `Assets encore sans candidat : ${readiness.unallocated_asset_names.join(', ')}` : 'Les assets declaratifs sont associes a des modules candidats.'}</span></div>}<p className="readiness-limit">Les propositions P21 restent des compromis explicables : elles ne valident pas une impression, l ergonomie ou Fusion.</p></section>      <section id="proposals" className="panel proposals-panel">
        <div className="panel-heading"><div><p className="eyebrow">04 · décider en confiance</p><h2>Compare les propositions</h2><p>Les scores restent des proxies. Chaque proposition est déterministe, inspectable et ne contient aucune recherche opaque.</p></div><div className="preference"><label>Priorité personnelle<select value={draft.preference} onChange={(event) => updateDraft((current) => ({ ...current, preference: event.target.value as ComposerDraft['preference'] }))}><option value="balanced">Équilibre</option><option value="compact">Compacité</option><option value="accessible">Accès</option><option value="print_simple">Simplicité d’impression</option></select></label></div></div>
        {!portfolio && <div className="empty-state"><div className="empty-illustration">✦</div><h3>Prêt à explorer</h3><p>Génère des propositions pour voir la boîte, les réservations et les compromis.</p><button className="button primary" onClick={() => void handleGenerate()} disabled={busy}>Générer maintenant</button></div>}
        {portfolio && <><div className="portfolio-summary"><span>{portfolio.variants.length} variantes</span><span>·</span><span>Préférence : {preferenceLabel(portfolio.preference.id)}</span><span>·</span><code>{portfolio.portfolio_digest.slice(0, 12)}</code></div><div className="variant-grid">{portfolio.variants.map((variant) => <VariantCard key={variant.id} variant={variant} active={selectedVariantId === variant.id} onSelect={() => setSelectedVariantId(variant.id)} />)}</div>
          <details className="limits"><summary>Ce que le moteur ne prétend pas valider</summary><ul>{portfolio.limits.map((limit) => <li key={limit}>{limit}</li>)}</ul></details></>}
      </section>

      <section id="export" className="panel export-panel">
        <div><p className="eyebrow">05 · exporter une décision</p><h2>{selectedVariant ? 'La sélection est prête' : 'Sélectionne une proposition'}</h2><p>{selectedVariant ? `« ${selectedVariant.policy_id} » est sélectionnée. Son plan reste traçable avant toute étape CAD.` : 'Choisis une carte de proposition. Tu pourras la figer ou la télécharger avec sa CAD IR.'}</p></div>
        <div className="export-actions"><button className="button secondary" disabled={!selectedVariant || busy} onClick={lockSelectedProposal}>Verrouiller cette proposition</button><button className="button primary" disabled={!selectedVariant || busy} onClick={() => void handleExport()}>Télécharger sélection + CAD IR</button></div>
      </section>
    </main>
  )
}

function VariantCard({ variant, active, onSelect }: { variant: Variant; active: boolean; onSelect: () => void }) {
  const explanation = proposalExplanation(variant.policy_id)
  return <article className={`variant-card ${active ? 'active' : ''}`}><div className="variant-card-header"><div><span className={`pill ${variant.recommended ? 'recommended' : ''}`}>{variant.recommended ? 'Recommand\u00e9e' : variant.pareto ? 'Pareto' : 'Alternative'}</span><h3>{explanation.title}</h3></div><button className="select-button" onClick={onSelect}>{active ? 'Selectionn\u00e9e' : 'Choisir'}</button></div><p className="variant-intent">{explanation.intent}</p><LayoutPreview variant={variant} /><div className="variant-advice"><div><strong>{'A choisir si'}</strong><span>{explanation.choose_if}</span></div><div><strong>{'A surveiller'}</strong><span>{explanation.watch_for}</span></div></div><div className="score-line"><strong>{formatScore(variant.weighted_score)}</strong><span>score selon ta preference</span></div><div className="score-grid">{Object.entries(variant.subscores).map(([key, score]) => <div key={key}><span>{scoreLabels[key] ?? key}</span><small>{scoreExplanation(key)}</small><meter min="0" max="1" value={score} /><b>{formatScore(score)}</b></div>)}</div><details className="engine-note"><summary>Trace technique du moteur</summary><ul>{variant.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></details></article>
}

function LayoutPreview({ variant }: { variant: Variant }) {
  const plan = variant.solution.solved_plan
  const layer = plan.layers[0]
  const width = plan.box.inner_dimensions_mm.x
  const height = plan.box.inner_dimensions_mm.y
  const reservations = plan.reservations.filter((entry) => entry.layer_id === layer?.id)
  const modules = plan.modules.filter((entry) => entry.layer_id === layer?.id)
  return <div className="layout-preview"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Plan de la variante ${variant.policy_id}`}><rect width={width} height={height} className="box-fill" />{reservations.map((entry) => <rect key={entry.id} x={entry.origin_mm.x} y={height - entry.origin_mm.y - entry.size_mm.y} width={entry.size_mm.x} height={entry.size_mm.y} className="reservation-fill" />)}{modules.map((module) => <g key={module.id}><rect x={module.origin_mm.x} y={height - module.origin_mm.y - module.size_mm.y} width={module.size_mm.x} height={module.size_mm.y} className={module.locked ? 'module-fill locked' : 'module-fill'} /><text x={module.origin_mm.x + 3} y={height - module.origin_mm.y - 4}>{module.name}</text></g>)}</svg><span>{layer ? `Layer · ${layer.id}` : 'Vue XY'}</span></div>
}

function ReservationEditor({ reservation, layers, onChange, onDelete }: { reservation: ReservationDraft; layers: string[]; onChange: (update: Partial<ReservationDraft>) => void; onDelete: () => void }) {
  return <div className="compact-editor"><div className="compact-top"><TextInput value={reservation.id} onChange={(value) => onChange({ id: value })} /><select value={reservation.kind} onChange={(event) => onChange({ kind: event.target.value as ReservationDraft['kind'] })}><option value="rulebook">Livret</option><option value="board">Plateau</option><option value="existing_tray">Bac existant</option><option value="generic">Réserve</option></select><select value={reservation.layer_id} onChange={(event) => onChange({ layer_id: event.target.value })}>{layers.map((layer) => <option key={layer}>{layer}</option>)}</select><button className="icon-button" aria-label="Supprimer la réservation" onClick={onDelete}>×</button></div><DimensionEditor label="Origine" value={reservation.origin_mm} onChange={(value) => onChange({ origin_mm: value })} /><DimensionEditor label="Taille" value={reservation.size_mm} onChange={(value) => onChange({ size_mm: value })} /></div>
}

function CandidateEditor({ candidate, assets, assetOwners, layers, onChange, onDimensionChange, onDelete }: { candidate: CandidateDraft; assets: AssetDraft[]; assetOwners: Record<string, string[]>; layers: string[]; onChange: (update: Partial<CandidateDraft>) => void; onDimensionChange: (axis: keyof Dimension, value: number) => void; onDelete: () => void }) {
  function toggleAsset(assetId: string, checked: boolean) {
    const assetIds = checked ? Array.from(new Set([...candidate.asset_ids, assetId])) : candidate.asset_ids.filter((current) => current !== assetId)
    onChange({ asset_ids: assetIds })
  }

  return <div className="compact-editor"><div className="compact-top"><TextInput value={candidate.name} onChange={(value) => onChange({ name: value })} /><select value={candidate.allowed_layers[0] ?? ''} onChange={(event) => onChange({ allowed_layers: [event.target.value] })}>{layers.map((layer) => <option key={layer}>{layer}</option>)}</select><label className="check"><input type="checkbox" checked={candidate.allow_xy_rotation} onChange={(event) => onChange({ allow_xy_rotation: event.target.checked })} /> Rotation</label><button className="icon-button" aria-label="Supprimer le module candidat" onClick={onDelete}>×</button></div><div className="candidate-details"><DimensionEditor label="Dimensions" value={candidate.size_mm} onChange={(value) => { onDimensionChange('x', value.x); onDimensionChange('y', value.y); onDimensionChange('z', value.z) }} /><div className="asset-picker"><div className="asset-picker-heading"><span>{'Assets associ\u00e9s'}</span><small>{candidate.asset_ids.length ? `${candidate.asset_ids.length} s\u00e9lectionn\u00e9(s)` : 'Aucun asset'}</small></div>{assets.map((asset) => { const checked = candidate.asset_ids.includes(asset.id); const usedByOther = (assetOwners[asset.id] ?? []).some((ownerId) => ownerId !== candidate.id); return <label key={asset.id} className={`asset-option ${usedByOther ? 'assigned-elsewhere' : ''}`}><input type="checkbox" checked={checked} disabled={usedByOther && !checked} onChange={(event) => toggleAsset(asset.id, event.target.checked)} /><span>{asset.name}</span>{usedByOther && !checked && <small>{'D\u00e9j\u00e0 affect\u00e9 ailleurs'}</small>}</label> })}</div></div></div>
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
  return { id: `asset-${index}`, name: 'Nouvel asset', kind: 'other', quantity: { count: 1, grouping: 'single' }, dimensions_mm: defaultDimension(), containment_intent: 'store', dimension_confidence: 'approximate' }
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
function formatError(reason: unknown) {
  if (reason instanceof ApiError) {
    if (reason.code === 'DRAFT_INVALID') return `Le moteur a trouve un point a corriger : ${reason.message}`
    if (reason.code === 'ENGINE_REJECTED') return `Le moteur refuse ce projet : ${reason.message}`
  }
  return reason instanceof Error ? reason.message : 'Une erreur inconnue est survenue.'
}
function preferenceLabel(preference: string) { return ({ balanced: 'Équilibre', compact: 'Compacité', accessible: 'Accès', print_simple: 'Simplicité d’impression' } as Record<string, string>)[preference] ?? preference }
function kindLabel(kind: AssetDraft['kind']) { return ({ cards: 'Cartes', tokens: 'Jetons', dice: 'Dés', meeples: 'Meeples', other: 'Autre' } as Record<AssetDraft['kind'], string>)[kind] }
const assetKinds: AssetDraft['kind'][] = ['cards', 'tokens', 'dice', 'meeples', 'other']