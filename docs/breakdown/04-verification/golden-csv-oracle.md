---
id: INFO-009
type: info
title: Golden CSV oracle
summary: The upstream baseline CSV is compared by the reference evaluator
date: 2026-11-23
status: current
---

# Golden CSV oracle

`tests/data/scenario_baseline.csv` records upstream C++ and FMPy output and is the numerical oracle for the Python evaluator.

- **Fixture:** `tests/data/scenario.txt` defines five series; the CSV holds `time`, `Alt`, `Mach`, `heat_load`, `Wgt_On_Whl`, and `Aircraft_state`.
- **Comparison:** `test_matches_upstream_reference_results` evaluates every series at every row and requires an absolute and relative tolerance of `1e-12`.
- **Semantics:** the baseline proves the pre-first-sample zero, the in-segment interpolation, the hold after the last sample, and nearest-neighbour ties.
- **Single-sample difference:** the C++ evaluator reads past its array; the Python oracle holds the only value, and the baseline does not encode that case.
- **Update policy:** the suite compares the baseline; it does not regenerate it.
