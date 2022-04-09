# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
import io
import sys
import logging
from difflib import Differ
from pprint import pprint

from swagger_combine.swagger_combiner import SwaggerCombiner


class TestSwaggerCombine(unittest.TestCase):
    def test_combine(self):
        logging.basicConfig(level=logging.DEBUG)
        files = ["input.yaml"]

        sc = SwaggerCombiner()
        sc.set_files(files)
        sc.set_relative_dir("tests/data/t1/")
        sc.set_verbose(False)

        output = io.StringIO()
        sc.combine(output)
        result = output.getvalue()
        output.close()

        is_py37 = sys.version_info >= (3, 7, 0)
        filename = "tests/data/t1/expected-output.yaml" if is_py37 else "tests/data/t1/expected-output-sorted.yaml" 
        f = open(filename, "r", encoding="utf-8")
        expected_output = f.read()
        f.close()
        self.nicer_assertEqual(result, expected_output)

    def nicer_assertEqual(self, result, expected_output):
        """An assertEqual method which produces a nicer diff output"""

        if (result==expected_output):
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
        self.assertEqual(result, expected_output)


if __name__ == "__main__":
    unittest.main()
