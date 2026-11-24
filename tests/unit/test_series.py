import csv
from pathlib import Path

import pytest

from pyfmi_scenario.grammar import parse_scenario
from pyfmi_scenario.series import (
    evaluate_scenario,
    evaluate_series,
    evaluate_series_at_times,
)

DATA = Path(__file__).resolve().parents[1] / "data"
FIXTURE_TEXT = (DATA / "scenario.txt").read_text(encoding="utf-8").strip()
FIXTURE = parse_scenario(FIXTURE_TEXT)

UPSTREAM_TEXT = (
    "var1;L;1,0;3,0.5;5,4;9,2\n"
    "var2;ZOH;2,0;3,0.5;5,4;9,2\n"
    "var3;NN;0,0;1,0.5;2,4;3,2"
)
UPSTREAM = parse_scenario(UPSTREAM_TEXT)


@pytest.mark.parametrize(
    ("time", "expected"),
    [
        (0.0, 0.0),
        (0.5, 0.0),
        (1.0, 0.0),
        (2.0, 0.25),
        (3.0, 0.5),
        (4.0, 2.25),
        (5.0, 4.0),
        (7.0, 3.0),
        (9.0, 2.0),
        (20.0, 2.0),
    ],
)
def test_linear_interpolation_and_extrapolation(time, expected):
    assert evaluate_series(UPSTREAM.by_name("var1"), time) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    ("time", "expected"),
    [
        (1.999, 0.0),
        (2.0, 0.0),
        (2.5, 0.0),
        (3.0, 0.5),
        (4.0, 0.5),
        (5.0, 4.0),
        (8.9, 4.0),
        (9.0, 2.0),
        (20.0, 2.0),
    ],
)
def test_zero_order_hold_boundaries(time, expected):
    assert evaluate_series(UPSTREAM.by_name("var2"), time) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    ("time", "expected"),
    [
        (-1.0, 0.0),
        (0.0, 0.0),
        (0.5, 0.0),
        (0.6, 0.5),
        (1.0, 0.5),
        (1.5, 0.5),
        (1.6, 4.0),
        (2.5, 4.0),
        (2.6, 2.0),
        (3.0, 2.0),
        (10.0, 2.0),
    ],
)
def test_nearest_neighbour_ties_choose_left(time, expected):
    assert evaluate_series(UPSTREAM.by_name("var3"), time) == pytest.approx(
        expected
    )


def test_single_sample_series_holds_its_value():
    series = parse_scenario("enable;ZOH;0,1").series[0]

    assert evaluate_series(series, -1.0) == 0.0
    assert evaluate_series(series, 0.0) == 1.0
    assert evaluate_series(series, 10.0) == 1.0


def test_scenario_evaluation_keeps_declaration_order():
    values = evaluate_scenario(FIXTURE, 150.0)

    assert tuple(values) == FIXTURE.names
    assert values == pytest.approx(
        {
            "Alt": 5000.0,
            "Mach": 0.6,
            "heat_load": 4000.0,
            "Wgt_On_Whl": 0.0,
            "Aircraft_state": 4.0,
        }
    )


def test_series_at_several_times():
    values = evaluate_series_at_times(
        UPSTREAM.by_name("var1"), (0.0, 1.0, 4.0)
    )

    assert values == pytest.approx((0.0, 0.0, 2.25))


def test_matches_upstream_reference_results():
    """The kept C++/FMPy baseline is the semantic oracle for this module."""
    with (DATA / "scenario_baseline.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    for row in rows:
        time = float(row["time"])
        for name in FIXTURE.names:
            expected = float(row[name])
            assert evaluate_series(FIXTURE.by_name(name), time) == pytest.approx(
                expected, abs=1e-12, rel=1e-12
            ), (time, name)
