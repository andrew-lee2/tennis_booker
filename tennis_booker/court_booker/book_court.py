from selenium.webdriver.support.ui import Select
from selenium import webdriver
import pandas as pd
import pytz
import time
from tennis_booker.message_parser.send_message import send_response
import re


class Caswell(object):
    def __init__(self, booking_day_datetime, singles_or_doubles, username,
                 password, driver_path, return_number=None, book_now=False):
        self.booking_day_datetime = booking_day_datetime
        self.singles_or_doubles = singles_or_doubles
        self.username = username
        self.password = password
        self.driver = None
        # TODO i dont think we should have a court order, just an initial preferred court
        self.default_court = 'Crt3'
        self.court_booking_order = ['Crt4', 'Crt2', 'Crt3', 'Crt1', 'Crt8', 'Crt7', 'Crt5', 'Crt6']
        self.driver_path = driver_path
        self.response_message = None
        self.return_number = return_number
        self.book_now = book_now

    # TODO change this back
    def initialize_webdriver(self, num_tries=5, heroku=False):
        chrome_driver = None
        if heroku:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.binary_location = self.driver_path
            i = 0

            while i < num_tries:
                try:
                    chrome_driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=options)
                    print('Got chrome webdriver')
                    break
                except:
                    i += 1
                    print('Retry chromedriver number {}'.format(str(i)))

        else:
            chrome_driver = webdriver.Chrome(self.driver_path)

        return chrome_driver

    def login_to_caswell(self):
        login_url = 'https://www.10sportal.net/login.html'
        self.driver.get(login_url)
        username_input = self.driver.find_element_by_id("j_username")
        password_input = self.driver.find_element_by_id("j_password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_xpath = '//*[@id="form-login"]/button'

        self.driver.find_element_by_xpath(login_xpath).click()
        print('logged onto caswell')

    def _get_courtsheet_url(self):
        booking_date = self._get_date()
        base_calendar_url = 'https://www.10sportal.net/entity/dashboard/index.html?src=resourceView&lvDate={date}'
        return base_calendar_url.format(date=booking_date)

    def go_to_courtsheet(self):
        courtsheet_url = self._get_courtsheet_url()
        self.driver.get(courtsheet_url)
        print('went to courtsheet')

    def go_to_form(self):
        submit_url_form = 'https://www.10sportal.net/entity/scheduler/index.html'

        self.driver.get(submit_url_form)
        if self.driver.current_url == submit_url_form:
            print('went to form')

    # TODO this needs to change
    def try_to_book(self):
        court_found = False
        court_str = None

        for court_str in self.court_booking_order:
            print('Current url: {}'.format(self.driver.current_url))
            self._fill_out_form_and_submit(court_str)
            if self.driver.current_url == self._get_courtsheet_url() + '&objStart=1':
                court_found = True
                break

        start_time = self._get_start_time()
        date_str = self._get_date()
        time_date_str = '{} {}'.format(date_str, start_time)

        if court_found:
            booked_message = 'Booked {court} at {time}'.format(court=court_str, time=time_date_str)
            self.response_message = booked_message
            print(booked_message)
        else:
            no_court_message = 'No courts avaliable at {}'.format(time_date_str)
            self.response_message = no_court_message
            print(no_court_message)

        self.driver.quit()
        print('finished trying to book')

    def try_to_book_new(self):
        self._initial_form_fill()
        self._click_submit()
        message = self._get_click_response()
        parsed_info = self._parse_court_response(message)

        # FIXME something doesnt seem right here dont think we shold have to be calling message so many times also need to fix the waiting one again
        while parsed_info['code'] in [0, 2]:
            if parsed_info['code'] == 0:
                self._select_court(parsed_info['valid_info'])
                self._click_submit()
                print('Trying to book {}'.format(parsed_info['valid_info']))
                message = self._get_click_response()
                parsed_info = self._parse_court_response(message)

            else:
                time.sleep(.01)
                message = self._get_click_response()
                parsed_info = self._parse_court_response(message)
                print('Waiting on time to book')
                continue





        # something about returning the message here





    def _code_responses(self, code):
        # TODO make some kind of responses
        start_time = self._get_start_time()
        date_str = self._get_date()
        time_date_str = '{} {}'.format(date_str, start_time)
        pass

    def _get_singles_doubles_value(self):
        # value "2" = doubles; value "1" = singles
        return "1" if self.singles_or_doubles == 'singles' else "2"

    @staticmethod
    def _parse_court_response(message):
        """
        Sample try and book again:
        The court you are trying to reserve is not available for the date and time you selected. Crt 8 is open.
        :param message: str
        :return: tuple (status, valid_info)
        """

        too_early_message = 'Reservations cannot be made more than 2 days in advance'
        booked_court_message = 'The reservation was scheduled successfully'
        no_courts_message = 'There are no open courts'
        court_in_message = re.findall('Crt [0-9]', message)
        parsed_response = {}

        if court_in_message:
            # try other court
            parsed_response['code'] = 0
            parsed_response['valid_info'] = court_in_message[0]
        elif booked_court_message in message:
            # booked court
            parsed_response['code'] = 1
            parsed_response['valid_info'] = None
        elif too_early_message in message:
            # try again later
            parsed_response['code'] = 2
            parsed_response['valid_info'] = None
        elif no_courts_message in message:
            parsed_response['code'] = 3
            parsed_response['valid_info'] = None

        return parsed_response

    def _initial_form_fill(self):
        mode_select = Select(self.driver.find_element_by_name("listMatchTypeID"))
        singles_doubles_value = self._get_singles_doubles_value()
        mode_select.select_by_value(singles_doubles_value)

        date = self.driver.find_element_by_id("apptDate")
        date.clear()
        date.send_keys(self._get_date())

        start_time = self.driver.find_element_by_id("startTime")
        end_time = self.driver.find_element_by_id("endTime")
        start_time.clear()
        end_time.clear()
        start_time.send_keys(self._get_start_time())
        end_time.send_keys(self._get_end_time())

        self._select_court(self.default_court)

        # print("filled out form for {}".format(court_str))

    def _select_court(self, court_str):
        select = Select(self.driver.find_element_by_name("court"))
        select.deselect_all()
        court_number = Caswell.map_court_to_str(court_str)
        select.select_by_value(court_number)

    def _get_click_response(self):
        booking_response_xpath = '// *[ @ id = "body-wrapper"] / fieldset / table / tbody / tr / td[2]'
        return self.driver.find_element_by_xpath(booking_response_xpath).text

    def _click_submit(self):
        self.driver.find_element_by_name("submit").click()
        print('Clicked Submit button')

    # TODO this need a pretty big change
    # def _fill_out_form_and_submit(self, court_str):
    #     mode_select = Select(self.driver.find_element_by_name("listMatchTypeID"))
    #     singles_doubles_value = self._get_singles_doubles_value()
    #     mode_select.select_by_value(singles_doubles_value)
    #
    #     date = self.driver.find_element_by_id("apptDate")
    #     date.clear()
    #     date.send_keys(self._get_date())
    #
    #     start_time = self.driver.find_element_by_id("startTime")
    #     end_time = self.driver.find_element_by_id("endTime")
    #     start_time.clear()
    #     end_time.clear()
    #     start_time.send_keys(self._get_start_time())
    #     end_time.send_keys(self._get_end_time())
    #
    #     select = Select(self.driver.find_element_by_name("court"))
    #     select.deselect_all()
    #     court_number = Caswell.map_court_to_str(court_str)
    #     select.select_by_value(court_number)
    #
    #     # TODO need to refactor this i think
    #     if self.book_now:
    #         self.driver.find_element_by_name("submit").click()
    #     else:
    #         self._to_click_now()
    #
    #     # this will never get called if it worked
    #     booking_response_xpath = '// *[ @ id = "body-wrapper"] / fieldset / table / tbody / tr / td[2]'
    #     print(self.driver.find_element_by_xpath(booking_response_xpath).text)
    #
    #
    #     print("filled out form for {}".format(court_str))

    # FIXME i dont think we need this anymore
    # def _to_click_now(self):
    #     # Their server is not synced the same as heroku's seems to be ~ 8 sec behind
    #     limit = 1500
    #     target_hour = 8
    #     target_minute = 45
    #     target_second = 8
    #     target_timestamp = pd.to_datetime('today').replace(hour=target_hour, minute=target_minute, second=target_second)
    #     central = pytz.timezone('US/Central')
    #     i = 0
    #
    #     while i < limit:
    #         current_time = pd.to_datetime('now').tz_localize(pytz.utc).tz_convert(central).tz_localize(None)
    #         if current_time >= target_timestamp:
    #             self.driver.find_element_by_name("submit").click()
    #             print('Clicked')
    #             return True
    #         else:
    #             time.sleep(.1)
    #             i += 1
    #             if i % 5 == 0:
    #                 print('current minute is {}'.format(current_time))
    #
    #     print('Did not click')
    #     return False

    # TODO do we need this? probably not
    def _close_driver(self):
        self.driver.close()

    def _get_date(self):
        return self.booking_day_datetime.strftime('%m/%d/%Y')

    def _get_start_time(self):
        start_time = self.booking_day_datetime.strftime('%I:%M %p')
        start_time = start_time[1:] if start_time[0] == '0' else start_time
        return start_time

    def _get_end_time(self):
        match_duration = 1.5 if self.singles_or_doubles == 'singles' else 2
        end_time = (self.booking_day_datetime + pd.DateOffset(hours=match_duration)).strftime('%I:%M %p')
        end_time = end_time[1:] if end_time[0] == '0' else end_time
        return end_time

    def _get_courtsheet_time_bucket(self):
        booking_hour = self.booking_day_datetime.hour
        booking_minutes = self.booking_day_datetime.minute
        starting_time_offset = 8
        time_increments = 2

        return (booking_hour - starting_time_offset) * time_increments + booking_minutes / 30

    @staticmethod
    def map_court_to_str(court_str):
        court_mapping = {
            'Crt1': "226",
            'Crt2': "227",
            'Crt3': "228",
            'Crt4': "229",
            'Crt5': "230",
            'Crt6': "231",
            'Crt7': "232",
            'Crt8': "233"
        }
        return court_mapping[court_str]


def run_booker(booking_dt, match_type, username, password, driver,
               return_number=None, book_now=False):
    caswell = Caswell(booking_dt, match_type, username, password, driver,
                      return_number, book_now)

    caswell.driver = caswell.initialize_webdriver()
    caswell.login_to_caswell()
    caswell.go_to_courtsheet()
    caswell.go_to_form()
    # caswell.try_to_book()

    # if caswell.response_message:
    #     send_response(caswell.return_number, caswell.response_message)

    print('finished run_booker')
