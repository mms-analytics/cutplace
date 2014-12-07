"""
Test for `_tools` module.
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
import decimal
import os.path
import unittest

from cutplace import cid
from cutplace import dev_test
from cutplace import errors
from cutplace import _tools


class ToolsTest(unittest.TestCase):
    def test_can_create_test_date_time(self):
        for _ in range(15):
            dateTime = dev_test.createTestDateTime()
            self.assertTrue(dateTime is not None)
            self.assertNotEqual(dateTime, "")

    def test_can_create_test_name(self):
        for _ in range(15):
            name = dev_test.createTestName()
            self.assertTrue(name is not None)
            self.assertNotEqual(name, "")

    def test_can_create_test_customer_row(self):
        for customer_id in range(15):
            row = dev_test.createTestCustomerRow(customer_id)
            self.assertTrue(row is not None)
            self.assertEqual(len(row), 6)

    def test_can_query_version(self):
        # Simply exercise these functions, their results do not really matter.
        _tools.platformVersion()
        _tools.pythonVersion()

    def test_can_validate_python_name(self):
        self.assertEqual(_tools.validatedPythonName("x", "abc_123"), "abc_123")
        self.assertEqual(_tools.validatedPythonName("x", " abc_123 "), "abc_123")
        self.assertRaises(NameError, _tools.validatedPythonName, "x", "1337")
        self.assertRaises(NameError, _tools.validatedPythonName, "x", "")
        self.assertRaises(NameError, _tools.validatedPythonName, "x", " ")
        self.assertRaises(NameError, _tools.validatedPythonName, "x", "a.b")

    def test_can_build_human_readable_list(self):
        self.assertEqual(_tools.humanReadableList([]), "")
        self.assertEqual(_tools.humanReadableList(["a"]), "'a'")
        self.assertEqual(_tools.humanReadableList(["a", "b"]), "'a' or 'b'")
        self.assertEqual(_tools.humanReadableList(["a", "b", "c"]), "'a', 'b' or 'c'")

    def _test_can_derive_suffix(self, expectedPath, pathToTest, suffixToTest):
        actualPath = _tools.withSuffix(pathToTest, suffixToTest)
        self.assertEqual(expectedPath, actualPath)

    def test_can_build_name_with_suffix(self):
        self._test_can_derive_suffix("hugo.pas", "hugo.txt", ".pas")
        self._test_can_derive_suffix("hugo", "hugo.txt", "")
        self._test_can_derive_suffix("hugo.", "hugo.txt", ".")
        self._test_can_derive_suffix("hugo.txt", "hugo", ".txt")
        self._test_can_derive_suffix(os.path.join("eggs", "hugo.pas"), os.path.join("eggs", "hugo.txt"), ".pas")

    def test_can_asciify_text(self):
        self.assertEqual(_tools.asciified("hello"), "hello")
        self.assertEqual(_tools.asciified("h\xe4ll\xf6"), "hallo")
        self.assertEqual(_tools.asciified("hello.world!"), "hello.world!")

    def test_fails_on_asciifying_non_unicode(self):
        self.assertRaises(ValueError, _tools.asciified, b"hello")
        self.assertRaises(ValueError, _tools.asciified, 17)

    def test_can_namify_text(self):
        self.assertEqual(_tools.namified("hello"), "hello")
        self.assertEqual(_tools.namified("hElLo"), "hElLo")
        self.assertEqual(_tools.namified("h3LL0"), "h3LL0")
        self.assertEqual(_tools.namified("Date of birth"), "Date_of_birth")
        self.assertEqual(_tools.namified("a    b"), "a_b")

    def test_can_namify_number(self):
        self.assertEqual(_tools.namified("1a"), "x1a")
        self.assertEqual(_tools.namified("3.1415"), "x3_1415")

    def test_can_namify_keyword(self):
        self.assertEqual(_tools.namified("if"), "if_")

    def test_can_namify_empty_text(self):
        self.assertEqual(_tools.namified(""), "x")
        self.assertEqual(_tools.namified(" "), "x")
        self.assertEqual(_tools.namified("\t"), "x")

    def test_can_namify_control_characters(self):
        self.assertEqual(_tools.namified("\r"), "x")
        self.assertEqual(_tools.namified("a\rb"), "a_b")


class NumberedTest(unittest.TestCase):
    def test_can_detect_none_number(self):
        self.assertEqual(_tools.numbered("123abc"), (None, False, "123abc"))
        self.assertEqual(_tools.numbered("01.02.2014"), (None, False, "01.02.2014"))

    def test_can_detect_integer(self):
        self.assertEqual(_tools.numbered("123"), (_tools.NUMBER_INTEGER, False, 123))

    def test_can_detect_decimal_with_point(self):
        self.assertEqual(_tools.numbered("123.45"), (_tools.NUMBER_DECIMAL_POINT, False, decimal.Decimal("123.45")))
        self.assertEqual(_tools.numbered("123,456.78"), (_tools.NUMBER_DECIMAL_POINT, True, decimal.Decimal("123456.78")))

    def test_can_detect_decimal_with_comma(self):
        actual = _tools.numbered("123,45", decimalSeparator=",", thousandsSeparator=".")
        expected = (_tools.NUMBER_DECIMAL_COMMA, False, decimal.Decimal("123.45"))
        self.assertEqual(actual, expected)
        actual = _tools.numbered("123.456,78", decimalSeparator=",", thousandsSeparator=".")
        expected = (_tools.NUMBER_DECIMAL_COMMA, True, decimal.Decimal("123456.78"))
        self.assertEqual(actual, expected)


class RowsTest(unittest.TestCase):
    def test_can_read_excel_rows(self):
        excel_path = dev_test.getTestInputPath('valid_customers.xls')
        row_count = len(list(_tools.excel_rows(excel_path)))
        self.assertTrue(row_count > 0)

    def test_can_read_ods_rows(self):
        ods_path = dev_test.getTestInputPath('valid_customers.ods')
        ods_rows = list(_tools.ods_rows(ods_path))
        self.assertTrue(len(ods_rows) > 0)
        none_empty_rows = [row for row in ods_rows if len(row) > 0]
        self.assertTrue(len(none_empty_rows) > 0)

    def test_fails_on_ods_with_broken_zip(self):
        broken_ods_path = dev_test.getTestInputPath('customers.csv')
        try:
            list(_tools.ods_rows(broken_ods_path))
            self.fail('expected DataFormatError')
        except errors.DataFormatError as error:
            error_message = '%s' % error
            self.assertTrue('cannot uncompress ODS spreadsheet:' in error_message,
                    'error_message=%r' % error_message)

    def test_fails_on_ods_without_content_xml(self):
        broken_ods_path = dev_test.getTestInputPath('broken_without_content_xml.ods')
        try:
            list(_tools.ods_rows(broken_ods_path))
            self.fail('expected DataFormatError')
        except errors.DataFormatError as error:
            error_message = '%s' % error
            self.assertTrue('cannot extract content.xml' in error_message,
                    'error_message=%r' % error_message)

    def test_fails_on_ods_without_broken_content_xml(self):
        broken_ods_path = dev_test.getTestInputPath('broken_content_xml.ods')
        try:
            list(_tools.ods_rows(broken_ods_path))
            self.fail('expected DataFormatError')
        except errors.DataFormatError as error:
            error_message = '%s' % error
            self.assertTrue('cannot parse content.xml' in error_message,
                    'error_message=%r' % error_message)

    def test_fails_on_non_existent_ods_sheet(self):
        ods_path = dev_test.getTestInputPath('valid_customers.ods')
        try:
            list(_tools.ods_rows(ods_path, 123))
            self.fail('expected DataFormatError')
        except errors.DataFormatError as error:
            error_message = '%s' % error
            self.assertTrue('ODS must contain at least' in error_message,
                    'error_message=%r' % error_message)

    def test_fails_on_delimited_with_unterminated_quote(self):
        cid_path = dev_test.getTestIcdPath('customers.ods')
        customer_cid = cid.Cid(cid_path)
        broken_delimited_path = dev_test.getTestInputPath('broken_customers_with_unterminated_quote.csv')
        try:
            list(_tools.delimited_rows(broken_delimited_path, customer_cid.data_format))
        except errors.DataFormatError as error:
            error_message = '%s' % error
            self.assertTrue('cannot parse delimited file' in error_message,
                    'error_message=%r' % error_message)

    def test_can_read_fixed_rows(self):
        cid_path = dev_test.getTestIcdPath('customers_fixed.ods')
        customer_cid = cid.Cid(cid_path)
        fixed_path = dev_test.getTestInputPath('valid_customers_fixed.txt')
        field_names_and_lengths = cid.field_names_and_lengths(customer_cid)
        rows = list(_tools.fixed_rows(fixed_path, customer_cid.data_format.encoding, field_names_and_lengths))
        self.assertNotEqual(0, len(rows))
        for row_index in range(len(rows) - 1):
            row = rows[row_index]
            next_row = rows[row_index + 1]
            self.assertNotEqual(0, len(row))
            self.assertEqual(len(row), len(next_row))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()