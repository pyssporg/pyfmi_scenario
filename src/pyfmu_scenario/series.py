"""Pure-Python reference evaluation of scenario series.

This module is the oracle for the later generated runtime. It repeats the
upstream C++ semantics:

- a time before the first sample evaluates to ``0.0`` for every mode;
- a time on a sample evaluates to that sample's value;
- between samples, ``L`` interpolates linearly, ``ZOH`` holds the left value,
  and ``NN`` chooses the nearer endpoint (a tie chooses the left value);
- a time after the last sample holds the last value for every mode, so linear
  series are not extrapolated.

The one intentional difference is a single-sample series: the C++ evaluator
reads past its array, while this evaluator holds the only value.
"""

from __future__ import annotations

from bisect import bisect_right

from .grammar import Interpolation, Sample, Scenario, Series


def evaluate_samples(
    samples: tuple[Sample, ...],
    interpolation: Interpolation,
    time: float,
) -> float:
    """Evaluate one sample sequence at ``time``."""
    if time < samples[0].time:
        return 0.0
    if time >= samples[-1].time:
        return samples[-1].value

    times = [sample.time for sample in samples]
    index = bisect_right(times, time) - 1
    left = samples[index]
    right = samples[index + 1]

    if time == left.time:
        return left.value
    if interpolation is Interpolation.ZERO_ORDER_HOLD:
        return left.value
    if interpolation is Interpolation.NEAREST_NEIGHBOUR:
        if abs(time - left.time) <= abs(time - right.time):
            return left.value
        return right.value
    if interpolation is Interpolation.LINEAR:
        span = right.time - left.time
        fraction = (time - left.time) / span
        return left.value + fraction * (right.value - left.value)

    raise ValueError(f"unsupported interpolation mode: {interpolation!r}")


def evaluate_series(series: Series, time: float) -> float:
    """Evaluate one series at ``time``."""
    return evaluate_samples(series.samples, series.interpolation, time)


def evaluate_scenario(scenario: Scenario, time: float) -> dict[str, float]:
    """Evaluate every series at ``time``, keyed by name in declaration order."""
    return {
        series.name: evaluate_series(series, time) for series in scenario.series
    }


def evaluate_series_at_times(
    series: Series, times: tuple[float, ...]
) -> tuple[float, ...]:
    """Evaluate one series at several times."""
    return tuple(evaluate_series(series, time) for time in times)


__all__ = [
    "evaluate_samples",
    "evaluate_scenario",
    "evaluate_series",
    "evaluate_series_at_times",
]
