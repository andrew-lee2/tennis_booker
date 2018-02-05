import configparser
from selenium import webdriver, common
import pandas as pd
from selenium.webdriver.support.ui import Select


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    username = config.get('LOGIN_INFO', 'USERNAME')
    password = config.get('LOGIN_INFO', 'PASSWORD')

    tomorrow = pd.to_datetime('today') + pd.DateOffset(days=1)
    tomorrow_str = tomorrow.strftime('%m/%d/%Y')

    driver = webdriver.Firefox()
    login_url = 'https://www.10sportal.net/login.html'
    base_calendar_url = 'https://www.10sportal.net/entity/dashboard/index.html?src=resourceView&lvDate={date}'
    schedule_url = base_calendar_url.format(date=tomorrow_str)
    driver.get(login_url)

    username_input = driver.find_element_by_id("j_username")
    password_input = driver.find_element_by_id("j_password")

    username_input.send_keys(username)
    password_input.send_keys(password)

    driver.find_element_by_xpath('//*[@id="form-login"]/button').click()

    driver.get(schedule_url)

    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # time.sleep(0.5)
    # we are going to offset from
    # // *[ @ id = "calendar"] / div / div / div / div / div / table / tbody / tr[1] / td / div
    # // *[ @ id = "calendar"] / div / div / div / div / div / table / tbody / tr[2] / th
    # // *[ @ id = "calendar"] / div / div / div / div / div / table / tbody / tr[28] / th
    # if we just iterate down after the courts dont work it should work
    pixel_court_distance = 95

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
