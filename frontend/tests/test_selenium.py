""" Note about tests:

They time out and cause failures intermittently.
See https://travis-ci.org/18F/calc/builds/77211412.

The original author of the tests and I could not solve this problem. I've
watched the timeouts happen on specific tests by increasing nose's verbosity,
and I have seen them on these tests:
test_schedule_column_is_open_by_default
test_contract_link

8/25/15 [TS]
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import Select

from contracts.mommy_recipes import get_contract_recipe
from model_mommy.recipe import seq
from itertools import cycle

import re
import time
import os
import socket
from datetime import datetime

from . import axe
from .utils import build_static_assets


WD_HUB_URL = os.environ.get('WD_HUB_URL')
WD_TESTING_URL = os.environ.get('WD_TESTING_URL')
WD_TESTING_BROWSER = os.environ.get('WD_TESTING_BROWSER',
                                    'phantomjs')
WD_SOCKET_TIMEOUT = int(os.environ.get('WD_SOCKET_TIMEOUT', '5'))
PHANTOMJS_TIMEOUT = int(os.environ.get('PHANTOMJS_TIMEOUT', '3'))
WEBDRIVER_TIMEOUT_LOAD_ATTEMPTS = 10


def _get_webdriver(name):
    name = name.lower()
    if name == 'chrome':
        return webdriver.Chrome()
    elif name == 'firefox':
        return webdriver.Firefox()
    elif name == 'phantomjs':
        driver = webdriver.PhantomJS()
        driver.command_executor.set_timeout(PHANTOMJS_TIMEOUT)
        return driver
    raise Exception('No such webdriver: "%s"' % name)


class SeleniumTestCase(StaticLiveServerTestCase):
    connect = None
    driver = None
    screenshot_filename = 'selenium_tests/screenshot.png'
    window_size = (1000, 1000)

    @classmethod
    def get_driver(cls):
        if not WD_TESTING_URL:
            return _get_webdriver(WD_TESTING_BROWSER)

        if not WD_HUB_URL:
            raise Exception('WD_HUB_URL must be defined!')

        desired_cap = webdriver.DesiredCapabilities.CHROME
        # these are the standard Selenium capabilities

        if 'WD_TESTING_PLATFORM' in os.environ:
            desired_cap['platform'] = os.environ['WD_TESTING_PLATFORM']
        desired_cap['browserName'] = WD_TESTING_BROWSER
        if 'WD_TESTING_BROWSER_VERSION' in os.environ:
            desired_cap['version'] = os.environ['WD_TESTING_BROWSER_VERSION']

        desired_cap['name'] = 'CALC'
        print('capabilities:', desired_cap)

        driver = webdriver.Remote(
            desired_capabilities=desired_cap,
            command_executor=WD_HUB_URL
        )

        # XXX should this be higher?
        driver.implicitly_wait(20)
        return driver

    @classmethod
    def setUpClass(cls):
        cls._old_socket_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(WD_SOCKET_TIMEOUT)
        build_static_assets()
        cls.driver = cls.get_driver()
        cls.longMessage = True
        cls.maxDiff = None
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.take_screenshot()
        cls.driver.quit()
        if cls.connect:
            cls.connect.shutdown_connect()
        socket.setdefaulttimeout(cls._old_socket_timeout)
        super().tearDownClass()

    @classmethod
    def take_screenshot(cls):
        """
        Take a screenshot of the browser whenever the test fails?
        """
        png = cls.screenshot_filename
        if '%' in png:
            png = png % {'date': datetime.today()}
        cls.driver.get_screenshot_as_file(png)
        print('screenshot taken: %s' % png)

    def _fail(self, *args, **kwargs):
        super().fail(*args, **kwargs)

    def setUp(self):
        self.base_url = self.live_server_url
        if WD_TESTING_URL:
            self.base_url = WD_TESTING_URL
        self.driver.set_window_size(*self.window_size)
        super().setUp()

    def load(self, uri='/'):
        url = self.base_url + uri
        print('loading URL: %s' % url)

        attempts = 0

        while True:
            try:
                self.driver.get(url)
                break
            except socket.timeout:
                if attempts >= WEBDRIVER_TIMEOUT_LOAD_ATTEMPTS:
                    raise
                print("Socket timeout, trying again.")
                attempts += 1

        # self.driver.execute_script('$("body").addClass("selenium")')
        return self.driver

    def wait_for(self, condition, timeout=10):
        try:
            wait_for(condition, timeout=timeout)
        except Exception as err:
            return self.fail(err)
        return True


class DataExplorerTests(SeleniumTestCase):
    def load_and_wait(self, uri='/'):
        self.load(uri)
        self.wait_for(self.data_is_loaded)
        return self.driver

    def get_form(self):
        return self.driver.find_element_by_id('search')

    def submit_form(self):
        form = self.get_form()
        form.submit()
        time.sleep(.001)
        return form

    def submit_form_and_wait(self):
        form = self.submit_form()
        self.wait_for(self.data_is_loaded)
        return form

    def search_for(self, query):
        q = self.driver.find_element_by_name('q')
        q.clear()
        q.send_keys(query + '\n')

    def search_for_query_type(self, query, query_type):
        # Important: We want to click the radio before entering the
        # text, otherwise the radio may be obscured by the autocomplete
        # suggestions (that's the working theory, at least).

        form = self.get_form()
        self.set_form_values(form, query_type=query_type)
        self.search_for(query)

    def data_is_loaded(self):
        form = self.get_form()
        if has_class(form, 'error'):
            self.driver.get_screenshot_as_file('test/data_not_loaded.png')
            return self.fail(
                "Form submit error: '%s'" %
                form.find_element_by_css_selector('.error-message').text
            )
        return has_class(form, 'loaded')

    def test_titles_are_correct(self):
        get_contract_recipe().make(_quantity=1,
                                   labor_category=seq("Architect"))
        driver = self.load_and_wait()
        self.assertTrue(
            driver.title.startswith('CALC'),
            'Title mismatch, {} does not start with CALC'.format(driver.title)
        )

    def test_contract_link(self):
        get_contract_recipe().make(_quantity=1, idv_piid='GS-23F-0062P')
        driver = self.load_and_wait()
        self.get_form()

        contract_link = driver.find_element_by_xpath(
            '//*[@id="results-table"]/tbody/tr[1]/td[5]/a')
        redirect_url = ('https://www.gsaadvantage.gov/ref_text/'
                        'GS23F0062P/GS23F0062P_online.htm')
        self.assertEqual(contract_link.get_attribute('href'), redirect_url)

    def test_there_is_no_business_size_column(self):
        get_contract_recipe().make(_quantity=5, vendor_name=seq("Large Biz"),
                                   business_size='o')
        driver = self.load()
        self.get_form()

        col_headers = get_column_headers(driver)

        for head in col_headers:
            self.assertFalse(has_matching_class(
                head, 'column-business[_-]size'))

    def test_index_accessibility(self):
        self.load_and_wait()
        axe.run_and_validate(self.driver)

    def test_styleguide_accessibility(self):
        self.load('/styleguide/')
        axe.run_and_validate(self.driver)

    def test_schedule_column_is_open_by_default(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load()
        col_header = find_column_header(driver, 'schedule')

        self.assertFalse(has_class(col_header, 'collapsed'))

    def test_schedule_column_is_last(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        col_headers = get_column_headers(driver)
        self.assertTrue(has_class(col_headers[-1], 'column-schedule'))

    def test_sortable_columns__non_default(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()

        for col in ['labor_category', 'education_level',
                    'min_years_experience']:
            self._test_column_is_sortable(driver, col)

    def test_price_column_is_sortable_and_is_the_default_sort(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        col_header = find_column_header(driver, 'current_price')
        # current_price should be sorted ascending by default
        self.assertTrue(has_class(col_header, 'sorted'),
                        "current_price is not the default sort")
        self.assertTrue(has_class(col_header, 'sortable'),
                        "current_price column is not sortable")
        self.assertFalse(has_class(col_header, 'descending'),
                         "current_price column is descending by default")
        col_header.click()
        self.assertTrue(has_class(col_header, 'sorted'),
                        "current_price is still sorted after clicking")

    def test_one_column_is_sortable_at_a_time(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        header1 = find_column_header(driver, 'education_level')
        header2 = find_column_header(driver, 'labor_category')

        header1.click()
        self.wait_for(lambda: has_class(header1, 'sorted'))
        self.assertTrue(has_class(header1, 'sorted'), "column 1 is not sorted")
        self.assertFalse(has_class(header2, 'sorted'),
                         "column 2 is still sorted (but should not be)")

        header2.click()
        self.wait_for(lambda: has_class(header2, 'sorted'))
        self.assertTrue(has_class(header2, 'sorted'), "column 2 is not sorted")
        self.assertFalse(has_class(header1, 'sorted'),
                         "column 1 is still sorted (but should not be)")

    def test_histogram_is_shown(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        rect_count = len(
            driver.find_elements_by_css_selector('.histogram rect'))
        self.assertTrue(
            rect_count > 0,
            "No histogram rectangles found (selector: '.histogram rect')"
        )

    def test_histogram_shows_tooltips(self):
        get_contract_recipe().make(_quantity=5)
        driver = self.load_and_wait()
        bars = driver.find_elements_by_css_selector('.histogram .bar')
        # TODO: check for "real" tooltips?
        for i, bar in enumerate(bars):
            title = bar.find_element_by_css_selector('title')
            self.assertIsNotNone(
                title.text, "Histogram bar #%d has no text" % i)

    def test_download_graph_button_shown(self):
        get_contract_recipe().make(_quantity=1)
        driver = self.load_and_wait()
        self.assertTrue(driver.find_element_by_id(
            'download-histogram').is_displayed())

    def test_histogram_download_canvas_hidden(self):
        get_contract_recipe().make(_quantity=1)
        driver = self.load_and_wait()
        self.assertFalse(driver.find_element_by_id('graph').is_displayed())

    def test_query_type_matches_words(self):
        get_contract_recipe().make(_quantity=3, labor_category=cycle(
            ['Systems Engineer', 'Software Engineer', 'Consultant']))
        driver = self.load()
        self.wait_for(self.data_is_loaded)
        self.get_form()
        self.search_for('engineer')
        self.submit_form_and_wait()
        cells = driver.find_elements_by_css_selector(
            'table.results tbody .column-labor_category')
        self.assertEqual(
            len(cells), 2, 'wrong cell count: %d (expected 2)' % len(cells))
        for cell in cells:
            self.assertTrue('Engineer' in cell.text,
                            'found cell without "Engineer": "%s"' % cell.text)

    def test_query_type_matches_phrase(self):
        get_contract_recipe().make(_quantity=3, labor_category=cycle(
            ['Systems Engineer I', 'Software Engineer II', 'Consultant II']))
        driver = self.load()
        self.wait_for(self.data_is_loaded)
        self.search_for_query_type('software engineer', 'match_phrase')
        self.submit_form_and_wait()
        cells = driver.find_elements_by_css_selector(
            'table.results tbody .column-labor_category')
        self.assertEqual(
            len(cells), 1, 'wrong cell count: %d (expected 1)' % len(cells))
        self.assertEqual(cells[0].text, 'Software Engineer II',
                         'bad cell text: "%s"' % cells[0].text)

    def test_query_type_matches_exact(self):
        get_contract_recipe().make(_quantity=3, labor_category=cycle(
            ['Software Engineer I', 'Software Engineer',
             'Senior Software Engineer']))
        driver = self.load()
        self.wait_for(self.data_is_loaded)
        self.search_for_query_type('software engineer', 'match_exact')
        self.submit_form_and_wait()
        cells = driver.find_elements_by_css_selector(
            'table.results tbody .column-labor_category')
        self.assertEqual(
            len(cells), 1, 'wrong cell count: %d (expected 1)' % len(cells))
        self.assertEqual(cells[0].text, 'Software Engineer',
                         'bad cell text: "%s"' % cells[0].text)

    def _test_column_is_sortable(self, driver, colname):
        col_header = find_column_header(driver, colname)
        self.assertTrue(has_class(col_header, 'sortable'),
                        "{} column is not sortable".format(colname))
        # NOT sorted by default
        self.assertFalse(has_class(col_header, 'sorted'),
                         "{} column is sorted by default".format(colname))
        col_header.click()
        self.assertTrue(
            has_class(col_header, 'sorted'),
            "{} column is not sorted after clicking".format(colname)
        )

    def assert_results_count(self, driver, num):
        results_count = driver.find_element_by_id('results-count').text
        # remove commas from big numbers (e.g. "1,000" -> "1000")
        results_count = results_count.replace(',', '')
        self.assertNotEqual(results_count, u'', "No results count")
        self.assertEqual(results_count, str(
            num), "Results count mismatch: '%s' != %d" % (results_count, num))

    def get_label_for_input(self, input, form):
        return form.find_element_by_css_selector('label[for="{}"]'.format(
            input.get_attribute('id')
        ))

    def set_form_value(self, form, key, value):
        fields = form.find_elements_by_name(key)
        field = fields[0]
        if field.tag_name == 'select':
            Select(field).select_by_value(value)
        else:
            field_type = field.get_attribute('type')
            if field_type in ('checkbox', 'radio'):
                for _field in fields:
                    if _field.get_attribute('value') == value:
                        self.get_label_for_input(_field, form).click()
            else:
                field.send_keys(str(value))
        return field

    def set_form_values(self, form, **values):
        for key, value in values.items():
            self.set_form_value(form, key, value)


def wait_for(condition, timeout=3):
    start = time.time()
    while time.time() < start + timeout:
        if condition():
            return True
        else:
            time.sleep(0.01)
    raise Exception('Timeout waiting for {}'.format(condition.__name__))


def has_class(element, klass):
    return klass in element.get_attribute('class').split(' ')


def has_matching_class(element, regex):
    return re.search(regex, element.get_attribute('class'))


def find_column_header(driver, col_name):
    return driver.find_element_by_css_selector(
        'th.column-{}'.format(col_name)
    )


def get_column_headers(driver):
    return driver.find_elements_by_xpath('//thead/tr/th')


# We only need this monkey patch here because the stack traces clutter up the
# test results output. --shawn
def patch_broken_pipe_error():
    """
    Monkey patch BaseServer.handle_error to not write a stack trace to stderr
    on broken pipe: <http://stackoverflow.com/a/22618740/362702>
    """
    import sys
    from socketserver import BaseServer
    from wsgiref import handlers

    handle_error = BaseServer.handle_error
    log_exception = handlers.BaseHandler.log_exception

    def is_broken_pipe_error():
        type, err, tb = sys.exc_info()
        r = repr(err)
        return r in (
            "error(32, 'Broken pipe')",
            "error(54, 'Connection reset by peer')"
        )

    def my_handle_error(self, request, client_address):
        if not is_broken_pipe_error():
            handle_error(self, request, client_address)

    def my_log_exception(self, exc_info):
        if not is_broken_pipe_error():
            log_exception(self, exc_info)

    BaseServer.handle_error = my_handle_error
    handlers.BaseHandler.log_exception = my_log_exception


patch_broken_pipe_error()


if __name__ == '__main__':
    import unittest
    unittest.main()
