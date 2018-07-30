from selenium.webdriver.support.ui import Select
from selenium import webdriver
import pandas as pd
import time
from tennis_booker.message_parser.send_message import send_response


class Caswell(object):
    def __init__(self, booking_day_datetime, singles_or_doubles, username,
                 password, driver_path, twilio_user=None, twilio_pw=None, return_number=None, book_now=False):
        self.booking_day_datetime = booking_day_datetime
        self.singles_or_doubles = singles_or_doubles
        self.username = username
        self.password = password
        self.driver = None
        self.court_booking_order = ['Crt4', 'Crt2', 'Crt3', 'Crt1', 'Crt8', 'Crt7', 'Crt5', 'Crt6']
        self.driver_path = driver_path
        self.response_message = None
        self.twilio_user = twilio_user
        self.twilio_pw = twilio_pw
        self.return_number = return_number
        self.book_now = book_now

    def initialize_webdriver(self, num_tries=5):
        chrome_driver = None
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
        max_tries = 120
        submit_url_form = 'https://www.10sportal.net/entity/scheduler/index.html'
        i = 0
        while i < max_tries:
            i += 1
            self.driver.get(submit_url_form)
            if self.driver.current_url == submit_url_form:
                print('went to form')
                break
            else:
                if i % 5 == 0:
                    print('{} try to go to form, {}'.format(i, self.driver.current_url))
                time.sleep(.10)

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

    def _get_singles_doubles_value(self):
        # value "2" = doubles; value "1" = singles
        value = "1" if self.singles_or_doubles == 'singles' else "2"
        return value

    def _fill_out_form_and_submit(self, court_str):

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

        select = Select(self.driver.find_element_by_name("court"))
        select.deselect_all()
        court_number = Caswell.map_court_to_str(court_str)
        select.select_by_value(court_number)

        # TODO need some kind of time check to submit here
        if self.book_now:
            print(pd.to_datetime('now'))
            self.driver.find_element_by_name("submit").click()
        else:
            self._to_click_now()
        print("filled out form for {}".format(court_str))

    def _to_click_now(self):
        # Their server is not synced the same as heroku's seems to be ~ 8 sec behind
        limit = 1500
        target_hour = 8
        target_minute = 45
        target_second = 8
        target_timestamp = pd.to_datetime('today').replace(hour=target_hour, minute=target_minute, second=target_second)

        i = 0

        while i < limit:
            current_time = pd.to_datetime('now')
            if current_time >= target_timestamp:
                self.driver.find_element_by_name("submit").click()
                print('Clicked')
                return True
            else:
                time.sleep(.1)
                i += 1
                if i % 5 == 0:
                    print('current minute is {}'.format(current_time))

        print('Did not click')
        return False

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
               twilio_user=None, twilio_pw=None, return_number=None, book_now=False):
    caswell = Caswell(booking_dt, match_type, username, password, driver,
                      twilio_user, twilio_pw, return_number, book_now)

    caswell.driver = caswell.initialize_webdriver()
    caswell.login_to_caswell()
    caswell.go_to_courtsheet()
    caswell.go_to_form()
    caswell.try_to_book()

    if caswell.response_message:
        send_response(caswell.return_number, caswell.response_message)

    print('finished run_booker')
