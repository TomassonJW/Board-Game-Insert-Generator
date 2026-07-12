import type { Dimension } from './types'
import type { ProjectV1Draft } from './project_v1'

export interface ProjectIssue {
  path: string
  message: string
}

export function validateProjectV1(project: ProjectV1Draft): ProjectIssue[] {
  const issues: ProjectIssue[] = []
  if (!project.project_name.trim()) add(issues, 'Nom du projet', 'Donne un nom à ton insert.')
  validateDimension(project.box.inner_dimensions_mm, 'Boîte', issues)
  if (!positive(project.box.usable_height_mm)) add(issues, 'Boîte > hauteur exploitable', 'Elle doit être supérieure à zéro.')
  if (!nonNegative(project.box.lid_clearance_mm)) add(issues, 'Boîte > marge sous couvercle', 'Elle doit être positive ou nulle.')

  if (!nonNegative(project.layout.layout_clearance_mm)) add(issues, 'Jeu entre les bacs', 'Il doit être positif ou nul.')
  if (!positive(project.layout.default_wall_thickness_mm)) add(issues, 'Parois par défaut', 'Elles doivent être supérieures à zéro.')
  if (!positive(project.layout.default_floor_thickness_mm)) add(issues, 'Fond par défaut', 'Il doit être supérieur à zéro.')
  if (!nonNegative(project.layout.default_content_clearance_mm)) add(issues, 'Jeu autour des pièces', 'Il doit être positif ou nul.')

  if (!project.contents.length) add(issues, 'Pièces', 'Ajoute au moins une famille de pièces à ranger.')
  const groupIds = new Set<string>()
  project.container_groups.forEach((group, index) => {
    const label = `Bac ${index + 1}`
    if (!group.id.trim()) add(issues, label, 'Son identifiant interne manque.')
    if (groupIds.has(group.id)) add(issues, label, 'Ce bac existe déjà.')
    groupIds.add(group.id)
    if (!group.name.trim()) add(issues, label, 'Donne un nom lisible à ce bac.')
    validateOptionalPositive(group.wall_thickness_mm, `${label} > parois`, issues)
    validateOptionalPositive(group.floor_thickness_mm, `${label} > fond`, issues)
  })

  const contentIds = new Set<string>()
  project.contents.forEach((content, index) => {
    const label = `Pièce ${index + 1}`
    if (!content.id.trim() || contentIds.has(content.id)) add(issues, label, 'Cette ligne doit avoir un identifiant unique.')
    contentIds.add(content.id)
    if (!content.name.trim()) add(issues, label, 'Donne un nom à cette famille de pièces.')
    validateDimension(content.dimensions_mm, label, issues)
    if (!Number.isInteger(content.quantity) || content.quantity <= 0) add(issues, `${label} > quantité`, 'Utilise un entier supérieur à zéro.')
    if (!groupIds.has(content.container_group_id)) add(issues, label, 'Choisis le bac qui doit contenir cette pièce.')
    if (content.content_clearance_mm !== null && !nonNegative(content.content_clearance_mm)) add(issues, `${label} > jeu`, 'Il doit être positif ou nul.')
  })

  const flatIds = new Set<string>()
  const stackOrders = new Set<number>()
  project.flat_items.forEach((item, index) => {
    const label = `Plateau ou livret ${index + 1}`
    if (!item.id.trim() || flatIds.has(item.id)) add(issues, label, 'Cette ligne doit avoir un identifiant unique.')
    flatIds.add(item.id)
    if (!item.name.trim()) add(issues, label, 'Donne un nom lisible.')
    validateDimension(item.dimensions_mm, label, issues)
    if (!Number.isInteger(item.quantity) || item.quantity <= 0) add(issues, `${label} > quantité`, 'Utilise un entier supérieur à zéro.')
    if (item.stack_order !== null) {
      if (!Number.isInteger(item.stack_order) || item.stack_order < 0) add(issues, `${label} > ordre`, 'Utilise un entier positif ou laisse le choix automatique.')
      if (stackOrders.has(item.stack_order)) add(issues, `${label} > ordre`, 'Deux éléments ne peuvent pas avoir le même ordre.')
      stackOrders.add(item.stack_order)
    }
  })

  const fillIds = new Set<string>()
  project.fill_elements.forEach((element, index) => {
    const label = `Complément ${index + 1}`
    if (!element.id.trim() || fillIds.has(element.id)) add(issues, label, 'Cette ligne doit avoir un identifiant unique.')
    fillIds.add(element.id)
    if (!element.name.trim()) add(issues, label, 'Donne un nom lisible.')
    if (element.mode === 'exact' && element.dimensions_mm === null) add(issues, label, 'Indique les dimensions du volume demandé.')
    if (element.mode === 'auto' && element.dimensions_mm !== null) add(issues, label, 'Choisis soit une taille exacte, soit un volume automatique.')
    if (element.dimensions_mm) validateDimension(element.dimensions_mm, label, issues)
    if (element.container_group_id && !groupIds.has(element.container_group_id)) add(issues, label, 'Le bac associé n’existe plus.')
  })

  return issues
}

function validateDimension(value: Dimension, label: string, issues: ProjectIssue[]) {
  for (const axis of ['x', 'y', 'z'] as const) {
    if (!positive(value[axis])) add(issues, `${label} > ${axis.toUpperCase()}`, 'La mesure doit être supérieure à zéro.')
  }
}

function validateOptionalPositive(value: number | null, label: string, issues: ProjectIssue[]) {
  if (value !== null && !positive(value)) add(issues, label, 'La mesure doit être supérieure à zéro ou laissée au réglage général.')
}

function add(issues: ProjectIssue[], path: string, message: string) { issues.push({ path, message }) }
function positive(value: number) { return Number.isFinite(value) && value > 0 }
function nonNegative(value: number) { return Number.isFinite(value) && value >= 0 }
