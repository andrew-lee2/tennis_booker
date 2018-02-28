from selenium.webdriver.support.ui import Select
import pandas as pd
import time


class Caswell(object):
    def __init__(self, booking_day_datetime, singles_or_doubles, username, password, driver):
        self.booking_day_datetime = booking_day_datetime
        self.singles_or_doubles = singles_or_doubles
        self.username = username
        self.password = password
        self.driver = None
        self.number_of_courts = 8
        self.driver = driver

    def login_to_caswell(self):
        login_url = 'https://www.10sportal.net/login.html'
        self.driver.get(login_url)
        username_input = self.driver.find_element_by_id("j_username")
        password_input = self.driver.find_element_by_id("j_password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_xpath = '//*[@id="form-login"]/button'

        self.driver.find_element_by_xpath(login_xpath).click()

    def _get_courtsheet_url(self):
        booking_date = self._get_date()
        base_calendar_url = 'https://www.10sportal.net/entity/dashboard/index.html?src=resourceView&lvDate={date}'
        return base_calendar_url.format(date=booking_date)

    def go_to_courtsheet(self):
        courtsheet_url = self._get_courtsheet_url()
        self.driver.get(courtsheet_url)

    def go_to_form(self):
        max_tries = 110
        submit_url_form = 'https://www.10sportal.net/entity/scheduler/index.html'
        i = 0
        while i < max_tries:
            i += 1
            self.driver.get(submit_url_form)
            if self.driver.current_url == submit_url_form:
                break
            else:
                time.sleep(.15)

    def try_to_book(self):
        number_of_tries = self.number_of_courts
        default_court = 'Crt4'
        i = 0

        # im sure there's a better way to do below
        while i < number_of_tries:
            i += 1
            self._fill_out_form_and_submit(default_court)
            if self.driver.current_url == self._get_courtsheet_url() + '&objStart=1':
                break
            else:
                default_court = 'Crt' + str(i)

            if i == number_of_tries:
                print('no courts available')

        self.driver.quit()

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

        self.driver.find_element_by_name("submit").click()

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


def run_booker(booking_dt, match_type, username, password, driver):
    caswell = Caswell(booking_dt, match_type, username, password, driver)

    caswell.login_to_caswell()
    print('logged onto caswell')
    caswell.go_to_courtsheet()
    print('went to courtsheet')
    caswell.go_to_form()
    print('went to form')
    caswell.try_to_book()
    # TODO need to return a success or failure message
