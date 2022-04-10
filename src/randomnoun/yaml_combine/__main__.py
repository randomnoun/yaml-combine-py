# yaml-combine main

import argparse
import logging
import sys

from randomnoun.yaml_combine.yaml_combiner import YamlCombiner


def main():
    """
    Entry point for the application script
    """

    parser = argparse.ArgumentParser(
        prog='python -m randomnoun.yaml_combine',
        description='A YAML pre-processor to combine one or more YAML files with $xref references.')
    parser.add_argument('files', metavar='filename', type=str, nargs='+', help='filename to combine')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()

    if args.verbose > 0:
        logging.basicConfig(level=logging.DEBUG)

    sc = YamlCombiner()
    sc.set_verbose(False)
    sc.set_relative_dir(".")
    sc.set_files(args.files)
    sc.combine(sys.stdout)


if __name__ == "__main__":
    main()
