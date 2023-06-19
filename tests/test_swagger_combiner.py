# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import io
import logging
from difflib import Differ
from pprint import pprint
import pytest

from randomnoun.yaml_combine.yaml_combiner import YamlCombiner

import os

DATA_DIR_VALID_CASES = "tests/data/valid_cases"
DATA_DIR_ERROR_CASES = "tests/data/error_cases"


def nicer_assert_equal(result, expected_output):
    """An assertEqual method which produces a nicer diff output"""

    if result == expected_output:
        return  # OK

    print("\n=============\n")
    print("result is\n" + result)

    print("\n=============\n")
    print("expected is\n" + expected_output)

    # nicer diff output
    d = Differ()
    result = list(
        d.compare(
            result.splitlines(keepends=True),
            expected_output.splitlines(keepends=True),
        )
    )
    pprint(result)
    assert result == expected_output


@pytest.mark.parametrize(
    "test_case_dir",
    sorted(os.listdir(f"{os.getcwd()}/{DATA_DIR_VALID_CASES}"), key=lambda s: int(s.split("_")[0][1:]))
)
def test_yaml_combiner_valid_cases(test_case_dir):
    """
    This parametrized test runs a test for each test case within the DATA_DIR_VALID_CASES directory. Each test takes the
    "input.yaml" file, pipes it through the YamlCombiner().combine() method, and compares its output to the
    "expected_output.yaml" file.
    """
    logging.basicConfig(level=logging.DEBUG)

    sc = YamlCombiner()
    sc.set_verbose(False)
    sc.set_relative_dir(f"{DATA_DIR_VALID_CASES}/{test_case_dir}/")
    sc.set_files(["input.yaml"])

    with io.StringIO() as output:
        sc.combine(output)
        result = output.getvalue()

    filename = f"{DATA_DIR_VALID_CASES}/{test_case_dir}/expected-output.yaml"
    with open(filename, "r", encoding="utf-8") as f:
        expected_output = f.read()

    nicer_assert_equal(result, expected_output)


@pytest.mark.parametrize(
    "test_case_dir, message_substring",
    [
        ("cycle_detection", "cycle detected"),
        ("unresolvable_object", "Inconsistent $xref types within object")
    ]
)
def test_yaml_combiner_error_cases(test_case_dir, message_substring):
    """
    This parametrized test runs a test for each test case within the DATA_DIR_ERROR_CASES directory. Each test takes the
    "input.yaml" file, pipes it through the YamlCombiner().combine() method, assert that a ValueError is raised, and
    asserts that the ValueError message contains some substring.
    """
    logging.basicConfig(level=logging.DEBUG)

    sc = YamlCombiner()
    sc.set_verbose(False)
    sc.set_relative_dir(f"{DATA_DIR_ERROR_CASES}/{test_case_dir}/")
    sc.set_files(["input.yaml"])

    with io.StringIO() as output:
        with pytest.raises(ValueError) as e_info:
            sc.combine(output)

    assert message_substring in e_info.value.args[0]
