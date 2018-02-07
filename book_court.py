import configparser
from selenium import webdriver, common
from selenium.webdriver.support.ui import Select
import pandas as pd
import re


class Caswell(object):
    def __init__(self, booking_day_datetime, singles_or_doubles, username, password):
        self.booking_day_datetime = booking_day_datetime
        self.singles_or_doubles = singles_or_doubles
        self.username = username
        self.password = password
        self.driver = None
        self.number_of_courts = 8

    def create_driver(self):
        # TODO will do this later depending on local or not
        self.driver = webdriver.Firefox()

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

    def login_to_caswell(self):
        login_url = 'https://www.10sportal.net/login.html'
        self.driver.get(login_url)
        username_input = self.driver.find_element_by_id("j_username")
        password_input = self.driver.find_element_by_id("j_password")
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_xpath = '//*[@id="form-login"]/button'

        self.driver.find_element_by_xpath(login_xpath).click()

    def go_to_courtsheet(self):
        booking_date = self._get_date()
        base_calendar_url = 'https://www.10sportal.net/entity/dashboard/index.html?src=resourceView&lvDate={date}'
        courtsheet_day_url = base_calendar_url.format(date=booking_date)
        self.driver.get(courtsheet_day_url)

    def go_to_form(self):
        # click_time_bucket = self._get_courtsheet_time_bucket()
        # bucket_xpath_raw = '//*[@id="calendar"]/div/div/div/div/div/table/tbody/tr[{bucket}]/td/div'
        # bucket_xpath_raw = '// *[ @ id = "calendar"] / div / div / div / div / div / table / tbody / tr[{bucket}] / th'
        # print(self.driver.current_url)
        # top_bar = self.driver.find_element_by_class_name("content-box-content" )
        # print(top_bar.location)
        #
        # action = webdriver.common.action_chains.ActionChains(self.driver)
        #
        # i = 0
        # max_number_of_tries = 8
        # pixel_court_distance = 95
        # initial_pixel_buffer_x = 115
        # initial_pixel_buffer_y = 210

        submit_url_form = 'https://www.10sportal.net/entity/scheduler/index.html'
        self.driver.get(submit_url_form)

        # while i < max_number_of_tries:
        #     # click_time_bucket = 1 if max_number_of_tries / self.number_of_courts > 0 else click_time_bucket
        #     # bucket_xpath = bucket_xpath_raw.format(bucket=click_time_bucket)
        #     # bucket_xpath = bucket_xpath_raw.format(bucket=0)
        #     # bucket_element = self.driver.find_element_by_xpath(bucket_xpath)
        #     pixels_to_move_right = (max_number_of_tries * pixel_court_distance) + initial_pixel_buffer_x
        #
        #     action.move_to_element_with_offset(top_bar, pixels_to_move_right, initial_pixel_buffer_y).click().perform()
        #     i += 1
        #     try:
        #         reserved_title_xpath = '//*[@id="ui-id-1"]'
        #         reserved_element = self.driver.find_element_by_xpath(reserved_title_xpath)
        #         if reserved_element.text == 'Reserved':
        #             continue
        #     except common.exceptions.NoSuchElementException:
        #         submit_url_form = 'https://www.10sportal.net/entity/scheduler/index.html'
        #         self.driver.get(submit_url_form)
        #         break

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

    def try_to_book(self):
        # print(self.driver.current_url)
        number_of_tries = self.number_of_courts
        default_court = 'Crt3'
        self._fill_out_form_and_submit(default_court)
        self.driver.switch_to.active_element
        page_content = self.driver.page_source
        # print(page_content)
        text = 'The court you are trying to reserve is not available for the date and time you selected. There are no open courts.'
        # text = 'There are no open courts'
        with open("Output.txt", "w") as text_file:
            text_file.write(page_content)
        text_found = re.search(text, page_content)
        if text_found:
            print('there is text')
        # print(text_found)
        # while number_of_tries > 0:
        # self.driver.quit()





def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    caswell_username = config.get('LOGIN_INFO', 'USERNAME')
    caswell_password = config.get('LOGIN_INFO', 'PASSWORD')

    tomorrow = pd.to_datetime('today') + pd.DateOffset(days=1)
    tomorrow = tomorrow.replace(hour=19, minute=30)

    #TODO inputs need to either be 00 or 30 for minutes

    caswell = Caswell(tomorrow, 'singles', caswell_username, caswell_password)
    caswell.create_driver()
    caswell.login_to_caswell()
    #TODO need to write retry here if it isnt time yet, account for lag etc
    caswell.go_to_courtsheet()

    caswell.go_to_form()

    caswell.try_to_book()
    # t = webdriver.Firefox()
    # t.find_element_by_class_name()
    # if we just iterate down after the courts dont work it should work

    # el = driver.find_element_by_xpath('//*[@id="calendar"]/div/div/div/div/div/table/tbody/tr[1]/td/div')
    # action = webdriver.common.action_chains.ActionChains(driver)
    # action.move_to_element_with_offset(el, 0 * pixel_court_distance + 75, 0).click().perform()
    #
    # try:
    #     el2 = driver.find_element_by_xpath('//*[@id="ui-id-1"]')
    #     if el2.txt == 'Reserved':
    #         pass
    #         # need to try again
    #         # will need to put this in a different order
    # except common.exceptions.NoSuchElementException:
    #     # print(driver.current_url)
    #     # content_box = driver.find_element_by_class_name("content-box-content")
    #     driver.get('https://www.10sportal.net/entity/scheduler/index.html')
    #     mode_select = Select(driver.find_element_by_name("listMatchTypeID"))
    #     mode_select.select_by_value("1")
    #     # value "2" = doubles; value "1" = singles
    #
    #     start_time = driver.find_element_by_id("startTime")
    #     end_time = driver.find_element_by_id("endTime")
    #     start_time.clear()
    #     end_time.clear()
    #     start_time.send_keys("11:30 AM")
    #     end_time.send_keys("1:00 PM")
    #
    #     select = Select(driver.find_element_by_name("court"))
    #     select.deselect_all()
    #     select.select_by_value("229")
    #
    #     driver.find_element_by_name("submit").click()

        # this will let us know to keep going, can also parcse this to get to the next court (Crt 6 is open.)
        # text = 'The court you are trying to reserve is not available for the date and time you selected.'
        # if text in driver.page_source:
        #     print('hey')


if __name__ == '__main__':
    main()
