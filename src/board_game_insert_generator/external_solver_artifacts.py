"""Verrous reproductibles des moteurs externes du tournoi P64-L07.

Les binaires et caches restent hors Git. Ce module valide le reçu versionné et
vérifie les artefacts locaux avant toute exécution d'un worker externe.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Mapping

from board_game_insert_generator.incremental_project_state import canonical_digest


EXTERNAL_SOLVER_ARTIFACT_LOCK_SCHEMA_V1 = (
    "bgig.external_solver_artifact_lock.v1"
)
EXTERNAL_SOLVER_ARTIFACT_RECEIPT_SCHEMA_V1 = (
    "bgig.external_solver_artifact_receipt.v1"
)
_PRODUCT_GATES = {
    "candidate",
    "benchmark_only_pending_epl_edl_dual_license_review",
    "benchmark_only_pending_bundled_native_license_inventory",
}


class ExternalSolverArtifactError(ValueError):
    """Verrou ou artefact externe invalide."""


def validate_external_solver_artifact_lock(lock: object) -> dict[str, object]:
    """Valide le verrou sans accepter de chemin local ni de digest implicite."""

    payload = _mapping(lock, "external solver artifact lock")
    supplied_digest = payload.pop("lock_digest", None)
    if payload.get("schema_version") != EXTERNAL_SOLVER_ARTIFACT_LOCK_SCHEMA_V1:
        raise ExternalSolverArtifactError(
            "Unsupported external solver artifact lock schema."
        )
    if not _is_digest(supplied_digest) or canonical_digest(payload) != supplied_digest:
        raise ExternalSolverArtifactError(
            "External solver artifact lock digest mismatch."
        )
    candidates = payload.get("candidates")
    artifacts = payload.get("artifacts")
    if (
        not isinstance(candidates, list)
        or len(candidates) < 3
        or not isinstance(artifacts, list)
        or not artifacts
        or payload.get("artifact_count") != len(artifacts)
    ):
        raise ExternalSolverArtifactError(
            "External solver artifact lock inventory is incomplete."
        )
    candidate_ids: set[str] = set()
    families: set[str] = set()
    for raw_candidate in candidates:
        candidate = _mapping(raw_candidate, "artifact lock candidate")
        candidate_id = _identifier(candidate.get("candidate_id"), "candidate id")
        if candidate_id in candidate_ids:
            raise ExternalSolverArtifactError(
                "External solver candidate identifiers must be unique."
            )
        candidate_ids.add(candidate_id)
        families.add(_identifier(candidate.get("family"), "candidate family"))
        _identifier(candidate.get("version"), "candidate version")
        _url(candidate.get("source_url"), "candidate source URL")
        _identifier(candidate.get("license"), "candidate license")
        if candidate.get("product_gate") not in _PRODUCT_GATES:
            raise ExternalSolverArtifactError(
                "External solver product gate is unsupported."
            )
        if not isinstance(candidate.get("exact_for_floor_model"), bool):
            raise ExternalSolverArtifactError(
                "External solver exactness must be explicit."
            )
    if len(families) < 3:
        raise ExternalSolverArtifactError(
            "External solver lock must cover at least three families."
        )
    seen: set[tuple[str, str]] = set()
    artifact_candidates: set[str] = set()
    for raw_artifact in artifacts:
        artifact = _mapping(raw_artifact, "artifact lock artifact")
        candidate_id = _identifier(
            artifact.get("candidate_id"), "artifact candidate id"
        )
        if candidate_id not in candidate_ids:
            raise ExternalSolverArtifactError(
                "Artifact references an unknown external solver candidate."
            )
        group = _identifier(artifact.get("artifact_group"), "artifact group")
        filename = _portable_filename(artifact.get("filename"))
        key = (group, filename)
        if key in seen:
            raise ExternalSolverArtifactError(
                "External solver artifact paths must be unique."
            )
        seen.add(key)
        artifact_candidates.add(candidate_id)
        byte_count = artifact.get("byte_count")
        if (
            isinstance(byte_count, bool)
            or not isinstance(byte_count, int)
            or byte_count <= 0
            or not _is_digest(artifact.get("sha256"))
        ):
            raise ExternalSolverArtifactError(
                "External solver artifact size or digest is invalid."
            )
        _url(artifact.get("source_url"), "artifact source URL")
        _identifier(artifact.get("license"), "artifact license")
    if artifact_candidates != candidate_ids:
        raise ExternalSolverArtifactError(
            "Every external solver candidate needs locked artifacts."
        )
    invariants = _mapping(payload.get("invariants"), "artifact lock invariants")
    if invariants != {
        "artifacts_embedded_in_repository": False,
        "download_before_lock_allowed": True,
        "execution_count_at_lock": 0,
        "global_install_count": 0,
        "offline_execution_required": True,
    }:
        raise ExternalSolverArtifactError(
            "External solver artifact lock invariants are invalid."
        )
    payload["lock_digest"] = supplied_digest
    return deepcopy(payload)


def external_solver_candidate_catalog(
    lock: object,
) -> tuple[dict[str, object], ...]:
    """Retourne les candidats canoniques du verrou."""

    validated = validate_external_solver_artifact_lock(lock)
    return tuple(deepcopy(validated["candidates"]))


def verify_external_solver_artifacts(
    lock: object,
    candidate_id: str,
    artifact_root: str | Path,
) -> dict[str, object]:
    """Vérifie tous les fichiers locaux d'un candidat avant son worker."""

    validated = validate_external_solver_artifact_lock(lock)
    candidate = _identifier(candidate_id, "candidate id")
    known = {
        str(item["candidate_id"]) for item in validated["candidates"]
    }
    if candidate not in known:
        raise ExternalSolverArtifactError(
            f"Unknown external solver candidate {candidate!r}."
        )
    root = Path(artifact_root).resolve()
    if not root.is_dir():
        raise ExternalSolverArtifactError(
            "External solver artifact root does not exist."
        )
    records: list[dict[str, object]] = []
    for artifact in validated["artifacts"]:
        if artifact["candidate_id"] != candidate:
            continue
        group = str(artifact["artifact_group"])
        filename = str(artifact["filename"])
        path = (root / group / filename).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ExternalSolverArtifactError(
                "External solver artifact escapes its root."
            ) from exc
        if not path.is_file():
            raise ExternalSolverArtifactError(
                f"Missing locked external solver artifact {group}/{filename}."
            )
        digest = _sha256_path(path)
        byte_count = path.stat().st_size
        if digest != artifact["sha256"] or byte_count != artifact["byte_count"]:
            raise ExternalSolverArtifactError(
                f"External solver artifact mismatch for {group}/{filename}."
            )
        records.append(
            {
                "artifact_group": group,
                "byte_count": byte_count,
                "filename": filename,
                "sha256": digest,
            }
        )
    records.sort(key=lambda item: (item["artifact_group"], item["filename"]))
    receipt: dict[str, object] = {
        "schema_version": EXTERNAL_SOLVER_ARTIFACT_RECEIPT_SCHEMA_V1,
        "candidate_id": candidate,
        "lock_digest": validated["lock_digest"],
        "artifact_count": len(records),
        "bundle_byte_count": sum(int(item["byte_count"]) for item in records),
        "artifacts": records,
        "verified_before_execution": True,
    }
    receipt["bundle_digest"] = canonical_digest(receipt)
    return receipt


def validate_external_solver_artifact_receipt(
    receipt: object,
    *,
    lock: object,
    candidate_id: str,
) -> dict[str, object]:
    """Lie un reçu déjà calculé au candidat et au verrou courants."""

    validated_lock = validate_external_solver_artifact_lock(lock)
    payload = _mapping(receipt, "external solver artifact receipt")
    supplied_digest = payload.pop("bundle_digest", None)
    if (
        payload.get("schema_version")
        != EXTERNAL_SOLVER_ARTIFACT_RECEIPT_SCHEMA_V1
        or payload.get("candidate_id") != candidate_id
        or payload.get("lock_digest") != validated_lock["lock_digest"]
        or payload.get("verified_before_execution") is not True
        or not _is_digest(supplied_digest)
        or canonical_digest(payload) != supplied_digest
    ):
        raise ExternalSolverArtifactError(
            "External solver artifact receipt is invalid."
        )
    artifacts = payload.get("artifacts")
    expected = [
        {
            "artifact_group": item["artifact_group"],
            "byte_count": item["byte_count"],
            "filename": item["filename"],
            "sha256": item["sha256"],
        }
        for item in validated_lock["artifacts"]
        if item["candidate_id"] == candidate_id
    ]
    expected.sort(key=lambda item: (item["artifact_group"], item["filename"]))
    if (
        not isinstance(artifacts, list)
        or payload.get("artifact_count") != len(artifacts)
        or not artifacts
        or artifacts != expected
        or payload.get("bundle_byte_count")
        != sum(
            int(_mapping(item, "artifact receipt item")["byte_count"])
            for item in artifacts
        )
    ):
        raise ExternalSolverArtifactError(
            "External solver artifact receipt inventory is invalid."
        )
    payload["bundle_digest"] = supplied_digest
    return deepcopy(payload)


def _sha256_path(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ExternalSolverArtifactError(f"{field} must be an object.")
    return deepcopy(dict(value))


def _identifier(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ExternalSolverArtifactError(f"{field} must be a string.")
    result = value.strip()
    if (
        not result
        or len(result) > 256
        or any(character in result for character in ("/", "\\", "\t", "\n"))
    ):
        raise ExternalSolverArtifactError(f"{field} is invalid.")
    return result


def _portable_filename(value: object) -> str:
    result = _identifier(value, "artifact filename")
    if Path(result).name != result or result in {".", ".."}:
        raise ExternalSolverArtifactError(
            "Artifact filename must be a portable basename."
        )
    return result


def _url(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ExternalSolverArtifactError(f"{field} must be a string.")
    result = value.strip()
    if (
        not result.startswith("https://")
        or len(result) > 2048
        or any(character in result for character in ("\t", "\n", "\r"))
    ):
        raise ExternalSolverArtifactError(f"{field} must use HTTPS.")
    return result


def _is_digest(value: object) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
