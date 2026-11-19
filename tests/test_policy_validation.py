"""Directly construct invalid statistical/sequential policies: each must raise ContractError."""

import dataclasses
import math

import pytest

from ragops.config import load_sequential_policy, load_statistical_policy
from ragops.loader import ContractError
from ragops.models import StatisticalMetricGate
from ragops.sequential import _validate_policy as validate_sequential
from ragops.statistical import _validate_policy as validate_statistical

STAT = load_statistical_policy("scenarios/statistical_gate/policy.toml")
SEQ = load_sequential_policy("scenarios/statistical_gate/sequential-policy.toml")
GATE = next(iter(STAT.metric_gates.values()))
BAD_GATES = [
    StatisticalMetricGate(direction="sideways", minimum=0.5, max_regression=0.1),
    StatisticalMetricGate(direction="higher", minimum=None, max_regression=0.1),
    StatisticalMetricGate(direction="higher", minimum=0.5, maximum=0.6, max_regression=0.1),
    StatisticalMetricGate(direction="lower", maximum=None, max_regression=0.1),
    StatisticalMetricGate(direction="lower", maximum=0.5, minimum=0.1, max_regression=0.1),
    StatisticalMetricGate(direction="higher", minimum=math.inf, max_regression=0.1),
    StatisticalMetricGate(direction="lower", maximum=math.nan, max_regression=0.1),
    StatisticalMetricGate(direction="higher", minimum=0.5, max_regression=-1),
    StatisticalMetricGate(direction="higher", minimum=0.5, max_regression=math.inf),
]
COMMON = [
    {"confidence": 0.4}, {"confidence": 1.0}, {"confidence": math.nan}, {"minimum_cases": 0},
    {"minimum_cases": True}, {"minimum_cases": 1.5}, {"resamples": 50}, {"resamples": True},
    {"resamples": 100.5}, {"seed": "x"}, {"seed": True}, {"metric_gates": {}},
]


def test_valid_policies_pass() -> None:
    validate_statistical(STAT)
    validate_sequential(SEQ)


@pytest.mark.parametrize("change", COMMON, ids=str)
def test_common_bad_values_are_rejected(change: dict) -> None:
    with pytest.raises(ContractError):
        validate_statistical(dataclasses.replace(STAT, **change))
    with pytest.raises(ContractError):
        validate_sequential(dataclasses.replace(SEQ, **change))


@pytest.mark.parametrize("gate", BAD_GATES, ids=lambda g: f"{g.direction}-{g.minimum}-{g.maximum}-{g.max_regression}")
def test_bad_gates_are_rejected(gate: StatisticalMetricGate) -> None:
    with pytest.raises(ContractError):
        validate_statistical(dataclasses.replace(STAT, metric_gates={"m": gate}))
    with pytest.raises(ContractError):
        validate_sequential(dataclasses.replace(SEQ, metric_gates={"m": gate}))


def test_statistical_rejects_empty_metric_name_and_sequential_repeat_order() -> None:
    with pytest.raises(ContractError):
        validate_statistical(dataclasses.replace(STAT, metric_gates={"": GATE}))
    with pytest.raises(ContractError, match="exceed"):
        validate_sequential(dataclasses.replace(SEQ, minimum_repeats=9, maximum_repeats=2))
    for field in ("look_every", "maximum_repeats", "minimum_repeats"):
        with pytest.raises(ContractError):
            validate_sequential(dataclasses.replace(SEQ, **{field: 0}))
