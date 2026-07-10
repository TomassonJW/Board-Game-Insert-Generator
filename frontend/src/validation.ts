import type {
  AssetDraft,
  CandidateDraft,
  ComposerDraft,
  Dimension,
  LayerDraft,
  ManualModuleDraft,
  Point,
  ReservationDraft,
} from './types'

export interface DraftIssue {
  path: string
  message: string
}
export interface DraftReadiness {
  issues: DraftIssue[]
  asset_count: number
  allocated_asset_count: number
  unallocated_asset_names: string[]
  candidate_count: number
  reservation_count: number
  fixed_module_count: number
  layer_count: number
}

export function validateDraft(draft: ComposerDraft): DraftIssue[] {
  const issues: DraftIssue[] = []
  const layerIds = new Set(draft.layers.map((layer) => layer.id))
  const assetIds = new Set(draft.assets.map((asset) => asset.id))

  if (!draft.project_name.trim()) add(issues, 'Projet', 'Saisis un nom de projet.')
  if (draft.project_name.length > 120) add(issues, 'Projet', 'Le nom doit rester sous 120 caracteres.')
  validateDimension(draft.box.inner_dimensions_mm, 'Boite', issues)
  if (!positive(draft.box.usable_height_mm)) add(issues, 'Boite > hauteur exploitable', 'Doit etre superieure a zero.')
  if (!nonNegative(draft.box.lid_clearance_mm)) add(issues, 'Boite > marge couvercle', 'Doit etre positive ou nulle.')

  if (!draft.assets.length) add(issues, 'Contenu', 'Ajoute au moins un asset a ranger.')
  validateUnique(draft.assets, 'Asset', issues)
  draft.assets.forEach((asset, index) => validateAsset(asset, index, issues))

  if (!draft.layers.length) add(issues, 'Layers', 'Ajoute au moins un layer utilisable.')
  validateUnique(draft.layers, 'Layer', issues)
  draft.layers.forEach((layer, index) => validateLayer(layer, index, issues))

  validateUnique(draft.reservations, 'Reservation', issues)
  draft.reservations.forEach((reservation, index) => validateReservation(reservation, index, layerIds, issues))

  validateUnique(draft.manual_modules, 'Module verrouille', issues)
  draft.manual_modules.forEach((module, index) => validateManualModule(module, index, layerIds, issues))

  const reservedIds = new Set(draft.manual_modules.map((module) => module.id))
  validateUnique(draft.candidates, 'Module candidat', issues)
  const assetOwners = new Map<string, string>()
  draft.candidates.forEach((candidate, index) => {
    validateCandidate(candidate, index, layerIds, assetIds, reservedIds, assetOwners, issues)
  })

  if (draft.manual_modules.length === 0) {
    draft.assets
      .filter((asset) => !assetOwners.has(asset.id))
      .forEach((asset) => add(issues, `Asset ${asset.name}`, 'Associe cet asset a un module candidat.'))
  }

  return issues
}
export function summarizeDraft(draft: ComposerDraft): DraftReadiness {
  const allocatedAssetIds = new Set(draft.candidates.flatMap((candidate) => candidate.asset_ids))
  return {
    issues: validateDraft(draft),
    asset_count: draft.assets.length,
    allocated_asset_count: allocatedAssetIds.size,
    unallocated_asset_names: draft.manual_modules.length
      ? []
      : draft.assets.filter((asset) => !allocatedAssetIds.has(asset.id)).map((asset) => asset.name),
    candidate_count: draft.candidates.length,
    reservation_count: draft.reservations.length,
    fixed_module_count: draft.manual_modules.length,
    layer_count: draft.layers.length,
  }
}

export function isComposerDraft(value: unknown): value is ComposerDraft {
  if (!isRecord(value) || value.schema_version !== 'bgig.local_composer.v0' || typeof value.project_name !== 'string' || !isBox(value.box)) return false
  return Array.isArray(value.assets) && value.assets.every(isAsset)
    && Array.isArray(value.layers) && value.layers.every(isLayer)
    && Array.isArray(value.reservations) && value.reservations.every(isReservation)
    && Array.isArray(value.manual_modules) && value.manual_modules.every(isManualModule)
    && Array.isArray(value.candidates) && value.candidates.every(isCandidate)
    && isPreference(value.preference)
}

function validateAsset(asset: AssetDraft, index: number, issues: DraftIssue[]) {
  const label = `Asset ${index + 1}`
  if (!asset.name.trim()) add(issues, label, 'Donne un nom lisible a cet asset.')
  if (!['cards', 'tokens', 'dice', 'meeples', 'other'].includes(asset.kind)) add(issues, label, 'Choisis un type d asset supporte.')
  if (!['store', 'protect', 'separate', 'access_first'].includes(asset.containment_intent)) add(issues, label, 'Choisis une intention de rangement supportee.')
  if (!['exact', 'approximate'].includes(asset.dimension_confidence)) add(issues, label, 'Choisis une confiance de mesure supportee.')
  if (!Number.isInteger(asset.quantity.count) || asset.quantity.count <= 0) add(issues, `${label} > quantite`, 'Utilise un entier superieur a zero.')
  validateDimension(asset.dimensions_mm, label, issues)
}

function validateLayer(layer: LayerDraft, index: number, issues: DraftIssue[]) {
  const label = `Layer ${index + 1}`
  if (!layer.id.trim()) add(issues, label, 'Donne un identifiant de layer.')
  if (!nonNegative(layer.origin_z_mm)) add(issues, `${label} > origine Z`, 'Doit etre positive ou nulle.')
  if (!positive(layer.height_mm)) add(issues, `${label} > hauteur`, 'Doit etre superieure a zero.')
}

function validateReservation(reservation: ReservationDraft, index: number, layerIds: Set<string>, issues: DraftIssue[]) {
  const label = `Reservation ${index + 1}`
  if (!reservation.id.trim()) add(issues, label, 'Donne un identifiant de reservation.')
  if (!['board', 'rulebook', 'existing_tray', 'generic'].includes(reservation.kind)) add(issues, label, 'Choisis un type de reservation supporte.')
  if (!layerIds.has(reservation.layer_id)) add(issues, label, 'Choisis un layer existant.')
  validatePoint(reservation.origin_mm, label, issues)
  validateDimension(reservation.size_mm, label, issues)
}

function validateManualModule(module: ManualModuleDraft, index: number, layerIds: Set<string>, issues: DraftIssue[]) {
  const label = `Module verrouille ${index + 1}`
  if (!module.id.trim() || !module.name.trim()) add(issues, label, 'Donne un identifiant et un nom.')
  if (!layerIds.has(module.layer_id)) add(issues, label, 'Choisis un layer existant.')
  validatePoint(module.origin_mm, label, issues)
  validateDimension(module.size_mm, label, issues)
}

function validateCandidate(
  candidate: CandidateDraft,
  index: number,
  layerIds: Set<string>,
  assetIds: Set<string>,
  reservedIds: Set<string>,
  assetOwners: Map<string, string>,
  issues: DraftIssue[],
) {
  const label = `Module candidat ${index + 1}`
  if (!candidate.id.trim() || !candidate.name.trim()) add(issues, label, 'Donne un identifiant et un nom.')
  if (reservedIds.has(candidate.id)) add(issues, label, 'Son identifiant est deja utilise par un module verrouille.')
  if (!candidate.allowed_layers.length || candidate.allowed_layers.some((layerId) => !layerIds.has(layerId))) add(issues, label, 'Choisis au moins un layer existant.')
  validateDimension(candidate.size_mm, label, issues)
  if (!candidate.asset_ids.length) add(issues, label, 'Associe au moins un asset ou supprime ce module.')
  const candidateAssetIds = new Set<string>()
  candidate.asset_ids.forEach((assetId) => {
    if (!assetIds.has(assetId)) add(issues, label, `L asset ${assetId} n existe pas dans le contenu.`)
    if (candidateAssetIds.has(assetId)) add(issues, label, `L asset ${assetId} est associe deux fois a ce module.`)
    candidateAssetIds.add(assetId)
    const owner = assetOwners.get(assetId)
    if (owner && owner !== candidate.id) add(issues, label, `L asset ${assetId} est deja associe a ${owner}.`)
    assetOwners.set(assetId, candidate.id)
  })
}

function validateUnique(values: Array<{ id: string }>, label: string, issues: DraftIssue[]) {
  const ids = new Set<string>()
  values.forEach((value) => {
    if (ids.has(value.id)) add(issues, label, `L identifiant ${value.id || '(vide)'} est duplique.`)
    ids.add(value.id)
  })
}

function validateDimension(value: Dimension, label: string, issues: DraftIssue[]) {
  for (const axis of ['x', 'y', 'z'] as const) {
    if (!positive(value[axis])) add(issues, `${label} > ${axis.toUpperCase()}`, 'Doit etre superieur a zero.')
  }
}

function validatePoint(value: Point, label: string, issues: DraftIssue[]) {
  for (const axis of ['x', 'y', 'z'] as const) {
    if (!nonNegative(value[axis])) add(issues, `${label} > origine ${axis.toUpperCase()}`, 'Doit etre positive ou nulle.')
  }
}

function add(issues: DraftIssue[], path: string, message: string) {
  issues.push({ path, message })
}

function positive(value: number) { return Number.isFinite(value) && value > 0 }
function nonNegative(value: number) { return Number.isFinite(value) && value >= 0 }

function isRecord(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === 'object' && !Array.isArray(value) }
function isString(value: unknown): value is string { return typeof value === 'string' }
function isNumber(value: unknown): value is number { return typeof value === 'number' && Number.isFinite(value) }
function isDimension(value: unknown): value is Dimension { return isRecord(value) && isNumber(value.x) && isNumber(value.y) && isNumber(value.z) }
function isPoint(value: unknown): value is Point { return isDimension(value) }
function isQuantity(value: unknown): value is AssetDraft['quantity'] { return isRecord(value) && isNumber(value.count) && isString(value.grouping) }
function isBox(value: unknown) { return isRecord(value) && isDimension(value.inner_dimensions_mm) && isNumber(value.usable_height_mm) && isNumber(value.lid_clearance_mm) }
function isAsset(value: unknown): value is AssetDraft { return isRecord(value) && isString(value.id) && isString(value.name) && isQuantity(value.quantity) && isDimension(value.dimensions_mm) && isString(value.kind) && isString(value.containment_intent) && isString(value.dimension_confidence) }
function isLayer(value: unknown): value is LayerDraft { return isRecord(value) && isString(value.id) && isNumber(value.origin_z_mm) && isNumber(value.height_mm) && isString(value.role) }
function isReservation(value: unknown): value is ReservationDraft { return isRecord(value) && isString(value.id) && isString(value.kind) && isPoint(value.origin_mm) && isDimension(value.size_mm) && isString(value.layer_id) }
function isManualModule(value: unknown): value is ManualModuleDraft { return isRecord(value) && isString(value.id) && isString(value.name) && isPoint(value.origin_mm) && isDimension(value.size_mm) && isString(value.layer_id) && typeof value.locked === 'boolean' }
function isCandidate(value: unknown): value is CandidateDraft { return isRecord(value) && isString(value.id) && isString(value.name) && isDimension(value.size_mm) && Array.isArray(value.allowed_layers) && value.allowed_layers.every(isString) && typeof value.allow_xy_rotation === 'boolean' && isNumber(value.priority) && Array.isArray(value.asset_ids) && value.asset_ids.every(isString) }
function isPreference(value: unknown): value is ComposerDraft['preference'] { return value === 'balanced' || value === 'compact' || value === 'accessible' || value === 'print_simple' }
