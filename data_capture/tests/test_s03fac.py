import json

from copy import deepcopy
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from .common import path, uploaded_xlsx_file, FakeWorkbook, FakeSheet
from .test_models import ModelTestCase
from ..schedules import s03fac, registry


S03FAC = '%s.Schedule03FACPriceList' % s03fac.__name__

S03FAC_XLSX_PATH = path('static', 'data_capture', '03FAC_example.xlsx')


class GleanLaborCategoriesTests(TestCase):
    def test_rows_are_returned(self):
        rows = s03fac.glean_labor_categories_from_file(
            uploaded_xlsx_file(S03FAC_XLSX_PATH))
        self.assertEqual(len(rows), 11)
        self.assertEqual(rows[0], {
            'sin': '811-004',
            'labor_category': 'Project Manager',
            'education_level': 'High School',
            'min_years_experience': '5',
            'unit_of_issue': 'Hour',
            'price_including_iff': '98.0',
        })

    def test_text_formatted_prices_are_gleaned(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells[1][14] = '$  1,107.50 '
        self.assertEqual(book._sheets[0]._cells[1][14], '$  1,107.50 ')

        rows = s03fac.glean_labor_categories_from_book(book)

        row = rows[0]
        self.assertEqual(row['price_including_iff'], '98.00')

    def test_min_education_is_gleaned_from_text(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells[1][2] = 'GED or high school diploma'

        rows = s03fac.glean_labor_categories_from_book(book)

        self.assertEqual(rows[0]['education_level'], 'High School')

    def test_unit_of_issue_is_gleaned_to_hour(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells[1][5] = 'Hourly'

        rows = s03fac.glean_labor_categories_from_book(book)

        self.assertEqual(rows[0]['unit_of_issue'], 'Hour')

    def test_min_experience_is_gleaned_from_text(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells[1][3] = '3'
        rows = s03fac.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['min_years_experience'], '3')

    def test_validation_error_raised_when_sheet_not_present(self):
        with self.assertRaisesRegexp(
            ValidationError,
            r'There is no sheet in the workbook called "foo"'
        ):
            s03fac.glean_labor_categories_from_file(
                uploaded_xlsx_file(S03FAC_XLSX_PATH),
                sheet_name='foo'
            )

    def test_stops_parsing_when_stop_text_encountered(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells.append(deepcopy(s03fac.EXAMPLE_SHEET_ROWS[1]))
        book._sheets[0]._cells.append(deepcopy(s03fac.EXAMPLE_SHEET_ROWS[1]))
        rows = s03fac.glean_labor_categories_from_book(book)
        self.assertEqual(len(rows), 3)

        """
        I don't think this stop text applies to this schedule?
        book._sheets[0]._cells[2][0] = ('Most favored customer’s Discount '
                                        'or Discount Range (MFC)')
        rows = s03fac.glean_labor_categories_from_book(book)
        self.assertEqual(len(rows), 1)
        """

    def stops_parsing_when_sin_and_price_are_empty(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells.append(deepcopy(s03fac.EXAMPLE_SHEET_ROWS[1]))
        book._sheets[0]._cells.append(deepcopy(s03fac.EXAMPLE_SHEET_ROWS[1]))
        rows = s03fac.glean_labor_categories_from_book(book)
        self.assertEqual(len(rows), 3)

        book._sheets[0]._cells[2][0] = ''
        book._sheets[0]._cells[2][11] = ''
        rows = s03fac.glean_labor_categories_from_book(book)
        self.assertEqual(len(rows), 1)


class LoadFromUploadValidationErrorTests(TestCase):
    @patch.object(s03fac, 'glean_labor_categories_from_file')
    def test_reraises_validation_errors(self, m):
        m.side_effect = ValidationError('foo')

        with self.assertRaisesRegexp(ValidationError, r'foo'):
            s03fac.Schedule03FACPriceList.load_from_upload(
                uploaded_xlsx_file(S03FAC_XLSX_PATH))

    def test_raises_validation_error_on_corrupt_files(self):
        f = uploaded_xlsx_file(S03FAC_XLSX_PATH, content=b'foo')

        with self.assertRaisesRegexp(
            ValidationError,
            r'An error occurred when reading your Excel data.'
        ):
            s03fac.Schedule03FACPriceList.load_from_upload(f)


@override_settings(DATA_CAPTURE_SCHEDULES=[S03FAC])
class S03FACTests(ModelTestCase):
    DEFAULT_SCHEDULE = S03FAC

    def test_valid_rows_are_populated(self):
        p = s03fac.Schedule03FACPriceList.load_from_upload(
            uploaded_xlsx_file(S03FAC_XLSX_PATH))

        self.assertEqual(len(p.valid_rows), 11)
        self.assertEqual(p.invalid_rows, [])

        self.assertEqual(p.valid_rows[0].cleaned_data, {
            'education_level': 'High School',
            'labor_category': 'Project Manager',
            'min_years_experience': 5,
            'price_including_iff': Decimal('98.0'),
            'sin': '811-004',
            'unit_of_issue': 'Hour'
        })

    def test_education_level_is_validated(self):
        p = s03fac.Schedule03FACPriceList(rows=[{'education_level': 'Batchelorz'}])

        self.assertRegexpMatches(
            p.invalid_rows[0].errors['education_level'][0],
            r'This field must contain one of the following values'
        )

    def test_price_including_iff_is_validated(self):
        p = s03fac.Schedule03FACPriceList(rows=[{'price_including_iff': '1.10'}])
        self.assertRegexpMatches(
            p.invalid_rows[0].errors['price_including_iff'][0],
            r'Price must be at least'
        )

    def test_min_years_experience_is_validated(self):
        p = s03fac.Schedule03FACPriceList(rows=[{'min_years_experience': ''}])

        self.assertEqual(p.invalid_rows[0].errors['min_years_experience'],
                         ['This field is required.'])

    def test_unit_of_issue_is_validated(self):
        p = s03fac.Schedule03FACPriceList(rows=[{'unit_of_issue': ''}])
        self.assertEqual(p.invalid_rows[0].errors['unit_of_issue'],
                         ['This field is required.'])

        p = s03fac.Schedule03FACPriceList(rows=[{'unit_of_issue': 'Day'}])
        self.assertEqual(p.invalid_rows[0].errors['unit_of_issue'],
                         ['Value must be "Hour" or "Hourly"'])

    def test_unit_of_issue_can_be_hour_or_hourly(self):
        p = s03fac.Schedule03FACPriceList(rows=[{'unit_of_issue': 'Hour'}])
        self.assertNotIn('unit_of_issue', p.invalid_rows[0])

        p = s03fac.Schedule03FACPriceList(rows=[{'unit_of_issue': 'hourly'}])
        self.assertNotIn('unit_of_issue', p.invalid_rows[0])

    def test_add_to_price_list_works(self):
        s = s03fac.Schedule03FACPriceList.load_from_upload(
            uploaded_xlsx_file(S03FAC_XLSX_PATH))

        p = self.create_price_list()
        p.save()

        s.add_to_price_list(p)

        row = p.rows.all()[0]

        self.assertEqual(row.labor_category, 'Material Handler Overtime')
        self.assertEqual(row.education_level, 'HS')
        self.assertEqual(row.min_years_experience, 1)
        self.assertEqual(row.base_year_rate, Decimal('47.04'))
        self.assertEqual(row.sin, '811-004')

        row.full_clean()

    def test_serialize_and_deserialize_work(self):
        s = s03fac.Schedule03FACPriceList.load_from_upload(
            uploaded_xlsx_file(S03FAC_XLSX_PATH))

        saved = json.dumps(registry.serialize(s))
        restored = registry.deserialize(json.loads(saved))

        self.assertTrue(isinstance(restored, s03fac.Schedule03FACPriceList))
        self.assertEqual(s.rows, restored.rows)

    def test_to_table_works(self):
        s = s03fac.Schedule03FACPriceList.load_from_upload(
            uploaded_xlsx_file(S03FAC_XLSX_PATH))
        table_html = s.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_to_table_renders_price_correctly(self):
        book = FakeWorkbook(sheets=[
            FakeSheet(s03fac.DEFAULT_SHEET_NAME, s03fac.EXAMPLE_SHEET_ROWS)])
        book._sheets[0]._cells[1][14] = '$  45.15923 '

        rows = s03fac.glean_labor_categories_from_book(book)
        s = s03fac.Schedule03FACPriceList(rows)

        table_html = s.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

        self.assertIn('$98.00', table_html)

    def test_to_error_table_works(self):
        s = s03fac.Schedule03FACPriceList.load_from_upload(
            uploaded_xlsx_file(S03FAC_XLSX_PATH))
        table_html = s.to_error_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_render_upload_example_works(self):
        html = s03fac.Schedule03FACPriceList.render_upload_example()
        self.assertTrue('High School' in html)
