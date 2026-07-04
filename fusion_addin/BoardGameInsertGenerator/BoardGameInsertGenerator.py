"""Fusion 360 add-in entry point for Board Game Insert Generator.

P6-M001 creates rectangular blank bodies and simple top-open rectangular cavity
cuts from a serialized CAD IR. Fusion consumes already resolved CAD IR dimensions
and must not recalculate layout, cavities, clearances, or tolerances.
"""

from __future__ import annotations

from pathlib import Path

try:
    from .fusion_skeleton import (
        DOCUMENT_STATUS_ZERO_DOC,
        FusionCavityCutPlan,
        FusionGenerationPlan,
        FusionSkeletonError,
        FusionSolidPlan,
        cad_ir_input_guidance,
        describe_document_state,
        generation_plan_from_cad_ir,
        load_cad_ir_json,
        mm_to_cm,
        resolve_cad_ir_input_path,
    )
except ImportError:  # pragma: no cover - Fusion may load the file as a script.
    from fusion_skeleton import (  # type: ignore[no-redef]
        DOCUMENT_STATUS_ZERO_DOC,
        FusionCavityCutPlan,
        FusionGenerationPlan,
        FusionSkeletonError,
        FusionSolidPlan,
        cad_ir_input_guidance,
        describe_document_state,
        generation_plan_from_cad_ir,
        load_cad_ir_json,
        mm_to_cm,
        resolve_cad_ir_input_path,
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
        payload = load_cad_ir_json(cad_ir_path)
        generation_plan = generation_plan_from_cad_ir(payload)
        design = _active_design(_app)
        result = _generate_from_plan(design, generation_plan)
    except FusionSkeletonError as exc:
        _show_message(
            "Board Game Insert Generator CAD IR error:\n"
            f"{exc}\n\n"
            f"{cad_ir_input_guidance(Path(__file__).resolve().parent)}"
        )
        return
    except Exception as exc:  # pragma: no cover - Fusion runtime boundary.
        _show_message(f"Board Game Insert Generator Fusion error:\n{exc}")
        return

    _show_message(
        "Board Game Insert Generator generated rectangular blanks and cavities.\n"
        f"Project: {generation_plan.project_name}\n"
        f"Input CAD IR: {cad_ir_path}\n"
        f"Reference outlines: {result['reference_outlines']}\n"
        f"Blank bodies: {result['blank_bodies']}\n"
        f"Rectangular cavity cuts: {result['cavity_cuts']}\n"
        "Creation scope: root component, compatible with Part Design documents.\n"
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

    created_bodies = {}
    for blank in plan.blanks:
        created_bodies[blank.cad_id] = _create_rectangular_blank(root_component, blank)

    cavity_cut_count = 0
    for cavity_cut in plan.cavity_cuts:
        target_body = created_bodies.get(cavity_cut.target_body_id)
        if target_body is None:
            raise RuntimeError(
                f"Cavity {cavity_cut.cavity_id} targets unknown body "
                f"{cavity_cut.target_body_id}."
            )
        _create_rectangular_cavity_cut(root_component, cavity_cut, target_body)
        cavity_cut_count += 1

    return {
        "reference_outlines": 1,
        "blank_bodies": len(created_bodies),
        "cavity_cuts": cavity_cut_count,
    }


def _create_reference_outline(root_component, solid_plan: FusionSolidPlan) -> None:  # noqa: ANN001
    _ensure_supported_z_origin(solid_plan)
    sketch = root_component.sketches.add(root_component.xYConstructionPlane)
    sketch.name = f"{solid_plan.component_name} outline"
    _add_scene_rectangle(sketch, solid_plan)


def _create_rectangular_blank(root_component, solid_plan: FusionSolidPlan):  # noqa: ANN001
    _ensure_supported_z_origin(solid_plan)
    sketch = root_component.sketches.add(root_component.xYConstructionPlane)
    sketch.name = f"{solid_plan.component_name} footprint"
    _add_scene_rectangle(sketch, solid_plan)

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed profile was created for {solid_plan.body_name}.")

    profile = sketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByString(f"{solid_plan.size_mm.z} mm")
    extrude = root_component.features.extrudeFeatures.addSimple(
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


def _create_rectangular_cavity_cut(root_component, cut_plan: FusionCavityCutPlan, target_body) -> None:  # noqa: ANN001
    cut_plane = _create_offset_xy_plane(
        root_component,
        cut_plan.cut_origin_mm.z,
        f"{cut_plan.component_name} {cut_plan.cavity_id} cavity cut plane",
    )
    sketch = root_component.sketches.add(cut_plane)
    sketch.name = f"{cut_plan.component_name} {cut_plan.cavity_id} cavity footprint"
    _add_scene_rectangle_from_mm(
        sketch,
        cut_plan.cut_origin_mm.x,
        cut_plan.cut_origin_mm.y,
        cut_plan.cut_size_mm.x,
        cut_plan.cut_size_mm.y,
        cut_plan.cavity_id,
    )

    if sketch.profiles.count < 1:
        raise RuntimeError(f"No closed cut profile was created for {cut_plan.cavity_id}.")

    profile = sketch.profiles.item(0)
    extrudes = root_component.features.extrudeFeatures
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


def _ensure_supported_z_origin(solid_plan: FusionSolidPlan) -> None:
    if solid_plan.origin_mm.z != 0:
        raise RuntimeError(
            "P6-M001 root-component generation only supports Z origins at 0 mm. "
            f"{solid_plan.body_name} has Z origin {solid_plan.origin_mm.z} mm."
        )


def _show_message(message: str) -> None:
    if _ui is not None:
        _ui.messageBox(message)
