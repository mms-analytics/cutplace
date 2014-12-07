"""
Test cutplace performance.
"""
# Copyright (C) 2009-2013 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import io
import logging
import pstats
import os.path
import unittest


from cutplace import cid
from cutplace import dev_test
from cutplace import validator
from cutplace import _cutplace
from cutplace import _tools

_log = logging.getLogger("cutplace.dev_reports")
# Import "best" profiler available.
try:
    import cProfile as profile
except ImportError:
    import profile
    _log.warning('cProfile is not available, using profile')


def _build_and_validate_many_customers():
    icd_ods_path = dev_test.getTestIcdPath("customers.ods")
    loc_csv_path = dev_test.getTestFile("input", "lots_of_customers.csv")
    dev_test.createLotsOfCustomersCsv(loc_csv_path, 50)

    # Validate the data using the API, so in case of errors we get specific information.
    customers_cid = cid.Cid(icd_ods_path)
    reader = validator.Reader(customers_cid, loc_csv_path)
    reader.validate()

    # Validate the data using the command line application in order to use
    # the whole tool chain from an end user's point of view.
    exit_code = _cutplace.main(["test_performance.py", icd_ods_path, loc_csv_path])
    if exit_code != 0:
        raise ValueError("exit code of performance test must be 0 but is %d" % exit_code)


class PerformanceTest(unittest.TestCase):
    """
    Test case for performance profiling.
    """
    def test_can_validate_many_customers(self):
        target_base_path = os.path.join("build", "site", "reports")
        item_name = "profile_lots_of_customers"
        target_profile_path = os.path.join(target_base_path, item_name) + ".profile"
        target_report_path = os.path.join(target_base_path, item_name) + ".txt"
        _tools.mkdirs(os.path.dirname(target_report_path))
        profile.run(
            "from tests import test_performance; test_performance._build_and_validate_many_customers()",
            target_profile_path)
        with io.open(target_report_path, "w", encoding='utf-8') as targetReportFile:
            stats = pstats.Stats(target_profile_path, stream=targetReportFile)
            stats.sort_stats("cumulative").print_stats("cutplace", 20)


if __name__ == '__main__':  # pragma: no cover
    logging.basicConfig()
    unittest.main()