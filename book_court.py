import configparser
from selenium import webdriver, common
import pandas as pd
from selenium.webdriver.support.ui import Select


class Caswell(object):
    def __init__(self, booking_day_datetime, singles_or_doubles, username, password):
        self.booking_day_datetime = booking_day_datetime
        self.singles_or_doubles = singles_or_doubles
        self.username = username
        self.password = password
        self.driver = None

    def select_driver(self):
        # TODO will do this later depending on local or not
        self.driver = webdriver.Firefox()

    def get_login_date(self):
        return self.booking_day_datetime.strftime('%m/%d/%Y')

    def get_start_time(self):
        start_time = self.booking_day_datetime.strftime('%I:%M %p')
        start_time = start_time[1:] if start_time[0] == '0' else start_time
        return start_time

    def get_courtsheet_time_bucket(self):
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
        booking_date = self.get_login_date()
        base_calendar_url = 'https://www.10sportal.net/entity/dashboard/index.html?src=resourceView&lvDate={date}'
        courtsheet_day_url = base_calendar_url.format(date=booking_date)
        self.driver.get(courtsheet_day_url)

    def try_to_click_courtsheet(self):
        pixel_court_distance = 95
        click_time_bucket = self.get_courtsheet_time_bucket()
        bucket_xpath = '//*[@id="calendar"]/div/div/div/div/div/table/tbody/tr[{bucket}]/td/div'
        bucket_xpath = bucket_xpath.format(bucket=click_time_bucket)

        action = webdriver.common.action_chains.ActionChains(self.driver)

        max_number_of_tries = 20

        while max_number_of_tries > 0:
            bucket_element = self.driver.find_element_by_xpath(bucket_xpath)
            action.move_to_element_with_offset(bucket_element, 0 * pixel_court_distance + 75, 0).click().perform()
            try:
                reserved_title_xpath = '//*[@id="ui-id-1"]'
                reserved_element = self.driver.find_element_by_xpath(reserved_title_xpath)
                if reserved_element.txt == 'Reserved':
                    # TODO need to update the courts / buckets
                    pass

            except common.exceptions.NoSuchElementException:
                submit_url_form = 'https://www.10sportal.net/entity/scheduler/index.html'
                self.driver.get(submit_url_form)
                break

    def fill_out_form(self):
        pass

    def try_to_book(self):
        pass


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    caswell_username = config.get('LOGIN_INFO', 'USERNAME')
    caswell_password = config.get('LOGIN_INFO', 'PASSWORD')

    tomorrow = pd.to_datetime('today') + pd.DateOffset(days=1)
    tomorrow = tomorrow.replace(hour=19, minute=30)

    #TODO inputs need to either be 00 or 30 for minutes

    caswell = Caswell(tomorrow, 'singles', caswell_username, caswell_password)
    caswell.select_driver()
    print(tomorrow.hour)
    # caswell.login_to_caswell()
    #
    # caswell.go_to_courtsheet()

    # if we just iterate down after the courts dont work it should work


    el = driver.find_element_by_xpath('//*[@id="calendar"]/div/div/div/div/div/table/tbody/tr[1]/td/div')
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(el, 0 * pixel_court_distance + 75, 0).click().perform()

    try:
        el2 = driver.find_element_by_xpath('//*[@id="ui-id-1"]')
        if el2.txt == 'Reserved':
            pass
            # need to try again
            # will need to put this in a different order
    except common.exceptions.NoSuchElementException:
        # print(driver.current_url)
        # content_box = driver.find_element_by_class_name("content-box-content")
        driver.get('https://www.10sportal.net/entity/scheduler/index.html')
        mode_select = Select(driver.find_element_by_name("listMatchTypeID"))
        mode_select.select_by_value("1")
        # value "2" = doubles; value "1" = singles

        start_time = driver.find_element_by_id("startTime")
        end_time = driver.find_element_by_id("endTime")
        start_time.clear()
        end_time.clear()
        start_time.send_keys("11:30 AM")
        end_time.send_keys("1:00 PM")

        select = Select(driver.find_element_by_name("court"))
        select.deselect_all()
        select.select_by_value("229")

        driver.find_element_by_name("submit").click()

        # this will let us know to keep going, can also parcse this to get to the next court (Crt 6 is open.)
        text = 'The court you are trying to reserve is not available for the date and time you selected.'
        if text in driver.page_source:
            print('hey')
    # Crt1 - "226"
    # Crt8 - "233"


    # the time slots just appear to have the name fc-slotx
    # x from 0 to 27 based on the time of day starting from 8 am

if __name__ == '__main__':
    main()
