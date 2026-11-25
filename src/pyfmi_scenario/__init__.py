"""Scenario grammar, reference evaluator, and FMI 2.0 interface model."""

__version__ = "0.2.0"

from .grammar import (
    BadNumberError,
    DuplicateSeriesNameError,
    EmptyScenarioError,
    Interpolation,
    MissingFieldError,
    NonMonotonicTimeError,
    Sample,
    Scenario,
    ScenarioError,
    Series,
    UnknownInterpolationError,
    UnsupportedInterpolationError,
    parse_scenario,
    serialize_scenario,
    serialize_series,
)
from .model import (
    AUTHOR,
    DEFAULT_EXPERIMENT,
    DEFAULT_GUID,
    GENERATION_TOOL,
    MODEL_IDENTIFIER,
    MODEL_NAME,
    PARAMETER_NAME,
    VERSION,
    build_component,
    build_reduction,
    build_variables,
)
from .model_description import build_document, build_model_description
from .parameter_set import write_parameter_set
from .series import (
    evaluate_samples,
    evaluate_scenario,
    evaluate_series,
    evaluate_series_at_times,
)

__all__ = [
    "AUTHOR",
    "DEFAULT_EXPERIMENT",
    "DEFAULT_GUID",
    "GENERATION_TOOL",
    "MODEL_IDENTIFIER",
    "MODEL_NAME",
    "PARAMETER_NAME",
    "VERSION",
    "BadNumberError",
    "DuplicateSeriesNameError",
    "EmptyScenarioError",
    "Interpolation",
    "MissingFieldError",
    "NonMonotonicTimeError",
    "Sample",
    "Scenario",
    "ScenarioError",
    "Series",
    "UnknownInterpolationError",
    "UnsupportedInterpolationError",
    "__version__",
    "build_component",
    "build_document",
    "build_model_description",
    "build_reduction",
    "build_variables",
    "evaluate_samples",
    "evaluate_scenario",
    "evaluate_series",
    "evaluate_series_at_times",
    "parse_scenario",
    "serialize_scenario",
    "serialize_series",
    "write_parameter_set",
]
