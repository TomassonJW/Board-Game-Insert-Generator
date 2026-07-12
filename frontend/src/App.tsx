import { type ChangeEvent, useEffect, useMemo, useState } from 'react'
import { ApiError, buildFunctionalCad, loadProjectV1Starter, normalizeProjectV1 } from './api'
import type {
  ContainerGroupDraft,
  FillElementDraft,
  FlatItemDraft,
  ProjectContentDraft,
  ProjectShapeKind,
  ProjectV1Draft,
} from './project_v1'
import { type ProjectIssue, validateProjectV1 } from './project_v1_validation'
import type { VolumeClosurePlan } from './volume_closure'
import type { FunctionalCadBuild } from './volume_cad'
import type { Dimension } from './types'

const shapeOptions: Array<{ value: ProjectShapeKind; label: string }> = [
  { value: 'round', label: 'Rond' },
  { value: 'square', label: 'Carré' },
  { value: 'rectangle', label: 'Rectangle' },
  { value: 'cards', label: 'Cartes' },
  { value: 'cube', label: 'Cube ou dé' },
  { value: 'meeple', label: 'Pion ou figurine' },
  { value: 'custom', label: 'Sur mesure' },
]

const shapeLabels: Record<ProjectShapeKind, [string, string, string]> = {
  round: ['Diamètre', 'Diamètre', 'Épaisseur'],
  square: ['Côté', 'Côté', 'Hauteur'],
  rectangle: ['Largeur', 'Profondeur', 'Hauteur'],
  cards: ['Largeur', 'Hauteur', 'Épaisseur totale'],
  cube: ['Côté', 'Côté', 'Côté'],
  meeple: ['Largeur', 'Profondeur', 'Hauteur'],
  custom: ['Largeur', 'Profondeur', 'Hauteur'],
}

const fillKindLabels: Record<FillElementDraft['kind'], string> = {
  hollow: 'Bac vide',
  solid: 'Remplissage plein',
  separator: 'Séparateur',
}

export default function App() {
  const [project, setProject] = useState<ProjectV1Draft>()
  const [message, setMessage] = useState('Préparation de ton projet…')
  const [error, setError] = useState<string>()
  const [attemptedBuild, setAttemptedBuild] = useState(false)
  const [buildPlan, setBuildPlan] = useState<VolumeClosurePlan>()
  const [cadBuild, setCadBuild] = useState<FunctionalCadBuild>()
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    void loadProjectV1Starter()
      .then((starter) => {
        setProject(starter)
        setMessage('Commence par mesurer ta boîte, puis ajoute ce que tu veux ranger.')
      })
      .catch((reason: unknown) => setError(formatError(reason)))
  }, [])

  const issues = useMemo(() => project ? validateProjectV1(project) : [], [project])
  const metrics = useMemo(() => project ? projectMetrics(project) : undefined, [project])

  function update(mutator: (current: ProjectV1Draft) => ProjectV1Draft) {
    setProject((current) => current ? mutator(current) : current)
    setError(undefined)
    setAttemptedBuild(false)
    setBuildPlan(undefined)
    setCadBuild(undefined)
  }

  function addContent() {
    update((current) => {
      const group = newGroup(current)
      const content: ProjectContentDraft = {
        id: nextId('piece', current.contents.map((item) => item.id)),
        name: 'Nouvelle pièce',
        shape_kind: 'custom',
        dimensions_mm: { x: 20, y: 20, z: 5 },
        quantity: 1,
        container_group_id: group.id,
        content_clearance_mm: null,
        measurement_confidence: 'exact',
      }
      return { ...current, container_groups: [...current.container_groups, group], contents: [...current.contents, content] }
    })
  }

  function addFlatItem() {
    update((current) => ({
      ...current,
      flat_items: [...current.flat_items, {
        id: nextId('plat', current.flat_items.map((item) => item.id)),
        name: 'Nouveau livret ou plateau',
        kind: 'rulebook',
        dimensions_mm: { x: 200, y: 140, z: 2 },
        quantity: 1,
        stack_order: null,
      }],
    }))
  }

  function addFillElement() {
    update((current) => ({
      ...current,
      fill_elements: [...current.fill_elements, {
        id: nextId('complement', current.fill_elements.map((item) => item.id)),
        name: 'Bac vide à placer',
        kind: 'hollow',
        mode: 'auto',
        dimensions_mm: null,
        container_group_id: null,
      }],
    }))
  }

  function assignContentToGroup(index: number, nextGroupId: string) {
    update((current) => {
      let groups = current.container_groups
      let groupId = nextGroupId
      if (nextGroupId === '__new__') {
        const group = newGroup(current)
        groups = [...groups, group]
        groupId = group.id
      }
      return {
        ...current,
        container_groups: groups,
        contents: current.contents.map((item, itemIndex) => itemIndex === index ? { ...item, container_group_id: groupId } : item),
      }
    })
  }

  function updateContentDimension(index: number, axis: keyof Dimension, value: number) {
    update((current) => ({
      ...current,
      contents: current.contents.map((item, itemIndex) => {
        if (itemIndex !== index) return item
        const dimensions = { ...item.dimensions_mm, [axis]: value }
        if (item.shape_kind === 'round' || item.shape_kind === 'square') {
          if (axis === 'x' || axis === 'y') dimensions.x = dimensions.y = value
        }
        if (item.shape_kind === 'cube') dimensions.x = dimensions.y = dimensions.z = value
        return { ...item, dimensions_mm: dimensions }
      }),
    }))
  }

  async function importProject(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    try {
      const raw = JSON.parse(await file.text()) as ProjectV1Draft
      const normalized = await normalizeProjectV1(raw)
      setProject(normalized.project)
      setAttemptedBuild(false)
      setBuildPlan(undefined)
      setCadBuild(undefined)
      setError(undefined)
      setMessage(normalized.migrated
        ? 'Ton ancien projet a été converti. Vérifie les bacs, plateaux et réglages avant de continuer.'
        : 'Projet V0.1 importé. Tu peux reprendre là où tu en étais.')
    } catch (reason) {
      setError(formatError(reason))
    } finally {
      event.target.value = ''
    }
  }

  async function handleBuild() {
    if (!project) return
    setAttemptedBuild(true)
    if (issues.length) {
      setMessage(`${issues.length} point(s) sont a completer avant de construire l insert.`)
      return
    }
    setBusy(true)
    setError(undefined)
    try {
      const result = await buildFunctionalCad(project)
      setCadBuild(result)
      setBuildPlan(result.volume_plan)
      setMessage(result.status === 'impossible'
        ? 'BGIG ne peut pas fabriquer cet insert avec ces mesures. Corrige les blocages indiques, puis relance la construction.'
        : `${result.materialization.component_count} piece(s) fonctionnelle(s) sont pretes pour la verification dans Fusion.`)
    } catch (reason) {
      setError(formatError(reason))
    } finally {
      setBusy(false)
    }
  }
  if (!project || !metrics) {
    return <main className="loading-shell"><div className="loading-card"><span className="loading-dot" /><p>{error ?? 'Connexion à ton projet local…'}</p></div></main>
  }

  return (
    <main className="studio-shell">
      <header className="studio-topbar">
        <div className="brand"><span className="brand-mark">B</span><span>BGIG <strong>Studio</strong></span></div>
        <div className="topbar-actions">
          <label className="button ghost"><span>Importer un projet</span><input type="file" accept="application/json" onChange={importProject} /></label>
          <button className="button secondary" onClick={() => downloadJson(`${safeFileName(project.project_name)}-projet.json`, project)}>Sauvegarder</button>
        </div>
      </header>

      <section className="studio-hero">
        <div>
          <p className="eyebrow">Projet d’insert</p>
          <h1>Organise ta boîte, simplement.</h1>
          <p>Décris ce que tu veux ranger. BGIG prépare les bons bacs, garde la place des plateaux et remplit la boîte sans te demander de dessiner.</p>
        </div>
        <div className="hero-status"><span className={issues.length ? 'status-dot warning' : 'status-dot'} /><div><strong>{issues.length ? 'À compléter' : 'Projet cohérent'}</strong><small>{issues.length ? `${issues.length} point(s) à vérifier` : 'Mesures et listes prêtes à construire'}</small></div></div>
      </section>

      {error && <section className="message error" role="alert"><strong>Impossible de charger le projet</strong><span>{error}</span></section>}
      <section className="message"><strong>Ce que tu fais ici</strong><span>{message}</span></section>
      {attemptedBuild && issues.length > 0 && <IssueList issues={issues} />}

      <section className="studio-layout">
        <div className="editor-column">
          <Section number="01" title="Ma boîte" subtitle="Mesure l’intérieur réellement disponible une fois la boîte fermée.">
            <div className="field-grid box-fields">
              <TextField label="Nom du projet" value={project.project_name} wide onChange={(value) => update((current) => ({ ...current, project_name: value }))} />
              <NumberField label="Largeur intérieure" value={project.box.inner_dimensions_mm.x} onChange={(value) => update((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, x: value } } }))} />
              <NumberField label="Profondeur intérieure" value={project.box.inner_dimensions_mm.y} onChange={(value) => update((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, y: value } } }))} />
              <NumberField label="Hauteur intérieure" value={project.box.inner_dimensions_mm.z} onChange={(value) => update((current) => ({ ...current, box: { ...current.box, inner_dimensions_mm: { ...current.box.inner_dimensions_mm, z: value } } }))} />
              <NumberField label="Hauteur disponible" value={project.box.usable_height_mm} onChange={(value) => update((current) => ({ ...current, box: { ...current.box, usable_height_mm: value } }))} />
              <NumberField label="Marge sous le couvercle" value={project.box.lid_clearance_mm} minimum={0} onChange={(value) => update((current) => ({ ...current, box: { ...current.box, lid_clearance_mm: value } }))} />
            </div>
          </Section>

          <Section number="02" title="Ce que tu veux ranger" subtitle="Une ligne par famille de pièces. Choisis le bac qu’elle doit partager avec les autres.">
            <div className="section-heading"><p>{project.contents.length ? `${project.contents.length} famille(s) de pièces` : 'Aucune pièce pour le moment'}</p><button className="button secondary" onClick={addContent}>+ Ajouter une pièce</button></div>
            <div className="table-scroll"><table className="data-table"><thead><tr><th>Pièce</th><th>Forme</th><th>Mesures</th><th>Quantité</th><th>Bac cible</th><th /></tr></thead><tbody>
              {project.contents.map((content, index) => <tr key={content.id}>
                <td><TextInput ariaLabel={`Nom de la pièce ${index + 1}`} value={content.name} onChange={(value) => update((current) => ({ ...current, contents: current.contents.map((item, itemIndex) => itemIndex === index ? { ...item, name: value } : item) }))} /></td>
                <td><select aria-label={`Forme de ${content.name}`} value={content.shape_kind} onChange={(event) => update((current) => ({ ...current, contents: current.contents.map((item, itemIndex) => itemIndex === index ? { ...item, shape_kind: event.target.value as ProjectShapeKind } : item) }))}>{shapeOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></td>
                <td><DimensionFields labels={shapeLabels[content.shape_kind]} value={content.dimensions_mm} onChange={(axis, value) => updateContentDimension(index, axis, value)} /></td>
                <td><NumberInput ariaLabel={`Quantité de ${content.name}`} value={content.quantity} step={1} onChange={(value) => update((current) => ({ ...current, contents: current.contents.map((item, itemIndex) => itemIndex === index ? { ...item, quantity: Math.round(value) } : item) }))} /></td>
                <td><select aria-label={`Bac cible de ${content.name}`} value={content.container_group_id} onChange={(event) => assignContentToGroup(index, event.target.value)}>{project.container_groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}<option value="__new__">+ Créer un nouveau bac</option></select></td>
                <td><button className="delete-button" aria-label={`Supprimer ${content.name}`} onClick={() => update((current) => ({ ...current, contents: current.contents.filter((_, itemIndex) => itemIndex !== index) }))}>×</button></td>
              </tr>)}
            </tbody></table></div>
            <p className="helper-copy">Rond, carré et cube synchronisent automatiquement leurs côtés. « Sur mesure » te laisse saisir les trois mesures librement.</p>
          </Section>

          <Section number="03" title="Plateaux et livrets" subtitle="Ces éléments sont posés au-dessus des bacs. Leur pile sera réservée automatiquement.">
            <div className="section-heading"><p>{project.flat_items.length ? `${project.flat_items.length} élément(s) plat(s)` : 'Tu peux laisser cette liste vide.'}</p><button className="button secondary" onClick={addFlatItem}>+ Ajouter un plateau ou livret</button></div>
            <div className="table-scroll"><table className="data-table compact"><thead><tr><th>Élément</th><th>Type</th><th>Mesures</th><th>Qté</th><th>Ordre</th><th /></tr></thead><tbody>
              {project.flat_items.map((item, index) => <FlatItemRow key={item.id} item={item} index={index} onChange={(change) => update((current) => ({ ...current, flat_items: current.flat_items.map((entry, entryIndex) => entryIndex === index ? { ...entry, ...change } : entry) }))} onDimensionChange={(axis, value) => update((current) => ({ ...current, flat_items: current.flat_items.map((entry, entryIndex) => entryIndex === index ? { ...entry, dimensions_mm: { ...entry.dimensions_mm, [axis]: value } } : entry) }))} onDelete={() => update((current) => ({ ...current, flat_items: current.flat_items.filter((_, entryIndex) => entryIndex !== index) }))} />)}
            </tbody></table></div>
          </Section>

          <Section number="04" title="Les bacs demandés" subtitle="Ils se créent automatiquement quand tu associes une pièce à un nouveau bac.">
            <div className="group-grid">{project.container_groups.map((group) => <ContainerGroupCard key={group.id} group={group} contentCount={project.contents.filter((content) => content.container_group_id === group.id).length} onChange={(change) => update((current) => ({ ...current, container_groups: current.container_groups.map((entry) => entry.id === group.id ? { ...entry, ...change } : entry) }))} onDelete={() => update((current) => ({ ...current, container_groups: current.container_groups.filter((entry) => entry.id !== group.id), contents: current.contents.filter((content) => content.container_group_id !== group.id) }))} />)}</div>
          </Section>

          <Section number="05" title="Compléter l’espace" subtitle="Ajoute un bac vide, un séparateur ou un remplissage précis si tu sais déjà ce que tu veux.">
            <div className="section-heading"><p>BGIG proposera aussi des compléments quand un espace reste libre.</p><button className="button secondary" onClick={addFillElement}>+ Ajouter un complément</button></div>
            {project.fill_elements.length === 0 ? <div className="empty-row">Aucun complément demandé : BGIG cherchera d’abord à agrandir utilement les bacs.</div> : <div className="fill-list">{project.fill_elements.map((element, index) => <FillElementRow key={element.id} element={element} groups={project.container_groups} onChange={(change) => update((current) => ({ ...current, fill_elements: current.fill_elements.map((entry, entryIndex) => entryIndex === index ? { ...entry, ...change } : entry) }))} onDelete={() => update((current) => ({ ...current, fill_elements: current.fill_elements.filter((_, entryIndex) => entryIndex !== index) }))} />)}</div>}
          </Section>

          <Section number="06" title="Réglages de fabrication" subtitle="Ces valeurs sont appliquées à toute la boîte, sauf si un bac possède sa propre valeur.">
            <div className="field-grid settings-fields">
              <NumberField label="Jeu entre les bacs" value={project.layout.layout_clearance_mm} minimum={0} onChange={(value) => update((current) => ({ ...current, layout: { ...current.layout, layout_clearance_mm: value } }))} />
              <NumberField label="Parois par défaut" value={project.layout.default_wall_thickness_mm} onChange={(value) => update((current) => ({ ...current, layout: { ...current.layout, default_wall_thickness_mm: value } }))} />
              <NumberField label="Fond par défaut" value={project.layout.default_floor_thickness_mm} onChange={(value) => update((current) => ({ ...current, layout: { ...current.layout, default_floor_thickness_mm: value } }))} />
              <NumberField label="Jeu autour des pièces" value={project.layout.default_content_clearance_mm} minimum={0} onChange={(value) => update((current) => ({ ...current, layout: { ...current.layout, default_content_clearance_mm: value } }))} />
            </div>
          </Section>

          <section className="build-panel"><div><p className="eyebrow">Pret quand tu l es</p><h2>Construire mon insert</h2><p>BGIG calcule les bacs, la pile haute, les espaces restants, puis prepare la geometrie fonctionnelle pour Fusion.</p></div><button className="build-button" onClick={handleBuild} disabled={busy}>{busy ? 'Construction en cours...' : <>Construire mon insert <span>-&gt;</span></>}</button></section>
          {buildPlan && <DerivationResult plan={buildPlan} build={cadBuild} />}
        </div>

        <aside className="preview-column"><ProjectPreview project={project} metrics={metrics} /><section className="summary-card"><p className="eyebrow">Ce que BGIG voit</p><div className="summary-line"><span>Pièces à ranger</span><strong>{metrics.itemCount}</strong></div><div className="summary-line"><span>Bacs demandés</span><strong>{metrics.groupCount}</strong></div><div className="summary-line"><span>Hauteur plateaux/livrets</span><strong>{formatMillimeters(metrics.flatHeight)}</strong></div><div className="summary-line"><span>Volume intérieur</span><strong>{formatVolume(metrics.volume)}</strong></div></section><section className="tip-card"><strong>À retenir</strong><p>La vue est un plan de saisie, pas une fausse promesse de placement. Le moteur calculera les dimensions et positions réelles des bacs au moment de la construction.</p></section></aside>
      </section>
    </main>
  )
}

function Section({ number, title, subtitle, children }: { number: string; title: string; subtitle: string; children: React.ReactNode }) {
  return <section className="work-section"><header><span className="section-number">{number}</span><div><h2>{title}</h2><p>{subtitle}</p></div></header>{children}</section>
}

function FlatItemRow({ item, index, onChange, onDimensionChange, onDelete }: { item: FlatItemDraft; index: number; onChange: (change: Partial<FlatItemDraft>) => void; onDimensionChange: (axis: keyof Dimension, value: number) => void; onDelete: () => void }) {
  return <tr><td><TextInput ariaLabel={`Nom de l’élément plat ${index + 1}`} value={item.name} onChange={(name) => onChange({ name })} /></td><td><select aria-label={`Type de ${item.name}`} value={item.kind} onChange={(event) => onChange({ kind: event.target.value as FlatItemDraft['kind'] })}><option value="board">Plateau</option><option value="rulebook">Livret</option><option value="other">Autre élément plat</option></select></td><td><DimensionFields labels={['Largeur', 'Profondeur', 'Épaisseur']} value={item.dimensions_mm} onChange={onDimensionChange} /></td><td><NumberInput ariaLabel={`Quantité de ${item.name}`} value={item.quantity} step={1} onChange={(quantity) => onChange({ quantity: Math.round(quantity) })} /></td><td><NumberInput ariaLabel={`Ordre de ${item.name}`} value={item.stack_order ?? 0} step={1} onChange={(stack_order) => onChange({ stack_order: Math.round(stack_order) })} /></td><td><button className="delete-button" aria-label={`Supprimer ${item.name}`} onClick={onDelete}>×</button></td></tr>
}

function ContainerGroupCard({ group, contentCount, onChange, onDelete }: { group: ContainerGroupDraft; contentCount: number; onChange: (change: Partial<ContainerGroupDraft>) => void; onDelete: () => void }) {
  return <article className="group-card"><div className="group-card-heading"><span>{contentCount} famille(s)</span>{contentCount === 0 && <button className="text-button danger" onClick={onDelete}>Supprimer</button>}</div><TextField label="Nom du bac" value={group.name} onChange={(name) => onChange({ name })} /><div className="mini-grid"><OptionalNumberField label="Parois" value={group.wall_thickness_mm} onChange={(wall_thickness_mm) => onChange({ wall_thickness_mm })} /><OptionalNumberField label="Fond" value={group.floor_thickness_mm} onChange={(floor_thickness_mm) => onChange({ floor_thickness_mm })} /></div><p>Vide = réglage général.</p></article>
}

function FillElementRow({ element, groups, onChange, onDelete }: { element: FillElementDraft; groups: ContainerGroupDraft[]; onChange: (change: Partial<FillElementDraft>) => void; onDelete: () => void }) {
  return <article className="fill-row"><TextField label="Nom" value={element.name} onChange={(name) => onChange({ name })} /><label className="field"><span>Type</span><select value={element.kind} onChange={(event) => onChange({ kind: event.target.value as FillElementDraft['kind'] })}>{Object.entries(fillKindLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label className="field"><span>Taille</span><select value={element.mode} onChange={(event) => onChange({ mode: event.target.value as FillElementDraft['mode'], dimensions_mm: event.target.value === 'auto' ? null : { x: 10, y: 10, z: 10 } })}><option value="auto">À calculer</option><option value="exact">Je donne les mesures</option></select></label><label className="field"><span>Bac associé</span><select value={element.container_group_id ?? ''} onChange={(event) => onChange({ container_group_id: event.target.value || null })}><option value="">Dans toute la boîte</option>{groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></label>{element.dimensions_mm && <div className="fill-dimensions"><DimensionFields labels={['Largeur', 'Profondeur', 'Hauteur']} value={element.dimensions_mm} onChange={(axis, value) => onChange({ dimensions_mm: { ...element.dimensions_mm!, [axis]: value } })} /></div>}<button className="delete-button" aria-label={`Supprimer ${element.name}`} onClick={onDelete}>×</button></article>
}

function DerivationResult({ plan, build }: { plan: VolumeClosurePlan; build?: FunctionalCadBuild }) {
  const blocked = plan.summary.status === 'impossible' || build?.status === 'impossible'
  const geometryReady = build?.status === 'planned_for_fusion_smoke'
  return <section className={`derivation-result ${blocked ? 'blocked' : 'ready'}`} aria-live="polite"><header><div><p className="eyebrow">Plan complet</p><h2>{blocked ? 'L insert ne peut pas encore etre construit' : 'Toute la boite est planifiee'}</h2><p>{blocked ? 'Les blocages ci-dessous indiquent quoi modifier.' : 'Les bacs, les supports et les espaces restants sont maintenant traduits en pieces fonctionnelles.'}</p></div><span>{plan.summary.placed_container_count} bac(s) places</span></header>{plan.placements.map((item) => <article key={item.id} className="derived-container"><div><strong>{item.name}</strong><span>Position : {formatDimension(item.origin_mm)}</span></div><b>{formatDimension(item.size_mm)}</b></article>)}<article className="flat-stack-result"><div><strong>Verifications</strong><span>{plan.summary.classified_free_region_count} region(s) restante(s) classee(s)</span></div><b>{plan.validation.volume_conserved ? 'Volume coherent' : 'Volume incoherent'}</b><p>{plan.support.note}</p><small>{plan.summary.hollow_fill_candidate_count} volume(s) creux proposes ; {plan.summary.solid_fill_candidate_count} volume(s) plein(s) demandes.</small></article>{build && <article className="flat-stack-result"><div><strong>Geometrie pour Fusion</strong><span>{build.materialization.component_count} piece(s) prete(s)</span></div><b>{geometryReady ? 'Prete a verifier' : 'A corriger'}</b>{geometryReady ? <p>Les parois, fonds et logements ont ete prepares. Fusion doit encore les afficher : ce n est pas une validation d impression.</p> : <p>La geometrie n a pas ete produite. Corrige les blocages ci-dessous sans reduire les parois minimales.</p>}{build.materialization.skipped_regions.length > 0 && <small>{build.materialization.skipped_regions.length} petit(s) espace(s) restent du jeu technique pour conserver les parois minimales.</small>}</article>}{[...plan.blockers, ...(build?.blockers ?? [])].map((blocker) => <p className="derivation-blocker" key={blocker}>{blocker}</p>)}<p className="derivation-next">{geometryReady ? 'Etape suivante : verifier la scene preparee dans Fusion.' : 'Corrige les mesures indiquees, puis relance la construction.'}</p></section>
}

function ProjectPreview({ project, metrics }: { project: ProjectV1Draft; metrics: ReturnType<typeof projectMetrics> }) {
  const width = Math.max(project.box.inner_dimensions_mm.x, 1)
  const depth = Math.max(project.box.inner_dimensions_mm.y, 1)
  const topHeightRatio = Math.min(1, metrics.flatHeight / Math.max(project.box.usable_height_mm, 1))
  const groups = project.container_groups
  const palette = ['#D9A441', '#94B78B', '#7FA8C9', '#C58DA4', '#7E9E91', '#BD9A6C']
  return <section className="preview-card"><div className="preview-heading"><div><p className="eyebrow">Vue vivante</p><h2>Ta boîte, maintenant</h2></div><span>Plan de saisie</span></div><div className="box-figure"><svg viewBox={`0 0 ${width} ${depth}`} role="img" aria-label="Vue de dessus indicative de la boîte"><rect x="0" y="0" width={width} height={depth} rx="4" className="box-outline" />{groups.map((group, index) => { const columnWidth = width / Math.max(groups.length, 1); const x = index * columnWidth + 3; return <g key={group.id}><rect x={x} y="5" width={Math.max(columnWidth - 6, 1)} height={Math.max(depth - 10, 1)} rx="3" fill={palette[index % palette.length]} className="group-block" /><text x={x + 4} y="18">{group.name}</text></g> })}</svg>{groups.length === 0 && <div className="preview-empty"><span>+</span><p>Ajoute une pièce pour voir apparaître un bac demandé.</p></div>}</div><div className="preview-legend"><span><i className="legend-group" />Bac demandé</span><span><i className="legend-flat" />Plateaux et livrets au-dessus</span></div><div className="cross-section"><div className="cross-section-label"><span>Coupe de hauteur</span><strong>{formatMillimeters(project.box.usable_height_mm)}</strong></div><div className="height-bar"><div className="flat-stack" style={{ height: `${topHeightRatio * 100}%` }} /><div className="storage-stack" style={{ height: `${(1 - topHeightRatio) * 100}%` }} /></div><div className="height-key"><span><i className="key-storage" />Bacs à calculer</span><span><i className="key-flat" />Pile supérieure</span></div></div></section>
}

function IssueList({ issues }: { issues: ProjectIssue[] }) {
  return <section className="message error issue-list" aria-live="polite"><strong>À compléter avant de construire</strong><ul>{issues.map((issue, index) => <li key={`${issue.path}-${index}`}><b>{issue.path}</b> — {issue.message}</li>)}</ul></section>
}

function TextField({ label, value, onChange, wide = false }: { label: string; value: string; onChange: (value: string) => void; wide?: boolean }) {
  return <label className={`field ${wide ? 'wide' : ''}`}><span>{label}</span><input value={value} onChange={(event) => onChange(event.target.value)} /></label>
}

function TextInput({ value, onChange, ariaLabel }: { value: string; onChange: (value: string) => void; ariaLabel: string }) {
  return <input aria-label={ariaLabel} value={value} onChange={(event) => onChange(event.target.value)} />
}

function NumberField({ label, value, onChange, minimum = 0.1 }: { label: string; value: number; onChange: (value: number) => void; minimum?: number }) {
  return <label className="field"><span>{label}</span><div className="number-unit"><input type="number" min={minimum} step="0.1" value={value} onChange={(event) => onChange(Number(event.target.value))} /><i>mm</i></div></label>
}

function OptionalNumberField({ label, value, onChange }: { label: string; value: number | null; onChange: (value: number | null) => void }) {
  return <label className="field"><span>{label}</span><div className="number-unit"><input type="number" min="0.1" step="0.1" value={value ?? ''} placeholder="Général" onChange={(event) => onChange(event.target.value === '' ? null : Number(event.target.value))} /><i>mm</i></div></label>
}

function NumberInput({ value, onChange, ariaLabel, step = 0.1 }: { value: number; onChange: (value: number) => void; ariaLabel: string; step?: number }) {
  return <input aria-label={ariaLabel} type="number" min="0" step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
}

function DimensionFields({ labels, value, onChange }: { labels: [string, string, string]; value: Dimension; onChange: (axis: keyof Dimension, value: number) => void }) {
  return <div className="dimension-fields">{(['x', 'y', 'z'] as const).map((axis, index) => <label key={axis}><span>{labels[index]}</span><NumberInput ariaLabel={labels[index]} value={value[axis]} onChange={(next) => onChange(axis, next)} /></label>)}</div>
}

function newGroup(project: ProjectV1Draft): ContainerGroupDraft {
  const id = nextId('bac', project.container_groups.map((group) => group.id))
  return { id, name: `Bac ${project.container_groups.length + 1}`, wall_thickness_mm: null, floor_thickness_mm: null }
}

function nextId(prefix: string, existing: string[]) {
  let index = existing.length + 1
  while (existing.includes(`${prefix}-${index}`)) index += 1
  return `${prefix}-${index}`
}

function projectMetrics(project: ProjectV1Draft) {
  return {
    itemCount: project.contents.reduce((total, item) => total + Math.max(0, item.quantity), 0),
    groupCount: project.container_groups.length,
    flatHeight: project.flat_items.reduce((total, item) => total + (item.dimensions_mm.z * item.quantity), 0),
    volume: project.box.inner_dimensions_mm.x * project.box.inner_dimensions_mm.y * project.box.usable_height_mm,
  }
}

function formatMillimeters(value: number) { return `${Math.round(value * 10) / 10} mm` }
function formatDimension(value: Dimension) { return `${formatMillimeters(value.x)} × ${formatMillimeters(value.y)} × ${formatMillimeters(value.z)}` }
function formatVolume(value: number) { return `${Math.round(value / 1000).toLocaleString('fr-FR')} cm³` }
function safeFileName(value: string) { return value.trim().toLowerCase().replace(/[^a-z0-9]+/gi, '-').replace(/(^-|-$)/g, '') || 'bgig' }
function downloadJson(fileName: string, value: unknown) { const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' })); const anchor = document.createElement('a'); anchor.href = url; anchor.download = fileName; anchor.click(); URL.revokeObjectURL(url) }
function formatError(reason: unknown) { return reason instanceof ApiError ? reason.message : reason instanceof Error ? reason.message : 'Une erreur inattendue est survenue.' }
