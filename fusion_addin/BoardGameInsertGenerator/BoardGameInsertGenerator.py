"""Fusion 360 add-in entry point for Board Game Insert Generator.

P4-M002 is a skeleton only. It detects Fusion's active document state and can
prepare a non-executable operation plan from CAD IR, but it does not create
components, bodies, sketches, extrusions, or exports.
"""

from __future__ import annotations

try:
    from .fusion_skeleton import (
        DOCUMENT_STATUS_ZERO_DOC,
        describe_document_state,
    )
except ImportError:  # pragma: no cover - Fusion may load the file as a script.
    from fusion_skeleton import (  # type: ignore[no-redef]
        DOCUMENT_STATUS_ZERO_DOC,
        describe_document_state,
    )

try:
    import adsk.core  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised only outside Fusion.
    adsk = None  # type: ignore[assignment]


_app = None
_ui = None


def run(context) -> None:  # noqa: ANN001 - Fusion controls the signature.
    """Fusion 360 add-in startup hook.

    The hook reports readiness and explicitly stops at the Zero Doc boundary.
    No CAD operation is executed in P4-M002.
    """

    global _app, _ui

    if adsk is None:
        return

    _app = adsk.core.Application.get()
    _ui = _app.userInterface if _app else None
    state = describe_document_state(_app)

    lines = [
        "Board Game Insert Generator adapter skeleton loaded.",
        state.message,
        "P4-M002 does not create Fusion geometry.",
    ]
    if state.document_name:
        lines.insert(2, f"Active document: {state.document_name}")
    if state.status == DOCUMENT_STATUS_ZERO_DOC:
        lines.append("Open or create a Fusion design before future generation.")

    _show_message("\n".join(lines))


def stop(context) -> None:  # noqa: ANN001 - Fusion controls the signature.
    """Fusion 360 add-in shutdown hook."""

    _show_message("Board Game Insert Generator adapter skeleton stopped.")


def _show_message(message: str) -> None:
    if _ui is not None:
        _ui.messageBox(message)
