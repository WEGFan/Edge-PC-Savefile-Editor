# -*- coding: utf-8 -*-
import pytest


def run_tests(coverage: bool):
    args = [
        'tests/',
        '-l', '-v', '-s'
    ]
    if coverage:
        args += [
            '--cov=.',
            '--cov-report=html', '--cov-report=term',
            '--cov-branch'
        ]
    pytest.main(args)


if __name__ == '__main__':
    run_tests(True)
