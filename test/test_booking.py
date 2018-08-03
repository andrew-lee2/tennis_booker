from tennis_booker.court_booker.book_court import run_booker
import pandas as pd


booking_dt = pd.to_datetime('2018-08-07 16:00:00')
match_type = 'singles'
username = ''
password = ''
driver = '/home/andrew/Downloads/chromedriver'
return_number = ''
book_now = True



def test_run_booker():
    run_booker(booking_dt, match_type, username, password, driver, return_number, book_now)


if __name__ == '__main__':
    test_run_booker()