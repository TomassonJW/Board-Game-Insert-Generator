"""Fusion 360 add-in entry point for Board Game Insert Generator.

P7-M001 creates one Fusion component per physical BGIG module, then places
linked compact and exploded occurrences of that component from a serialized CAD
IR. Fusion consumes already resolved CAD IR dimensions and must not recalculate
layout, cavities, clearances, placements, or tolerances.
"""

from __future__ import annotations

from pathlib import Path

try:
    from .fusion_skeleton import (
        DOCUMENT_STATUS_ZERO_DOC,
        FUSION_EXTENT_NEGATIVE,
        FUSION_EXTENT_POSITIVE,
        FUSION_SKETCH_PLANE_XZ,
        FUSION_SKETCH_PLANE_YZ,
        OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
        FusionAssemblyDocumentRequiredError,
        FusionCavityCutPlan,
        FusionFingerNotchCutPlan,
        FusionGenerationPlan,
        FusionSkeletonError,
        FusionSolidPlan,
        FusionVectorMm,
        assembly_document_required_message,
        cad_ir_input_guidance,
        describe_document_state,
        generation_plan_from_cad_ir,
        is_part_design_component_limit_error,
        load_cad_ir_json,
        mm_to_cm,
        resolve_cad_ir_input_path,
        resolve_generation_mode,
    )
except ImportError:  # pragma: no cover - Fusion may load the file as a script.
    from fusion_skeleton import (  # type: ignore[no-redef]
        DOCUMENT_STATUS_ZERO_DOC,
        FUSION_EXTENT_NEGATIVE,
        FUSION_EXTENT_POSITIVE,
        FUSION_SKETCH_PLANE_XZ,
        FUSION_SKETCH_PLANE_YZ,
        OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE,
        FusionAssemblyDocumentRequiredError,
        FusionCavityCutPlan,
        FusionFingerNotchCutPlan,
        FusionGenerationPlan,
        FusionSkeletonError,
        FusionSolidPlan,
        FusionVectorMm,
        assembly_document_required_message,
        cad_ir_input_guidance,
        describe_document_state,
        generation_plan_from_cad_ir,
        is_part_design_component_limit_error,
        load_cad_ir_json,
        mm_to_cm,
        resolve_cad_ir_input_path,
        resolve_generation_mode,
    )

try:
    import adsk.core  # type: ignore[import-not-found]
    import adsk.fusion  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised only outside Fusion.
    adsk = None  # type: ignore[assignment]



_app = None
_ui = None


def run(context) -> None:  # noqa: ANN001 - Fusion controls the signature.
    """Fusion 360 add-in startup hook."""

    global _app, _ui

    if adsk is None:
        return

    _app = adsk.core.Application.get()
    _ui = _app.userInterface if _app else None
    state = describe_document_state(_app)

    if state.status == DOCUMENT_STATUS_ZERO_DOC:
        _show_message(
            "Board Game Insert Generator cannot generate blanks.\n"
            f"{state.message}\n"
            "Open or create a Fusion design, then run the add-in again."
        )
        return

    try:
        addin_dir = Path(__file__).resolve().parent
        cad_ir_path = resolve_cad_ir_input_path(addin_dir)
        generation_mode = resolve_generation_mode(addin_dir)
        payload = load_cad_ir_json(cad_ir_path)
        generation_plan = generation_plan_from_cad_ir(payload, generation_mode=generation_mode)
        design = _active_design(_app)
        result = _generate_from_plan(design, generation_plan)
    except FusionAssemblyDocumentRequiredError as exc:
        _show_message(
            "Board Game Insert Generator requires an Assembly-compatible Fusion document.\n"
            f"{exc}\n\n"
            "Status: assembly document required."
        )
        return
    except FusionSkeletonError as exc:
        _show_message(
            "Board Game Insert Generator CAD IR error:\n"
            f"{exc}\n\n"
            f"{cad_ir_input_guidance(Path(__file__).resolve().parent)}"
        )
        return
    except Exception as exc:  # pragma: no cover - Fusion runtime boundary.
        if is_part_design_component_limit_error(exc):
            _show_message(
                "Board Game Insert Generator requires an Assembly-compatible Fusion document.\n"
                f"{assembly_document_required_message(exc)}\n\n"
                "Status: assembly document required."
            )
            return
        _show_message(f"Board Game Insert Generator Fusion error:\n{exc}")
        return

    _show_message(
        "Board Game Insert Generator generated compact and exploded CAD IR scene.\n"
        f"Project: {generation_plan.project_name}\n"
        f"Input CAD IR: {cad_ir_path}\n"
        f"Generation mode: {generation_plan.generation_mode}\n"
        f"Reference outlines: {result['reference_outlines']}\n"
        f"CAD IR module blanks planned: {len(generation_plan.blanks)}\n"
        f"Grid-positioned asset modules planned: {len(generation_plan.grid_positioned_blanks)}\n"
        f"Multi-layer grid modules planned: {generation_plan.multi_layer_grid_module_count}\n"
        f"Grid modules with Z placement: {generation_plan.grid_modules_with_z_placement_count}\n"
        f"Grid module height variants: {generation_plan.grid_module_height_variant_count}\n"
        f"Module components planned: {generation_plan.module_component_count}\n"
        f"Compact occurrences planned: {len(generation_plan.compact_occurrences)}\n"
        f"Exploded occurrences planned: {len(generation_plan.exploded_occurrences)}\n"
        f"Module components created: {result['module_components_created']}\n"
        f"Compact occurrences created: {result['compact_occurrences_created']}\n"
        f"Exploded occurrences created: {result['exploded_occurrences_created']}\n"
        f"Linked exploded occurrences: {result['linked_exploded_occurrences']}\n"
        "Occurrence direct rename attempted: no\n"
        f"Occurrence naming policy: {OCCURRENCE_NAME_POLICY_COMPONENT_SOURCE}\n"
        "Occurrence Browser names: Fusion-generated; BGIG source Component names and plan roles are authoritative.\n"
        f"Grid-positioned modules refused: {len(generation_plan.rejected_grid_modules)}\n"
        f"Rectangular cavity cuts: {result['cavity_cuts']}\n"
        f"Simple finger notch features planned: {result['finger_notch_features_planned']}\n"
        f"Simple finger notch sketches: {result['finger_notch_sketches']}\n"
        f"Simple top-open finger notch cuts: {result['finger_notch_cuts']}\n"
        "Finger notch topology: top-open rectangular wall cut.\n"
        "Compact placement source: CAD IR metadata.executable_asset_plan.\n"
        "Exploded placement source: linked occurrences on add-in deterministic inspection grid; dimensions from CAD IR.\n"
        "Creation scope: one Fusion component per BGIG module, compact/exploded occurrences linked.\n"
        "Status: manual validation required in Fusion 360."
    )


def stop(context) -> None:  # noqa: ANN001 - Fusion controls the signature.
    """Fusion 360 add-in shutdown hook."""

    _show_message("Board Game Insert Generator adapter stopped.")


def _active_design(application):  # noqa: ANN001 - Fusion API object.
    active_product = application.activeProduct if application else None
    if active_product is None:
        raise RuntimeError("No active Fusion product. Open or create a design first.")

    design = adsk.fusion.Design.cast(active_product)
    if design is None:
        raise RuntimeError("The active Fusion product is not a Design workspace.")
    return design


def _generate_from_plan(design, plan: FusionGenerationPlan) -> dict[str, int]:  # noqa: ANN001
    root_component = design.rootComponent
    _create_reference_outline(root_component, plan.reference_box)

    source_blanks = [*plan.blanks, *plan.grid_positioned_blanks]
    compact_occurrences_by_component_id = {
        occurrence.component_id: occurrence for occurrence in plan.compact_occurrences
    }
    created_bodies = {}
    created_components = {}
    compact_occurrence_count = 0

    for blank in source_blanks:
        occurrence_plan = compact_occurrences_by_component_id.get(blank.cad_id)
        if occurrence_plan is None:
            raise RuntimeError(f"Missing compact occurrence plan for {blank.body_name}.")
        occurrence, body = _create_module_component_occurrence(
            root_component,
            blank,
            occurrence_plan,
        )
        created_bodies[blank.cad_id] = body
        created_components[blank.cad_id] = occurrence.component
        compact_occurrence_count += 1

    source_blanks_by_id = {blank.cad_id: blank for blank in source_blanks}

    cavity_cut_count = 0
    for cavity_cut in plan.cavity_cuts:
        target_body = created_bodies.get(cavity_cut.target_body_id)
        target_component = created_components.get(cavity_cut.target_body_id)
        source_blank = source_blanks_by_id.get(cavity_cut.target_body_id)
        if target_body is None or target_component is None or source_blank is None:
            raise RuntimeError(
                f"Cavity {cavity_cut.cavity_id} targets unknown body "
                f"{cavity_cut.target_body_id}."
            )
        _create_rectangular_cavity_cut(
            target_component,
            cavity_cut,
            target_body,
            source_blank.origin_mm,
        )
        cavity_cut_count += 1

    finger_notch_sketch_count = 0
    finger_notch_cut_count = 0
    for notch_cut in plan.finger_notch_cuts:
        target_body = created_bodies.get(notch_cut.target_body_id)
        target_component = created_components.get(notch_cut.target_body_id)
        source_blank = source_blanks_by_id.get(notch_cut.target_body_id)
        if target_body is None or target_component is None or source_blank is None:
            raise RuntimeError(
                f"Finger notch {notch_cut.feature_id} targets unknown body "
                f"{notch_cut.target_body_id}."
            )
        result = _create_rectangular_finger_notch_cut(
            target_component,
            notch_cut,
            target_body,
            source_blank.origin_mm,
        )
        finger_notch_sketch_count += result["sketches"]
        finger_notch_cut_count += result["cuts"]

    exploded_occurrence_count = 0
    for occurrence_plan in plan.exploded_occurrences:
        module_component = created_components.get(occurrence_plan.component_id)
        if module_component is None:
            raise RuntimeError(
                f"Exploded occurrence {occurrence_plan.occurrence_name!r} targets unknown "
                f"component {occurrence_plan.component_id!r}."
            )
        _create_linked_module_occurrence(root_component, module_component, occurrence_plan)
        exploded_occurrence_count += 1

    return {
        "reference_outlines": 1,
        "module_components_created": len(created_components),
        "compact_occurrences_created": compact_occurrence_count,
        "exploded_occurrences_created": exploded_occurrence_count,
        "linked_exploded_occurrences": "yes" if plan.linked_exploded_occurrences else "no",
        "cavity_cuts": cavity_cut_count,
        "finger_notch_features_planned": len(plan.finger_notch_cuts),
        "finger_notch_sketches": finger_notch_sketch_count,
        "finger_notch_cuts": finger_notch_cut_count,
    }


def _create_reference_outline(root_component, solid_plan: FusionSolidPlan) -> None:  # noqa: ANN001
    if solid_plan.origin_mm.z != 0:
        raise RuntimeError("Reference box outline must stay on Z origin 0 mm.")
    sketch = root_component.sketches.add(root_component.xYConstructionPlane)
    sketch.name = f"{solid_plan.component_name} outline"
    _add_scene_rectangle(sketch, solid_plan)


def _create_module_component_occurrence(
    root_component,  # noqa: ANN001
    solid_plan: FusionSolidPlan,
    occurrence_plan,  # noqa: ANN001
):
    transform = _matrix_for_origin(occurrence_plan.origin_mm)
    try:
        occurrence = root_component.occurrences.addNewComponent(transform)
    except Exception as exc:
        if is_part_design_component_limit_error(exc):
            raise FusionAssemblyDocumentRequiredError(
                assembly_document_required_message(exc)
            ) from exc
        raise
    if occurrence is None:
        raise RuntimeError(
            "Fusion component creation failed. Use an assembly-capable Fusion design "
            "for linked compact/exploded module occurrences."
        )
    _apply_occurrence_transform(occurrence, transform)

    module_component = occurrence.component
    if module_component is None:
        raise RuntimeError(f"Fusion component is unavailable for {solid_plan.body_name}.")
    module_component.name = solid_plan.component_name
    body = _create_rectangular_blank(module_component, _local_solid_plan(solid_plan))
    return occurrence, body


def _create_linked_module_occurrence(root_component, module_component, occurrence_plan) -> None:  # noqa: ANN001
    transform = _matrix_for_origin(occurrence_plan.origin_mm)
    try:
        occurrence = root_component.occurrences.addExistingComponent(module_component, transform)
    except Exception as exc:
        if is_part_design_component_limit_error(exc):
            raise FusionAssemblyDocumentRequiredError(
                assembly_document_required_message(exc)
            ) from exc
        raise
    if occurrence is None:
        raise RuntimeError(
            f"Fusion linked exploded occurrence failed for {occurrence_plan.occurrence_name}."
        )
    _apply_occurrence_transform(occurrence, transform)


def _create_rectangular_blank(target_component, solid_plan: FusionSolidPlan):  # noqa: ANN001
    sketch_plane = _xy_plane_for_z(target_component, solid_plan.origin_mm.z, f"{solid_plan.component_name} footprint plane")
    sketch = target_component.sketches.add(sketch_plane)
    sketch.name = f"{solid_plan.component_name} footprint"
    _add_scene_rectangle(sketch, solid_plan)

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed profile was created for {solid_plan.body_name}.")

    profile = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByString(f"{solid_plan.size_mm.z} mm")
    extrude = target_component.features.extrudeFeatures.addSimple(
        profile,
        distance,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    if extrude is None:
        raise RuntimeError(f"Fusion extrusion failed for {solid_plan.body_name}.")

    extrude.name = f"{solid_plan.component_name} extrusion"
    if extrude.bodies.count < 1:
        raise RuntimeError(f"Fusion extrusion created no body for {solid_plan.body_name}.")
    body = extrude.bodies.item(0)
    body.name = solid_plan.body_name
    return body


def _create_rectangular_cavity_cut(
    target_component,  # noqa: ANN001
    cut_plan: FusionCavityCutPlan,
    target_body,  # noqa: ANN001
    body_origin_mm: FusionVectorMm,
) -> None:
    local_cut_origin = _relative_vector(cut_plan.cut_origin_mm, body_origin_mm)
    cut_plane = _create_offset_xy_plane(
        target_component,
        local_cut_origin.z,
        f"{cut_plan.component_name} {cut_plan.cavity_id} cavity cut plane",
    )
    sketch = target_component.sketches.add(cut_plane)
    sketch.name = f"{cut_plan.component_name} {cut_plan.cavity_id} cavity footprint"
    _add_scene_rectangle_from_mm(
        sketch,
        local_cut_origin.x,
        local_cut_origin.y,
        cut_plan.cut_size_mm.x,
        cut_plan.cut_size_mm.y,
        cut_plan.cavity_id,
    )

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed cut profile was created for {cut_plan.cavity_id}.")

    profile = sketch.profiles.item(0)
    extrudes = target_component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    if cut_input is None:
        raise RuntimeError(f"Fusion cut input failed for cavity {cut_plan.cavity_id}.")

    distance = adsk.core.ValueInput.createByString(f"{cut_plan.cut_size_mm.z} mm")
    extent = adsk.fusion.DistanceExtentDefinition.create(distance)
    if extent is None:
        raise RuntimeError(f"Fusion cut extent failed for cavity {cut_plan.cavity_id}.")
    ok = cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    if not ok:
        raise RuntimeError(f"Fusion cut distance failed for cavity {cut_plan.cavity_id}.")

    cut_input.participantBodies = [target_body]
    cut_feature = extrudes.add(cut_input)
    if cut_feature is None:
        raise RuntimeError(f"Fusion cut failed for cavity {cut_plan.cavity_id}.")
    cut_feature.name = f"{cut_plan.component_name} {cut_plan.cavity_id} cavity cut"


def _create_rectangular_finger_notch_cut(
    target_component,  # noqa: ANN001
    cut_plan: FusionFingerNotchCutPlan,
    target_body,  # noqa: ANN001
    body_origin_mm: FusionVectorMm,
) -> dict[str, int]:
    cut_plane = _create_finger_notch_plane(target_component, cut_plan, body_origin_mm)
    sketch = target_component.sketches.add(cut_plane)
    sketch.name = f"{cut_plan.component_name} {cut_plan.feature_id} finger notch wall footprint"
    _add_model_space_rectangle_on_sketch(
        sketch,
        _relative_vector(cut_plan.profile_start_mm, body_origin_mm),
        _relative_vector(cut_plan.profile_end_mm, body_origin_mm),
        cut_plan.feature_id,
    )

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed wall cut profile was created for {cut_plan.feature_id}.")

    profile = sketch.profiles.item(0)
    extrudes = target_component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    if cut_input is None:
        raise RuntimeError(f"Fusion cut input failed for finger notch {cut_plan.feature_id}.")

    distance = adsk.core.ValueInput.createByString(f"{cut_plan.cut_depth_mm} mm")
    extent = adsk.fusion.DistanceExtentDefinition.create(distance)
    if extent is None:
        raise RuntimeError(f"Fusion cut extent failed for finger notch {cut_plan.feature_id}.")
    ok = cut_input.setOneSideExtent(
        extent,
        _fusion_extent_direction(cut_plan.extrude_direction),
    )
    if not ok:
        raise RuntimeError(f"Fusion cut distance failed for finger notch {cut_plan.feature_id}.")

    cut_input.participantBodies = [target_body]
    cut_feature = extrudes.add(cut_input)
    if cut_feature is None:
        raise RuntimeError(f"Fusion cut failed for finger notch {cut_plan.feature_id}.")
    cut_feature.name = f"{cut_plan.component_name} {cut_plan.feature_id} finger notch wall cut"
    return {"sketches": 1, "cuts": 1}


def _create_finger_notch_plane(
    target_component,  # noqa: ANN001
    cut_plan: FusionFingerNotchCutPlan,
    body_origin_mm: FusionVectorMm,
):
    if cut_plan.sketch_plane == FUSION_SKETCH_PLANE_XZ:
        return _create_offset_xz_plane(
            target_component,
            cut_plan.sketch_plane_offset_mm - body_origin_mm.y,
            f"{cut_plan.component_name} {cut_plan.feature_id} finger notch XZ wall cut plane",
        )
    if cut_plan.sketch_plane == FUSION_SKETCH_PLANE_YZ:
        return _create_offset_yz_plane(
            target_component,
            cut_plan.sketch_plane_offset_mm - body_origin_mm.x,
            f"{cut_plan.component_name} {cut_plan.feature_id} finger notch YZ wall cut plane",
        )
    raise RuntimeError(
        f"Unsupported finger notch sketch plane {cut_plan.sketch_plane!r} for {cut_plan.feature_id}."
    )


def _fusion_extent_direction(direction: str):  # noqa: ANN001
    if direction == FUSION_EXTENT_POSITIVE:
        return adsk.fusion.ExtentDirections.PositiveExtentDirection
    if direction == FUSION_EXTENT_NEGATIVE:
        return adsk.fusion.ExtentDirections.NegativeExtentDirection
    raise RuntimeError(f"Unsupported Fusion extent direction {direction!r}.")



def _matrix_for_origin(origin_mm: FusionVectorMm):  # noqa: ANN001
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(
        mm_to_cm(origin_mm.x),
        mm_to_cm(origin_mm.y),
        mm_to_cm(origin_mm.z),
    )
    return transform


def _apply_occurrence_transform(occurrence, transform) -> None:  # noqa: ANN001
    try:
        occurrence.transform2 = transform
    except Exception:
        try:
            occurrence.transform = transform
        except Exception:
            pass


def _local_solid_plan(solid_plan: FusionSolidPlan) -> FusionSolidPlan:
    return FusionSolidPlan(
        cad_id=solid_plan.cad_id,
        component_name=solid_plan.component_name,
        body_name=solid_plan.body_name,
        origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
        size_mm=solid_plan.size_mm,
        role=solid_plan.role,
        printable=solid_plan.printable,
        operation_kind=solid_plan.operation_kind,
        validation_status=solid_plan.validation_status,
    )


def _relative_vector(vector: FusionVectorMm, origin: FusionVectorMm) -> FusionVectorMm:
    return FusionVectorMm(
        vector.x - origin.x,
        vector.y - origin.y,
        vector.z - origin.z,
    )


def _xy_plane_for_z(root_component, offset_z_mm: float, name: str):  # noqa: ANN001
    if offset_z_mm == 0:
        return root_component.xYConstructionPlane
    return _create_offset_xy_plane(root_component, offset_z_mm, name)

def _create_offset_xy_plane(root_component, offset_z_mm: float, name: str):  # noqa: ANN001
    plane_input = root_component.constructionPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(f"{offset_z_mm} mm")
    ok = plane_input.setByOffset(root_component.xYConstructionPlane, offset)
    if not ok:
        raise RuntimeError(f"Fusion construction plane offset failed for {name}.")
    plane = root_component.constructionPlanes.add(plane_input)
    if plane is None:
        raise RuntimeError(f"Fusion construction plane creation failed for {name}.")
    plane.name = name
    return plane


def _create_offset_xz_plane(root_component, offset_y_mm: float, name: str):  # noqa: ANN001
    plane_input = root_component.constructionPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(f"{offset_y_mm} mm")
    ok = plane_input.setByOffset(root_component.xZConstructionPlane, offset)
    if not ok:
        raise RuntimeError(f"Fusion construction plane offset failed for {name}.")
    plane = root_component.constructionPlanes.add(plane_input)
    if plane is None:
        raise RuntimeError(f"Fusion construction plane creation failed for {name}.")
    plane.name = name
    return plane


def _create_offset_yz_plane(root_component, offset_x_mm: float, name: str):  # noqa: ANN001
    plane_input = root_component.constructionPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(f"{offset_x_mm} mm")
    ok = plane_input.setByOffset(root_component.yZConstructionPlane, offset)
    if not ok:
        raise RuntimeError(f"Fusion construction plane offset failed for {name}.")
    plane = root_component.constructionPlanes.add(plane_input)
    if plane is None:
        raise RuntimeError(f"Fusion construction plane creation failed for {name}.")
    plane.name = name
    return plane


def _add_scene_rectangle(sketch, solid_plan: FusionSolidPlan) -> None:  # noqa: ANN001
    _add_scene_rectangle_from_mm(
        sketch,
        solid_plan.origin_mm.x,
        solid_plan.origin_mm.y,
        solid_plan.size_mm.x,
        solid_plan.size_mm.y,
        solid_plan.body_name,
    )


def _add_scene_rectangle_from_mm(
    sketch,  # noqa: ANN001
    origin_x_mm: float,
    origin_y_mm: float,
    size_x_mm: float,
    size_y_mm: float,
    label: str,
) -> None:
    start = adsk.core.Point3D.create(
        mm_to_cm(origin_x_mm),
        mm_to_cm(origin_y_mm),
        0,
    )
    end = adsk.core.Point3D.create(
        mm_to_cm(origin_x_mm + size_x_mm),
        mm_to_cm(origin_y_mm + size_y_mm),
        0,
    )
    lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(start, end)
    if lines is None:
        raise RuntimeError(f"Fusion rectangle sketch failed for {label}.")


def _add_model_space_rectangle_on_sketch(
    sketch,  # noqa: ANN001
    start_mm,  # noqa: ANN001
    end_mm,  # noqa: ANN001
    label: str,
) -> None:
    model_start = adsk.core.Point3D.create(
        mm_to_cm(start_mm.x),
        mm_to_cm(start_mm.y),
        mm_to_cm(start_mm.z),
    )
    model_end = adsk.core.Point3D.create(
        mm_to_cm(end_mm.x),
        mm_to_cm(end_mm.y),
        mm_to_cm(end_mm.z),
    )
    start = sketch.modelToSketchSpace(model_start)
    end = sketch.modelToSketchSpace(model_end)
    if start is None or end is None:
        raise RuntimeError(f"Fusion model-to-sketch conversion failed for {label}.")

    lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(start, end)
    if lines is None:
        raise RuntimeError(f"Fusion wall rectangle sketch failed for {label}.")


def _show_message(message: str) -> None:
    if _ui is not None:
        _ui.messageBox(message)
