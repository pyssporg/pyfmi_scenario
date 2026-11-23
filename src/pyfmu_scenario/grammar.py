"""Parse and serialize the scenario grammar carried by ``scenario_input``.

The grammar is one series per line::

    name;interpolation;time_0,value_0;time_1,value_1;...

Interpolation is ``L`` (linear), ``ZOH`` (zero-order hold), or ``NN``
(nearest neighbour). ``C`` is declared by the upstream format but not
implemented; parsing it raises :class:`UnsupportedInterpolationError` instead of
silently choosing another mode.

Parsing is deliberately stricter than the prototype C++ parser: fields,
numbers, series names, and time ordering are checked, so a malformed scenario
fails with a typed error before it reaches a generated runtime.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class ScenarioError(ValueError):
    """Base class for every scenario grammar error."""


class EmptyScenarioError(ScenarioError):
    """The scenario text has no series."""


class MissingFieldError(ScenarioError):
    """A line or sample point is missing a required field."""


class DuplicateSeriesNameError(ScenarioError):
    """Two series declare the same output name."""


class NonMonotonicTimeError(ScenarioError):
    """Sample times are not strictly increasing."""


class BadNumberError(ScenarioError):
    """A sample time or value is not a finite decimal number."""


class UnknownInterpolationError(ScenarioError):
    """The interpolation token is not part of the scenario grammar."""


class UnsupportedInterpolationError(ScenarioError):
    """The interpolation mode is declared by the grammar but not implemented."""


class Interpolation(str, Enum):
    """Interpolation mode of one scenario series."""

    LINEAR = "L"
    ZERO_ORDER_HOLD = "ZOH"
    NEAREST_NEIGHBOUR = "NN"
    CUBIC = "C"


@dataclass(frozen=True)
class Sample:
    """One ``time,value`` coordinate pair."""

    time: float
    value: float


@dataclass(frozen=True)
class Series:
    """One named output series with its interpolation mode and samples."""

    name: str
    interpolation: Interpolation
    samples: tuple[Sample, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "samples", tuple(self.samples))
        if not self.name or not self.name.strip():
            raise MissingFieldError("series name must not be empty")
        if self.interpolation is Interpolation.CUBIC:
            raise UnsupportedInterpolationError(
                "cubic interpolation ('C') is declared by the scenario grammar "
                "but is not implemented"
            )
        if not self.samples:
            raise MissingFieldError(
                f"series {self.name!r} has no time,value samples"
            )
        for sample in self.samples:
            if not math.isfinite(sample.time) or not math.isfinite(sample.value):
                raise BadNumberError(
                    f"series {self.name!r} sample {sample.time!r},"
                    f"{sample.value!r} must be finite"
                )
        for previous, current in zip(self.samples, self.samples[1:]):
            if current.time <= previous.time:
                raise NonMonotonicTimeError(
                    f"series {self.name!r} times must be strictly increasing: "
                    f"{previous.time!r} followed by {current.time!r}"
                )


@dataclass(frozen=True)
class Scenario:
    """An ordered collection of uniquely named series."""

    series: tuple[Series, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "series", tuple(self.series))
        if not self.series:
            raise EmptyScenarioError("scenario must contain at least one series")
        seen: set[str] = set()
        for item in self.series:
            if item.name in seen:
                raise DuplicateSeriesNameError(
                    f"duplicate series name {item.name!r}"
                )
            seen.add(item.name)

    @property
    def names(self) -> tuple[str, ...]:
        """Series names in declaration order."""
        return tuple(item.name for item in self.series)

    def by_name(self, name: str) -> Series:
        """Return the series named ``name`` or raise :class:`KeyError`."""
        for item in self.series:
            if item.name == name:
                return item
        raise KeyError(name)


def _parse_interpolation(token: str, line_number: int) -> Interpolation:
    if token == Interpolation.CUBIC.value:
        raise UnsupportedInterpolationError(
            f"line {line_number}: cubic interpolation ('C') is declared by the "
            "scenario grammar but is not implemented"
        )
    try:
        return Interpolation(token)
    except ValueError as exc:
        raise UnknownInterpolationError(
            f"line {line_number}: unknown interpolation {token!r}; "
            "expected 'L', 'ZOH', or 'NN'"
        ) from exc


def _parse_number(token: str, line_number: int, what: str) -> float:
    try:
        value = float(token)
    except ValueError as exc:
        raise BadNumberError(
            f"line {line_number}: {what} {token!r} is not a number"
        ) from exc
    if not math.isfinite(value):
        raise BadNumberError(
            f"line {line_number}: {what} {token!r} must be finite"
        )
    return value


def _parse_series(line: str, line_number: int) -> Series:
    fields = [field.strip() for field in line.split(";")]
    if len(fields) < 3:
        raise MissingFieldError(
            f"line {line_number}: expected "
            "'name;interpolation;time,value[;time,value...]'"
        )

    name = fields[0]
    if not name:
        raise MissingFieldError(f"line {line_number}: series name is empty")

    if not fields[1]:
        raise MissingFieldError(f"line {line_number}: interpolation is empty")
    interpolation = _parse_interpolation(fields[1], line_number)

    samples: list[Sample] = []
    for field in fields[2:]:
        coordinates = field.split(",")
        if (
            len(coordinates) != 2
            or not coordinates[0].strip()
            or not coordinates[1].strip()
        ):
            raise MissingFieldError(
                f"line {line_number}: sample {field!r} is not 'time,value'"
            )
        samples.append(
            Sample(
                time=_parse_number(coordinates[0], line_number, "time"),
                value=_parse_number(coordinates[1], line_number, "value"),
            )
        )

    return Series(name=name, interpolation=interpolation, samples=tuple(samples))


def parse_scenario(text: str) -> Scenario:
    """Parse scenario text into typed series, or raise :class:`ScenarioError`."""
    if not isinstance(text, str):
        raise TypeError(f"scenario text must be str, got {type(text).__name__}")

    body = text.strip()
    if not body:
        raise EmptyScenarioError("scenario text is empty")

    series: list[Series] = []
    for line_number, line in enumerate(body.splitlines(), start=1):
        if not line.strip():
            raise MissingFieldError(f"line {line_number}: empty series")
        series.append(_parse_series(line, line_number))
    return Scenario(series=tuple(series))


def serialize_series(series: Series) -> str:
    """Render one series in canonical ``name;interp;t,v;...`` form."""
    samples = ";".join(
        f"{sample.time},{sample.value}" for sample in series.samples
    )
    return f"{series.name};{series.interpolation.value};{samples}"


def serialize_scenario(scenario: Scenario) -> str:
    """Render a scenario as newline-separated canonical series lines."""
    return "\n".join(serialize_series(item) for item in scenario.series)


__all__ = [
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
    "parse_scenario",
    "serialize_scenario",
    "serialize_series",
]
