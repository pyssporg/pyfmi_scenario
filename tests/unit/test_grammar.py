from pathlib import Path

import pytest

from pyfmu_scenario.grammar import (
    BadNumberError,
    DuplicateSeriesNameError,
    EmptyScenarioError,
    Interpolation,
    MissingFieldError,
    NonMonotonicTimeError,
    UnknownInterpolationError,
    UnsupportedInterpolationError,
    parse_scenario,
    serialize_scenario,
)

DATA = Path(__file__).resolve().parents[1] / "data"
FIXTURE_TEXT = (DATA / "scenario.txt").read_text(encoding="utf-8").strip()
FIXTURE_NAMES = ("Alt", "Mach", "heat_load", "Wgt_On_Whl", "Aircraft_state")


def test_parse_fixture_series():
    scenario = parse_scenario(FIXTURE_TEXT)

    assert scenario.names == FIXTURE_NAMES
    assert [series.interpolation for series in scenario.series] == [
        Interpolation.LINEAR,
        Interpolation.LINEAR,
        Interpolation.ZERO_ORDER_HOLD,
        Interpolation.ZERO_ORDER_HOLD,
        Interpolation.ZERO_ORDER_HOLD,
    ]
    assert scenario.by_name("Alt").samples[0].time == 0.0
    assert scenario.by_name("Alt").samples[-1].value == 10000.0
    assert scenario.by_name("heat_load").samples[-1].time == 150.0


def test_serialize_round_trip_is_canonical():
    scenario = parse_scenario(FIXTURE_TEXT)

    assert serialize_scenario(scenario) == FIXTURE_TEXT
    assert parse_scenario(serialize_scenario(scenario)) == scenario


def test_spaces_around_fields_are_trimmed():
    scenario = parse_scenario(" var1 ; L ; 1, 0 ; 3, 0.5 ")

    assert scenario.names == ("var1",)
    series = scenario.series[0]
    assert series.interpolation is Interpolation.LINEAR
    assert [(sample.time, sample.value) for sample in series.samples] == [
        (1.0, 0.0),
        (3.0, 0.5),
    ]


def test_trailing_newline_is_accepted():
    scenario = parse_scenario(FIXTURE_TEXT + "\n")

    assert scenario.names == FIXTURE_NAMES


@pytest.mark.parametrize("text", ["", "   ", "\n\t\n"])
def test_empty_input_is_rejected(text):
    with pytest.raises(EmptyScenarioError):
        parse_scenario(text)


@pytest.mark.parametrize(
    "text",
    [
        "Alt;L",
        "Alt;L;",
        ";L;0,0",
        "Alt;;0,0",
        "Alt;L;0",
        "Alt;L;0,0,1",
        "Alt;L;0,0\n\nMach;L;0,1",
    ],
)
def test_missing_fields_are_rejected(text):
    with pytest.raises(MissingFieldError):
        parse_scenario(text)


def test_duplicate_series_names_are_rejected():
    with pytest.raises(DuplicateSeriesNameError):
        parse_scenario("Alt;L;0,0\nAlt;ZOH;0,1")


@pytest.mark.parametrize(
    "text",
    [
        "Alt;L;1,0;0,1",
        "Alt;L;0,0;0,1",
        "Alt;L;0,0;2,1;1,2",
    ],
)
def test_non_monotonic_times_are_rejected(text):
    with pytest.raises(NonMonotonicTimeError):
        parse_scenario(text)


@pytest.mark.parametrize(
    "text",
    [
        "Alt;L;x,0",
        "Alt;L;0,y",
        "Alt;L;1e,0",
        "Alt;L;nan,0",
        "Alt;L;0,inf",
    ],
)
def test_bad_numbers_are_rejected(text):
    with pytest.raises(BadNumberError):
        parse_scenario(text)


@pytest.mark.parametrize("text", ["Alt;Q;0,0", "Alt;l;0,0"])
def test_unknown_interpolation_is_rejected(text):
    with pytest.raises(UnknownInterpolationError):
        parse_scenario(text)


def test_cubic_is_declared_but_unsupported():
    with pytest.raises(UnsupportedInterpolationError, match="not implemented"):
        parse_scenario("Alt;C;0,0;1,1")
