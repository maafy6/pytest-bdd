"""Test cucumber json output."""
from __future__ import annotations

import json
import os.path
import textwrap
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _pytest.pytester import Pytester, RunResult


def runandparse(pytester: Pytester, *args: Any) -> tuple[RunResult, list[dict[str, Any]]]:
    """Run tests in testdir and parse json output."""
    resultpath = pytester.path.joinpath("cucumber.json")
    result = pytester.runpytest(f"--cucumberjson={resultpath}", "-s", *args)
    with resultpath.open() as f:
        jsonobject = json.load(f)
    return result, jsonobject


class OfType:
    """Helper object to help compare object type to initialization type"""

    def __init__(self, type: type = None) -> None:
        self.type = type

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.type) if self.type else True


def test_step_trace(pytester):
    """Test step trace."""
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
    [pytest]
    markers =
        scenario-passing-tag
        scenario-failing-tag
        scenario-outline-passing-tag
        feature-tag
    """
        ),
    )
    pytester.makefile(
        ".feature",
        test=textwrap.dedent(
            """
    @feature-tag
    Feature: One passing scenario, one failing scenario

        @scenario-passing-tag
        Scenario: Passing
            Given a passing step
            And some other passing step

        @scenario-failing-tag
        Scenario: Failing
            Given a passing step
            And a failing step

        @scenario-outline-passing-tag
        Scenario Outline: Passing outline
            Given type <type> and value <value>

            Examples: example1
            | type    | value  |
            | str     | hello  |
            | int     | 42     |
            | float   | 1.0    |
    """
        ),
    )
    pytester.makepyfile(
        textwrap.dedent(
            """
        import pytest
        from pytest_bdd import given, when, scenario, parsers

        @given('a passing step')
        def _():
            return 'pass'

        @given('some other passing step')
        def _():
            return 'pass'

        @given('a failing step')
        def _():
            raise Exception('Error')

        @given(parsers.parse('type {type} and value {value}'))
        def _():
            return 'pass'

        @scenario('test.feature', 'Passing')
        def test_passing():
            pass

        @scenario('test.feature', 'Failing')
        def test_failing():
            pass

        @scenario('test.feature', 'Passing outline')
        def test_passing_outline():
            pass
    """
        )
    )
    result, jsonobject = runandparse(pytester)
    result.assert_outcomes(passed=4, failed=1)

    assert result.ret
    expected = [
        {
            "description": "",
            "elements": [
                {
                    "description": "",
                    "id": "test_passing",
                    "keyword": "Scenario",
                    "line": 5,
                    "name": "Passing",
                    "steps": [
                        {
                            "keyword": "Given",
                            "line": 6,
                            "match": {"location": ""},
                            "name": "a passing step",
                            "result": {"status": "passed", "duration": OfType(int)},
                        },
                        {
                            "keyword": "And",
                            "line": 7,
                            "match": {"location": ""},
                            "name": "some other passing step",
                            "result": {"status": "passed", "duration": OfType(int)},
                        },
                    ],
                    "tags": [{"name": "scenario-passing-tag", "line": 4}],
                    "type": "scenario",
                },
                {
                    "description": "",
                    "id": "test_failing",
                    "keyword": "Scenario",
                    "line": 10,
                    "name": "Failing",
                    "steps": [
                        {
                            "keyword": "Given",
                            "line": 11,
                            "match": {"location": ""},
                            "name": "a passing step",
                            "result": {"status": "passed", "duration": OfType(int)},
                        },
                        {
                            "keyword": "And",
                            "line": 12,
                            "match": {"location": ""},
                            "name": "a failing step",
                            "result": {"error_message": OfType(str), "status": "failed", "duration": OfType(int)},
                        },
                    ],
                    "tags": [{"name": "scenario-failing-tag", "line": 9}],
                    "type": "scenario",
                },
                {
                    "description": "",
                    "keyword": "Scenario",
                    "tags": [{"line": 14, "name": "scenario-outline-passing-tag"}],
                    "steps": [
                        {
                            "line": 16,
                            "match": {"location": ""},
                            "result": {"status": "passed", "duration": OfType(int)},
                            "keyword": "Given",
                            "name": "type str and value hello",
                        }
                    ],
                    "line": 15,
                    "type": "scenario",
                    "id": "test_passing_outline[str-hello]",
                    "name": "Passing outline",
                },
                {
                    "description": "",
                    "keyword": "Scenario",
                    "tags": [{"line": 14, "name": "scenario-outline-passing-tag"}],
                    "steps": [
                        {
                            "line": 16,
                            "match": {"location": ""},
                            "result": {"status": "passed", "duration": OfType(int)},
                            "keyword": "Given",
                            "name": "type int and value 42",
                        }
                    ],
                    "line": 15,
                    "type": "scenario",
                    "id": "test_passing_outline[int-42]",
                    "name": "Passing outline",
                },
                {
                    "description": "",
                    "keyword": "Scenario",
                    "tags": [{"line": 14, "name": "scenario-outline-passing-tag"}],
                    "steps": [
                        {
                            "line": 16,
                            "match": {"location": ""},
                            "result": {"status": "passed", "duration": OfType(int)},
                            "keyword": "Given",
                            "name": "type float and value 1.0",
                        }
                    ],
                    "line": 15,
                    "type": "scenario",
                    "id": "test_passing_outline[float-1.0]",
                    "name": "Passing outline",
                },
            ],
            "id": os.path.join("test_step_trace0", "test.feature"),
            "keyword": "Feature",
            "line": 2,
            "name": "One passing scenario, one failing scenario",
            "tags": [{"name": "feature-tag", "line": 1}],
            "uri": os.path.join(pytester.path.name, "test.feature"),
        }
    ]

    assert jsonobject == expected
