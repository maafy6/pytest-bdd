"""Test code generation command."""

import os
import sys
import textwrap

from pytest_bdd.scripts import main

PATH = os.path.dirname(__file__)


def test_generate(pytester, monkeypatch, capsys):
    """Test if the code is generated by a given feature."""

    features = pytester.mkdir("scripts")
    feature = features.joinpath("generate.feature")
    feature.write_text(
        textwrap.dedent(
            """\
            Feature: Code generation

                Scenario: Given and when using the same fixture should not evaluate it twice
                    Given I have an empty list
                    And 1 have a fixture (appends 1 to a list) in reuse syntax

                    When I use this fixture

                    Then my list should be [1]
            """
        ),
        "utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["", "generate", str(feature)])
    main()
    out, err = capsys.readouterr()
    assert out == textwrap.dedent(
        '''\
    """Code generation feature tests."""

    from pytest_bdd import (
        given,
        scenario,
        then,
        when,
    )


    @scenario('scripts/generate.feature', 'Given and when using the same fixture should not evaluate it twice')
    def test_given_and_when_using_the_same_fixture_should_not_evaluate_it_twice():
        """Given and when using the same fixture should not evaluate it twice."""


    @given('1 have a fixture (appends 1 to a list) in reuse syntax')
    def _():
        """1 have a fixture (appends 1 to a list) in reuse syntax."""
        raise NotImplementedError


    @given('I have an empty list')
    def _():
        """I have an empty list."""
        raise NotImplementedError


    @when('I use this fixture')
    def _():
        """I use this fixture."""
        raise NotImplementedError


    @then('my list should be [1]')
    def _():
        """my list should be [1]."""
        raise NotImplementedError

    '''
    )


def test_generate_with_quotes(pytester):
    """Test that code generation escapes quote characters properly."""
    pytester.makefile(
        ".feature",
        generate_with_quotes=textwrap.dedent(
            '''\
        Feature: Handling quotes in code generation

            Scenario: A step definition with quotes should be escaped as needed
                Given I have a fixture with 'single' quotes
                And I have a fixture with "double" quotes
                And I have a fixture with single-quote \'\'\'triple\'\'\' quotes
                And I have a fixture with double-quote """triple""" quotes

                When I generate the code

                Then The generated string should be written
        '''
        ),
    )

    result = pytester.run("pytest-bdd", "generate", "generate_with_quotes.feature")
    assert result.stdout.str() == textwrap.dedent(
        '''\
    """Handling quotes in code generation feature tests."""

    from pytest_bdd import (
        given,
        scenario,
        then,
        when,
    )


    @scenario('generate_with_quotes.feature', 'A step definition with quotes should be escaped as needed')
    def test_a_step_definition_with_quotes_should_be_escaped_as_needed():
        """A step definition with quotes should be escaped as needed."""


    @given('I have a fixture with "double" quotes')
    def _():
        """I have a fixture with "double" quotes."""
        raise NotImplementedError


    @given('I have a fixture with \\'single\\' quotes')
    def _():
        """I have a fixture with 'single' quotes."""
        raise NotImplementedError


    @given('I have a fixture with double-quote """triple""" quotes')
    def _():
        """I have a fixture with double-quote \\"\\"\\"triple\\"\\"\\" quotes."""
        raise NotImplementedError


    @given('I have a fixture with single-quote \\'\\'\\'triple\\'\\'\\' quotes')
    def _():
        """I have a fixture with single-quote \'\'\'triple\'\'\' quotes."""
        raise NotImplementedError


    @when('I generate the code')
    def _():
        """I generate the code."""
        raise NotImplementedError


    @then('The generated string should be written')
    def _():
        """The generated string should be written."""
        raise NotImplementedError
    '''
    )


def test_unicode_characters(pytester, monkeypatch):
    """Test generating code with unicode characters.

    Primary purpose is to ensure compatibility with Python2.
    """

    pytester.makefile(
        ".feature",
        unicode_characters=textwrap.dedent(
            """\
        Feature: Generating unicode characters

            Scenario: Calculating the circumference of a circle
                Given We have a circle
                When We want to know its circumference
                Then We calculate 2 * ℼ * 𝑟
        """
        ),
    )

    result = pytester.run("pytest-bdd", "generate", "unicode_characters.feature")
    expected_output = textwrap.dedent(
        '''\
            """Generating unicode characters feature tests."""

            from pytest_bdd import (
                given,
                scenario,
                then,
                when,
            )


            @scenario('unicode_characters.feature', 'Calculating the circumference of a circle')
            def test_calculating_the_circumference_of_a_circle():
                """Calculating the circumference of a circle."""


            @given('We have a circle')
            def _():
                """We have a circle."""
                raise NotImplementedError


            @when('We want to know its circumference')
            def _():
                """We want to know its circumference."""
                raise NotImplementedError


            @then('We calculate 2 * ℼ * 𝑟')
            def _():
                """We calculate 2 * ℼ * 𝑟."""
                raise NotImplementedError
            '''
    )
    assert result.stdout.str() == expected_output
