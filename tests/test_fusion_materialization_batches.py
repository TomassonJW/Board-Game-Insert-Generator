from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fusion_addin.BoardGameInsertGenerator import (
    BoardGameInsertGenerator as fusion_entrypoint,
)
from fusion_addin.BoardGameInsertGenerator.fusion_skeleton import (
    FusionAdditivePrismPlan,
    FusionCavityCutPlan,
    FusionVectorMm,
)


class _Collection:
    def __init__(self) -> None:
        self.items: list[object] = []

    @property
    def count(self) -> int:
        return len(self.items)

    def add(self, value: object) -> None:
        self.items.append(value)

    def item(self, index: int) -> object:
        return self.items[index]


class _ObjectCollection:
    @staticmethod
    def create() -> _Collection:
        return _Collection()


class _GeometryFactory:
    @staticmethod
    def create(*values: object) -> tuple[object, ...]:
        return values


class _TemporaryBRepManager:
    instance = None

    def __init__(self) -> None:
        self.boxes: list[object] = []

    @classmethod
    def get(cls):
        return cls.instance

    def createBox(self, box):  # noqa: ANN001, N802 - Fusion API spelling.
        body = SimpleNamespace(box=box, operations=[])
        self.boxes.append(body)
        return body

    def booleanOperation(  # noqa: ANN001, N802 - Fusion API spelling.
        self,
        target,
        tool,
        operation,
    ) -> bool:
        target.operations.append((operation, tool.box))
        return True


class _BaseFeature:
    def __init__(self) -> None:
        self.name = ""
        self.sourceBodies = _Collection()
        self.bodies = _Collection()
        self.started = False
        self.finished = False

    def startEdit(self) -> bool:  # noqa: N802 - Fusion API spelling.
        self.started = True
        return True

    def finishEdit(self) -> bool:  # noqa: N802 - Fusion API spelling.
        self.finished = True
        for source_body in self.sourceBodies.items:
            self.bodies.add(
                SimpleNamespace(
                    box=source_body.box,
                    operations=list(source_body.operations),
                    body_kind="result",
                    name="",
                )
            )
        return True


class _BaseFeatures:
    def __init__(self) -> None:
        self.created: list[_BaseFeature] = []

    def add(self) -> _BaseFeature:
        feature = _BaseFeature()
        self.created.append(feature)
        return feature


class _BRepBodies:
    def add(self, body, base_feature):  # noqa: ANN001
        source_body = SimpleNamespace(
            box=body.box,
            operations=list(body.operations),
            body_kind="source",
        )
        base_feature.sourceBodies.add(source_body)
        return source_body


class _CombineFeatures:
    def __init__(self) -> None:
        self.inputs: list[object] = []
        self.features: list[object] = []

    def createInput(self, target_body, tool_bodies):  # noqa: ANN001, N802
        if any(
            getattr(tool_body, "body_kind", "") != "result"
            for tool_body in tool_bodies.items
        ):
            raise RuntimeError(
                "ALL_TOOL_BODY_REFERENCE_LOST: source bodies cannot be combined "
                "after BaseFeature.finishEdit."
            )
        value = SimpleNamespace(
            targetBody=target_body,
            toolBodies=tool_bodies,
            operation=None,
            isKeepToolBodies=True,
            isNewComponent=True,
        )
        self.inputs.append(value)
        return value

    def add(self, value):  # noqa: ANN001
        feature = SimpleNamespace(name="", input=value)
        self.features.append(feature)
        return feature


def _fake_adsk(manager: _TemporaryBRepManager):
    _TemporaryBRepManager.instance = manager
    return SimpleNamespace(
        core=SimpleNamespace(
            ObjectCollection=_ObjectCollection,
            Point3D=_GeometryFactory,
            Vector3D=_GeometryFactory,
            OrientedBoundingBox3D=_GeometryFactory,
        ),
        fusion=SimpleNamespace(
            TemporaryBRepManager=_TemporaryBRepManager,
            BooleanTypes=SimpleNamespace(
                UnionBooleanType="union",
                DifferenceBooleanType="difference",
            ),
            FeatureOperations=SimpleNamespace(
                JoinFeatureOperation="join",
                CutFeatureOperation="cut",
            ),
        ),
    )


def _component():
    base_features = _BaseFeatures()
    combine_features = _CombineFeatures()
    return SimpleNamespace(
        features=SimpleNamespace(
            baseFeatures=base_features,
            combineFeatures=combine_features,
        ),
        bRepBodies=_BRepBodies(),
    )


class FusionMaterializationBatchTests(unittest.TestCase):
    def test_additive_prisms_use_transient_unions_and_one_stable_body(self) -> None:
        component = _component()
        manager = _TemporaryBRepManager()
        solid = SimpleNamespace(
            origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
            size_mm=FusionVectorMm(10.0, 10.0, 20.0),
            component_name="A",
            body_name="A body",
        )
        joins = tuple(
            FusionAdditivePrismPlan(
                component_id="component:a",
                component_name="A",
                target_body_id="body:a",
                target_body_name="A body",
                operation_id=f"join:{index}",
                local_origin_mm=FusionVectorMm(index * 10.0, 0.0, 0.0),
                size_mm=FusionVectorMm(10.0, 10.0, 20.0),
            )
            for index in range(3)
        )

        with patch.object(
            fusion_entrypoint,
            "adsk",
            _fake_adsk(manager),
        ):
            body = fusion_entrypoint._create_boolean_rectangular_blank(
                component,
                solid,
                joins,
                (),
                body_origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
            )

        self.assertEqual(len(manager.boxes), 4)
        self.assertEqual(len(component.features.baseFeatures.created), 1)
        self.assertEqual(len(component.features.combineFeatures.inputs), 0)
        self.assertEqual(
            [operation for operation, _ in body.operations],
            ["union", "union", "union"],
        )
        self.assertEqual(body.name, "A body")

    def test_cavities_keep_negative_depth_in_one_stable_boolean_body(self) -> None:
        component = _component()
        manager = _TemporaryBRepManager()
        solid = SimpleNamespace(
            origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
            size_mm=FusionVectorMm(50.0, 30.0, 30.0),
            component_name="A",
            body_name="A body",
        )
        cuts = tuple(
            FusionCavityCutPlan(
                component_id="component:a",
                component_name="A",
                target_body_id="body:a",
                target_body_name="A body",
                operation_id=f"cut:{index}",
                cavity_id=f"cavity:{index}",
                cut_origin_mm=FusionVectorMm(20.0 * index, 0.0, 30.0),
                cut_size_mm=FusionVectorMm(10.0, 10.0, 12.0),
                requested_local_origin_mm=FusionVectorMm(
                    20.0 * index,
                    0.0,
                    18.0,
                ),
                retained_floor_mm=2.0,
            )
            for index in range(2)
        )

        with patch.object(
            fusion_entrypoint,
            "adsk",
            _fake_adsk(manager),
        ):
            body = fusion_entrypoint._create_boolean_rectangular_blank(
                component,
                solid,
                (),
                cuts,
                body_origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
            )

        self.assertEqual(len(manager.boxes), 3)
        first_obb = manager.boxes[1].box
        self.assertAlmostEqual(first_obb[0][2], 2.4)
        self.assertAlmostEqual(first_obb[5], 1.2)
        self.assertEqual(
            [operation for operation, _ in body.operations],
            ["difference", "difference"],
        )
        self.assertEqual(len(component.features.combineFeatures.inputs), 0)

    def test_buried_flat_inset_brep_tool_uses_declared_interval(self) -> None:
        component = _component()
        manager = _TemporaryBRepManager()
        solid = SimpleNamespace(
            origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
            size_mm=FusionVectorMm(50.0, 30.0, 69.8),
            component_name="A",
            body_name="A body",
        )
        cut = FusionCavityCutPlan(
            component_id="component:a",
            component_name="A",
            target_body_id="body:a",
            target_body_name="A body",
            operation_id="cut:buried-booklet",
            cavity_id="booklet:buried",
            cut_origin_mm=FusionVectorMm(0.0, 0.0, 65.8),
            cut_size_mm=FusionVectorMm(10.0, 10.0, 2.0),
            requested_local_origin_mm=FusionVectorMm(
                0.0,
                0.0,
                63.8,
            ),
            retained_floor_mm=63.8,
            cavity_source="top_inset_reservation",
            boolean_operation="difference",
            geometry_attribution="flat_inset",
            positive_geometry_digest="positive-digest",
            local_interval_bottom_z_mm=63.8,
            local_interval_top_z_mm=65.8,
        )

        with patch.object(
            fusion_entrypoint,
            "adsk",
            _fake_adsk(manager),
        ):
            fusion_entrypoint._create_boolean_rectangular_blank(
                component,
                solid,
                (),
                (cut,),
                body_origin_mm=FusionVectorMm(0.0, 0.0, 0.0),
            )

        self.assertEqual(len(manager.boxes), 2)
        tool_obb = manager.boxes[1].box
        self.assertAlmostEqual(tool_obb[0][2], 6.48)
        self.assertAlmostEqual(tool_obb[5], 0.2)
        self.assertEqual(
            cut.to_dict()["brep_tool_interval_z_mm"],
            {"bottom": 63.8, "top": 65.8},
        )

    def test_failed_generation_cleanup_reports_clean_and_incomplete_rollbacks(self) -> None:
        class _Registry:
            def __init__(self, clear_result: dict[str, object]) -> None:
                self.clear_result = clear_result
                self.calls = 0

            def clear(self) -> dict[str, object]:
                self.calls += 1
                return self.clear_result

        clean_registry = _Registry(
            {
                "bgig_objects_remaining": 0,
                "scene_roots_after": 0,
            }
        )
        clean = fusion_entrypoint._rollback_failed_generation(clean_registry)

        self.assertEqual(clean_registry.calls, 1)
        self.assertTrue(clean["clean"])
        self.assertEqual(clean["remaining"], 0)

        incomplete_registry = _Registry(
            {
                "bgig_objects_remaining": 3,
                "scene_roots_after": 1,
            }
        )
        incomplete = fusion_entrypoint._rollback_failed_generation(
            incomplete_registry
        )

        self.assertEqual(incomplete_registry.calls, 1)
        self.assertFalse(incomplete["clean"])
        self.assertEqual(incomplete["remaining"], 3)


if __name__ == "__main__":
    unittest.main()
