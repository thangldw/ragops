"""RAGOps public API."""

from ragops.engine import compare, evaluate
from ragops.drift import detect_evaluator_drift
from ragops.loader import load_responses, load_scenario, responses_from_data, scenario_from_dict
from ragops.statistical import (
    compare_replay_bundles,
    load_replay_bundle,
    replay_bundle_from_dict,
)
from ragops.provenance import diagnose_provenance
from ragops.sequential import compare_replay_bundles_sequentially

__version__ = "1.1.0"

__all__ = [
    "compare",
    "compare_replay_bundles_sequentially",
    "detect_evaluator_drift",
    "diagnose_provenance",
    "evaluate",
    "compare_replay_bundles",
    "load_replay_bundle",
    "load_responses",
    "load_scenario",
    "responses_from_data",
    "replay_bundle_from_dict",
    "scenario_from_dict",
    "__version__",
]
