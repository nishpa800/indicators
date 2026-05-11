"""
python_ports.squarify — canonical Python port of the Squarify indicator
family.

Active canonical port: ``canonical_46_v2`` (mirrors
``squarify/versions/SQUARIFY_46_v2_2026-05-04.pine``).

Per SD-002 (never modify, always new-version), older versions of the
Squarify Pine source remain in ``squarify/versions/`` for traceability.
"""
from . import canonical_46_v2
from .canonical_46_v2 import (
    DEFAULTS,
    DETECTIONS,
    STATE_MACHINES,
    STUBBED,
)

__all__ = [
    "canonical_46_v2",
    "DEFAULTS",
    "DETECTIONS",
    "STATE_MACHINES",
    "STUBBED",
]
