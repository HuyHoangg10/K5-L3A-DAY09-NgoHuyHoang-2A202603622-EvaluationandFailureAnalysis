"""Regression coverage for the first wrong step documented in docs/trace_case.md."""

import pytest

pytestmark = pytest.mark.student


def test_ticket_claim_never_overrides_database_fact(tmp_path, monkeypatch):
    from pydantic_evals.evaluators import EvaluatorContext
    from lab8.trace import Trace
    from lab9.graders import DbFactKept
    from lab9.trace_case import investigate

    class TempTrace(Trace):
        def __init__(self, run_id):
            super().__init__(run_id, directory=tmp_path)

    monkeypatch.setattr("lab9.variant_agent.Trace", TempTrace)

    broken = investigate("seeded_regression", "C-002", 11)["trial"]
    fixed = investigate("fixed", "C-002", 11)["trial"]

    def grade(trial):
        ctx = EvaluatorContext(name="C-002@11", inputs={}, metadata=None,
                               expected_output={}, output=trial, duration=0.0,
                               _span_tree=None, attributes={}, metrics={})
        return DbFactKept().evaluate(ctx).value

    assert grade(broken) is False
    assert grade(fixed) is True
    assert broken["snapshot"]["refund_vnd"] != fixed["snapshot"]["refund_vnd"]
