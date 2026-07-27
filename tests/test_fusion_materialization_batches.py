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
        body = SimpleNamespace(box=box)
        self.boxes.append(body)
        return body


class _BaseFeature:
    def __init__(self) -> None:
        self.name = ""
        self.bodies = _Collection()
        self.started = False
        self.finished = False

    def startEdit(self) -> bool:  # noqa: N802 - Fusion API spelling.
        self.started = True
        return True

    def finishEdit(self) -> bool:  # noqa: N802 - Fusion API spelling.
        self.finished = True
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
        base_feature.bodies.add(body)
        return body


class _CombineFeatures:
    def __init__(self) -> None:
        self.inputs: list[object] = []
        self.features: list[object] = []

    def createInput(self, target_body, tool_bodies):  # noqa: ANN001, N802
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
    def test_additive_prisms_use_one_base_feature_and_one_combine(self) -> None:
        component = _component()
        manager = _TemporaryBRepManager()
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
            fusion_entrypoint._create_joined_rectangular_prism_batch(
                component,
                joins,
                object(),
            )

        self.assertEqual(len(manager.boxes), 3)
        self.assertEqual(len(component.features.baseFeatures.created), 1)
        self.assertEqual(len(component.features.combineFeatures.inputs), 1)
        combine = component.features.combineFeatures.inputs[0]
        self.assertEqual(combine.toolBodies.count, 3)
        self.assertEqual(combine.operation, "join")
        self.assertFalse(combine.isKeepToolBodies)

    def test_cavities_keep_negative_depth_and_use_one_combine(self) -> None:
        component = _component()
        manager = _TemporaryBRepManager()
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
            fusion_entrypoint._create_rectangular_cavity_cut_batch(
                component,
                cuts,
                object(),
                FusionVectorMm(0.0, 0.0, 0.0),
            )

        self.assertEqual(len(manager.boxes), 2)
        first_obb = manager.boxes[0].box
        self.assertAlmostEqual(first_obb[0][2], 2.4)
        self.assertAlmostEqual(first_obb[5], 1.2)
        self.assertEqual(len(component.features.combineFeatures.inputs), 1)
        combine = component.features.combineFeatures.inputs[0]
        self.assertEqual(combine.toolBodies.count, 2)
        self.assertEqual(combine.operation, "cut")
        self.assertFalse(combine.isKeepToolBodies)


if __name__ == "__main__":
    unittest.main()
