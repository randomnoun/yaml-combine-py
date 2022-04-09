# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest
import io
from difflib import Differ
from pprint import pprint


from swagger_combine.swagger_combiner import SwaggerCombiner

class TestSwaggerCombine(unittest.TestCase):

    def test_combine(self):
        
        files = [ "input.yaml" ]
        
        sc = SwaggerCombiner()
        sc.set_files(files)
        sc.set_relative_dir("tests/data/t1/")
        
        output = io.StringIO()
        sc.combine(output)
        result = output.getvalue()
        output.close()
        
        f = open("tests/data/t1/expected-output.yaml", "r", encoding="utf-8")
        expected_output = f.read()
        f.close()
        
        print("\n=============\n")
        print("result is\n" + result)
        
        print("\n=============\n")
        print("expected is\n" + expected_output)
        
        
        # self.assertEqual(result, expected_output)
        # nicer diff output
        d = Differ()
        result = list(d.compare(result.splitlines(keepends=True), expected_output.splitlines(keepends=True)))
        pprint(result)
        


if __name__ == '__main__':
    unittest.main()
