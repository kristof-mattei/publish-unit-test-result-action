import contextlib
import locale
import unittest
from typing import Any

from publish_unit_test_results import as_delta, as_stat_number, as_stat_duration, \
    get_formatted_digits, get_short_summary_md, get_long_summary_md, get_stats, \
    get_stats_with_delta, parse_junit_xml_files


@contextlib.contextmanager
def temp_locale(encoding) -> Any:
    old_locale = locale.getlocale()
    locale.setlocale(locale.LC_ALL, encoding)
    try:
        res = yield
    finally:
        locale.setlocale(locale.LC_ALL, old_locale)
    return res


def n(number, delta=None):
    if delta is None:
        return dict(number=number)
    return dict(number=number, delta=delta)


def d(duration, delta=None):
    if delta is None:
        return dict(duration=duration)
    return dict(duration=duration, delta=delta)


class Test(unittest.TestCase):
    def test_get_formatted_digits(self):
        self.assertEqual(get_formatted_digits(None), (3, 0))
        self.assertEqual(get_formatted_digits(None, 1), (3, 0))
        self.assertEqual(get_formatted_digits(None, 123), (3, 0))
        self.assertEqual(get_formatted_digits(None, 1234), (4, 0))
        self.assertEqual(get_formatted_digits(0), (1, 0))
        self.assertEqual(get_formatted_digits(1, 2, 3), (1, 0))
        self.assertEqual(get_formatted_digits(10), (2, 0))
        self.assertEqual(get_formatted_digits(100), (3, 0))
        self.assertEqual(get_formatted_digits(1234, 123, 0), (4, 0))
        with temp_locale('en_US.utf8'):
            self.assertEqual(get_formatted_digits(1234, 123, 0), (5, 0))
        with temp_locale('de_DE.utf8'):
            self.assertEqual(get_formatted_digits(1234, 123, 0), (5, 0))

        self.assertEqual(get_formatted_digits(dict()), (3, 3))
        self.assertEqual(get_formatted_digits(dict(number=1)), (1, 3))
        self.assertEqual(get_formatted_digits(dict(number=12)), (2, 3))
        self.assertEqual(get_formatted_digits(dict(number=123)), (3, 3))
        self.assertEqual(get_formatted_digits(dict(number=1234)), (4, 3))
        with temp_locale('en_US.utf8'):
            self.assertEqual(get_formatted_digits(dict(number=1234)), (5, 3))
        with temp_locale('de_DE.utf8'):
            self.assertEqual(get_formatted_digits(dict(number=1234)), (5, 3))

        self.assertEqual(get_formatted_digits(dict(delta=1)), (3, 1))
        self.assertEqual(get_formatted_digits(dict(number=1, delta=1)), (1, 1))
        self.assertEqual(get_formatted_digits(dict(number=1, delta=12)), (1, 2))
        self.assertEqual(get_formatted_digits(dict(number=1, delta=123)), (1, 3))
        self.assertEqual(get_formatted_digits(dict(number=1, delta=1234)), (1, 4))
        with temp_locale('en_US.utf8'):
            self.assertEqual(get_formatted_digits(dict(number=1, delta=1234)), (1, 5))
        with temp_locale('de_DE.utf8'):
            self.assertEqual(get_formatted_digits(dict(number=1, delta=1234)), (1, 5))

    def test_get_stats(self):
        self.assertEqual(get_stats(dict()), dict(
            files=None,
            suites=None,
            duration=None,

            tests=None,
            tests_succ=None,
            tests_skip=None,
            tests_fail=None,
            tests_error=None,

            runs=None,
            runs_succ=None,
            runs_skip=None,
            runs_fail=None,
            runs_error=None
        ))

        self.assertEqual(get_stats(dict(
            suite_tests=20,
            suite_skipped=5,
            suite_failures=None,

            tests=40,
            tests_skipped=10,
            tests_failures=None
        )), dict(
            files=None,
            suites=None,
            duration=None,

            tests=40,
            tests_succ=30,
            tests_skip=10,
            tests_fail=None,
            tests_error=None,

            runs=20,
            runs_succ=15,
            runs_skip=5,
            runs_fail=None,
            runs_error=None
        ))

        self.assertEqual(get_stats(dict(
            files=1,
            suites=2,
            suite_time=3,

            suite_tests=20,
            suite_skipped=5,
            suite_failures=6,
            suite_errors=7,

            tests=30,
            tests_skipped=8,
            tests_failures=9,
            tests_errors=10
        )), dict(
            files=1,
            suites=2,
            duration=3,

            tests=30,
            tests_succ=3,
            tests_skip=8,
            tests_fail=9,
            tests_error=10,

            runs=20,
            runs_succ=2,
            runs_skip=5,
            runs_fail=6,
            runs_error=7
        ))

    def test_get_stats_with_delta(self):
        self.assertEqual(get_stats_with_delta(dict(), dict(), 'type'), dict(
            reference_commit=None,
            reference_type='type'
        ))
        self.assertEqual(get_stats_with_delta(dict(
            files=1,
            suites=2,
            duration=3,

            tests=20,
            tests_succ=2,
            tests_skip=5,
            tests_fail=6,
            tests_error=7,

            runs=40,
            runs_succ=12,
            runs_skip=8,
            runs_fail=9,
            runs_error=10,

            commit='commit'
        ), dict(), 'missing'), dict(
            files=dict(number=1),
            suites=dict(number=2),
            duration=dict(duration=3),

            tests=dict(number=20),
            tests_succ=dict(number=2),
            tests_skip=dict(number=5),
            tests_fail=dict(number=6),
            tests_error=dict(number=7),

            runs=dict(number=40),
            runs_succ=dict(number=12),
            runs_skip=dict(number=8),
            runs_fail=dict(number=9),
            runs_error=dict(number=10),

            reference_commit=None,
            reference_type='missing'
        ))

        self.assertEqual(get_stats_with_delta(dict(
            files=1,
            suites=2,
            duration=3,

            tests=20,
            tests_succ=2,
            tests_skip=5,
            tests_fail=6,
            tests_error=7,

            runs=40,
            runs_succ=12,
            runs_skip=8,
            runs_fail=9,
            runs_error=10,

            commit='commit'
        ), dict(
            files=3,
            suites=5,
            duration=7,

            tests=41,
            tests_succ=5,
            tests_skip=11,
            tests_fail=13,
            tests_error=15,

            runs=81,
            runs_succ=25,
            runs_skip=17,
            runs_fail=19,
            runs_error=21,

            commit='ref'
        ), 'type'), dict(
            files=n(1, 2),
            suites=n(2, 3),
            duration=d(3, 4),

            tests=n(20, 21),
            tests_succ=n(2, 3),
            tests_skip=n(5, 6),
            tests_fail=n(6, 7),
            tests_error=n(7, 8),

            runs=n(40, 41),
            runs_succ=n(12, 13),
            runs_skip=n(8, 9),
            runs_fail=n(9, 10),
            runs_error=n(10, 11),

            reference_commit='ref',
            reference_type='type'
        ))

    def test_as_delta(self):
        self.assertEqual(as_delta(0, 1), '±0')
        self.assertEqual(as_delta(+1, 1), '+1')
        self.assertEqual(as_delta(-2, 1), '-2')

        self.assertEqual(as_delta(0, 2), '± 0')
        self.assertEqual(as_delta(+1, 2), '+ 1')
        self.assertEqual(as_delta(-2, 2), '- 2')

        self.assertEqual(as_delta(1, 5), '+    1')
        self.assertEqual(as_delta(12, 5), '+   12')
        self.assertEqual(as_delta(123, 5), '+  123')
        self.assertEqual(as_delta(1234, 5), '+ 1234')

        with temp_locale('en_US.utf8'):
            self.assertEqual(as_delta(1234, 5), '+1,234')
        with temp_locale('de_DE.utf8'):
            self.assertEqual(as_delta(1234, 5), '+1.234')

    def test_as_stat_number(self):
        label = 'unit'
        self.assertEqual(as_stat_number(None, 1, 0, label), 'N/A unit')

        self.assertEqual(as_stat_number(1, 1, 0, label), '1 unit')
        self.assertEqual(as_stat_number(1234, 5, 0, label), ' 1234 unit')
        self.assertEqual(as_stat_number(12345, 5, 0, label), '12345 unit')

        with temp_locale('en_US.utf8'):
            self.assertEqual(as_stat_number(123, 6, 0, label), '   123 unit')
            self.assertEqual(as_stat_number(1234, 6, 0, label), ' 1,234 unit')
            self.assertEqual(as_stat_number(12345, 6, 0, label), '12,345 unit')
        with temp_locale('de_DE.utf8'):
            self.assertEqual(as_stat_number(123, 6, 0, label), '   123 unit')
            self.assertEqual(as_stat_number(1234, 6, 0, label), ' 1.234 unit')
            self.assertEqual(as_stat_number(12345, 6, 0, label), '12.345 unit')

        self.assertEqual(as_stat_number(dict(number=1), 1, 0, label), '1 unit')

        self.assertEqual(as_stat_number(dict(number=1, delta=-1), 1, 1, label), '1 unit [-1]')
        self.assertEqual(as_stat_number(dict(number=2, delta=+0), 1, 1, label), '2 unit [±0]')
        self.assertEqual(as_stat_number(dict(number=3, delta=+1), 1, 1, label), '3 unit [+1]')
        self.assertEqual(as_stat_number(dict(number=3, delta=+1), 1, 2, label), '3 unit [+ 1]')
        self.assertEqual(as_stat_number(dict(number=3, delta=+1), 2, 2, label), ' 3 unit [+ 1]')
        self.assertEqual(as_stat_number(dict(number=3, delta=+1234), 1, 6, label), '3 unit [+  1234]')
        with temp_locale('en_US.utf8'):
            self.assertEqual(as_stat_number(dict(number=3, delta=+1234), 1, 6, label), '3 unit [+ 1,234]')
            self.assertEqual(as_stat_number(dict(number=3, delta=+12345), 1, 6, label), '3 unit [+12,345]')
        with temp_locale('de_DE.utf8'):
            self.assertEqual(as_stat_number(dict(number=3, delta=+1234), 1, 6, label), '3 unit [+ 1.234]')
            self.assertEqual(as_stat_number(dict(number=3, delta=+12345), 1, 6, label), '3 unit [+12.345]')

        self.assertEqual(as_stat_number(dict(delta=-1), 3, 1, label), 'N/A [-1]')

        self.assertEqual(as_stat_number(dict(number=1, delta=-2, new=3), 1, 1, label), '1 unit [-2, 3 new]')
        self.assertEqual(as_stat_number(dict(number=2, delta=+0, new=3, gone=4), 1, 1, label), '2 unit [±0, 3 new, 4 gone]')
        self.assertEqual(as_stat_number(dict(number=3, delta=+1, gone=4), 1, 1, label), '3 unit [+1, 4 gone]')

    def test_as_stat_duration(self):
        label = 'time'
        self.assertEqual(as_stat_duration(None, label), 'N/A time')
        self.assertEqual(as_stat_duration(0, None), '0s')
        self.assertEqual(as_stat_duration(0, label), '0s time')
        self.assertEqual(as_stat_duration(12, label), '12s time')
        self.assertEqual(as_stat_duration(72, label), '1m 12s time')
        self.assertEqual(as_stat_duration(3754, label), '1h 2m 34s time')
        self.assertEqual(as_stat_duration(-3754, label), '1h 2m 34s time')

        self.assertEqual(as_stat_duration(d(3754), label), '1h 2m 34s time')
        self.assertEqual(as_stat_duration(d(3754, 0), label), '1h 2m 34s time [± 0s]')
        self.assertEqual(as_stat_duration(d(3754, 1234), label), '1h 2m 34s time [+ 20m 34s]')
        self.assertEqual(as_stat_duration(d(3754, -123), label), '1h 2m 34s time [- 2m 3s]')
        self.assertEqual(as_stat_duration(dict(delta=123), label), 'N/A time [+ 2m 3s]')

    def do_test_get_short_summary_md(self, stats, expected_md):
        self.assertEqual(get_short_summary_md(stats), expected_md)

    def test_get_short_summary_md(self):
        self.do_test_get_short_summary_md(dict(
        ), ('N/A tests N/A :heavy_check_mark: N/A :zzz: N/A :heavy_multiplication_x: N/A :fire:'))

        self.do_test_get_short_summary_md(dict(
            files=1, suites=2, duration=3,
            tests=4, tests_succ=5, tests_skip=6, tests_fail=7, tests_error=8,
            runs=9, runs_succ=10, runs_skip=11, runs_fail=12, runs_error=13
        ), ('4 tests 5 :heavy_check_mark: 6 :zzz: 7 :heavy_multiplication_x: 8 :fire:'))

        self.do_test_get_short_summary_md(dict(
            files=n(1, 2), suites=n(2, -3), duration=d(3, 4),
            tests=n(4, -5), tests_succ=n(5, 6), tests_skip=n(6, -7), tests_fail=n(7, 8), tests_error=n(8, -9),
            runs=n(9, 10), runs_succ=n(10, -11), runs_skip=n(11, 12), runs_fail=n(12, -13), runs_error=n(13, 14),
            reference_type='type', reference_commit='0123456789abcdef'
        ), ('4 tests [-5] 5 :heavy_check_mark: [+6] 6 :zzz: [-7] 7 :heavy_multiplication_x: [+8] 8 :fire: [-9]'))

    def do_test_get_long_summary_md(self, stats, expected_md):
        self.assertEqual(get_long_summary_md(stats), expected_md)

    def test_get_long_summary_md(self):
        self.do_test_get_long_summary_md(dict(
        ), ('## Unit Test Results\n'
            'N/A files  N/A suites N/A :stopwatch:\n'
            'N/A tests N/A :heavy_check_mark: N/A :zzz: N/A :heavy_multiplication_x: N/A :fire:\n'
            'N/A runs  N/A :heavy_check_mark: N/A :zzz: N/A :heavy_multiplication_x: N/A :fire:\n'))

        self.do_test_get_long_summary_md(dict(
            files=1, suites=2, duration=3,
            tests=4, tests_succ=5, tests_skip=6, tests_fail=7, tests_error=8,
            runs=9, runs_succ=10, runs_skip=11, runs_fail=12, runs_error=13
        ), ('## Unit Test Results\n'
            '1 files  2 suites 3s :stopwatch:\n'
            '4 tests  5 :heavy_check_mark:  6 :zzz:  7 :heavy_multiplication_x:  8 :fire:\n'
            '9 runs  10 :heavy_check_mark: 11 :zzz: 12 :heavy_multiplication_x: 13 :fire:\n'))

        self.do_test_get_long_summary_md(dict(
            files=n(1, 2), suites=n(2, -3), duration=d(3, 4),
            tests=n(4, -5), tests_succ=n(5, 6), tests_skip=n(6, -7), tests_fail=n(7, 8), tests_error=n(8, -9),
            runs=n(9, 10), runs_succ=n(10, -11), runs_skip=n(11, 12), runs_fail=n(12, -13), runs_error=n(13, 14),
            reference_type='type', reference_commit='0123456789abcdef'
        ), ('## Unit Test Results\n'
            '1 files  [+ 2] 2 suites [-3] 3s :stopwatch: [+ 4s]\n'
            '4 tests [- 5]  5 :heavy_check_mark: [+ 6]  6 :zzz: [- 7]  7 :heavy_multiplication_x: [+ 8]  8 :fire: [- 9]\n'
            '9 runs  [+10] 10 :heavy_check_mark: [-11] 11 :zzz: [+12] 12 :heavy_multiplication_x: [-13] 13 :fire: [+14]\n'
            '\n'
            '[±] comparison w.r.t. type commit 01234567'))

    def test_files(self):
        results = parse_junit_xml_files(['../buildkite-horovod/cd4330fe-2af5-44f3-9972-c61690526c55/artifacts/junit.gloo.elastic.spark.torch.xml',
                                         '../buildkite-horovod/c215122a-9851-4aa8-92f9-7cce46730b43/artifacts/junit.mpi.integration.xml',
                                         '../buildkite-horovod/f57caa6c-98d4-4b27-bfb7-9872a8d72b0e/artifacts/junit.gloo.standalone.xml',
                                         '../buildkite-horovod/172135eb-00f6-4c9b-ab3f-77e3bf690378/artifacts/junit.spark.integration.xml',
                                         '../buildkite-horovod/cce56ac0-9aa2-4fdf-a0a9-0a80fabf424e/artifacts/junit.mpi.static.xml',
                                         '../buildkite-horovod/03c86385-4d41-4c22-8283-6bcb3c3b8e43/artifacts/junit.mpi.standalone.xml',
                                         '../buildkite-horovod/5d697bab-6fdc-4771-a8e8-33f82ed5a1b1/artifacts/junit.gloo.elastic.spark.tf.xml',
                                         '../buildkite-horovod/7eedfefc-8ceb-4e5e-8841-1a38dda72767/artifacts/junit.spark.integration.xml',
                                         '../buildkite-horovod/0eb07c0e-3bd8-48ab-8cf2-93b0cae943f0/artifacts/junit.gloo.elastic.xml',
                                         '../buildkite-horovod/ed277c72-31ba-4deb-9890-980293b3e3f6/artifacts/junit.gloo.static.xml'])
        stats = get_stats(results)
        md = get_long_summary_md(stats)
        print(md)


if __name__ == '__main__':
    unittest.main()
