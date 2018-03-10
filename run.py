# /usr/bin/env python
from flask import Flask, request
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os
from tennis_booker.court_booker.book_court import run_booker
from tennis_booker.message_parser.parser import Parser
# from selenium import webdriver
import pandas as pd
import psycopg2
import logging


app = Flask(__name__)

logging.basicConfig()

postgres_url = os.environ['DATABASE_URL']
jobstores = {
    'default': SQLAlchemyJobStore(url=postgres_url)
}

scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()


@app.route('/')
def home():
    # now = pd.to_datetime('now')
    # TODO could turn this into a parser to return scheds
    url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(url, sslmode='require')
    temp = pd.read_sql_query('select * from "apscheduler_jobs"', con=conn)
    print(temp)
    conn.close()
    return '{}'.format(url)


@app.route("/sms", methods=['GET', 'POST'])
def sms_parse():
    message_number = request.form['From']
    message_body = request.form['Body']

    message_parser = Parser(message_body)
    book_now = message_parser.to_book_now()
    booking_dt = message_parser.booking_time
    match_type = message_parser.game_type
    playing_time = message_parser.playing_time
    cas_user, cas_pw = get_tennis_creds()
    chromedriver_path = get_chromedriver_path()
    twilio_user, twilio_pw = get_twilio_creds()

    booker_args = [playing_time, match_type, cas_user, cas_pw, chromedriver_path,
                   twilio_user, twilio_pw, message_number]

    if book_now:
        send_response(message_number, 'trying to book')
        # TODO make we just make the scheduler run right now?
        booking_dt = pd.to_datetime('now') + pd.DateOffset(seconds=5)
        # booking_dt = booking_dt.astimezone('UTC')
        # booking_dt = booking_dt.isoformat()
        print('BOOKING_TIME {}'.format(booking_dt))

        scheduler.add_job(run_booker, 'date', run_date=booking_dt, args=booker_args)
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
        response_str = 'Ran for {}'.format(playing_time)
    else:
        if message_parser.booking_time:
            scheduler.add_job(run_booker, 'date', run_date=booking_dt, args=booker_args)
            response_str = 'Scheduled to run on {} for {}'.format(booking_dt, playing_time)
        else:
            response_str = 'Error: needs to be in MM/DD/YYYY HH:MM PM/AM singles/doubles format'

    send_response(message_number, response_str)

    return 'finished'


def get_twilio_creds():
    twilio_sid = os.environ.get('TWILIO_SID', None)
    twilio_token_auth = os.environ.get('TWILIO_AUTH', None)
    return twilio_sid, twilio_token_auth


def send_response(return_number, message_response):
    send_back_num = return_number
    # TODO need to cache twilio auth
    twilio_sid, twilio_token_auth = get_twilio_creds()
    client = Client(twilio_sid, twilio_token_auth)

    client.api.account.messages.create(
        to=send_back_num,
        from_="+12349013540",
        body=message_response)


def get_tennis_creds():
    try:
        caswell_username = os.environ.get('CASWELL_USER', None)
        caswell_password = os.environ.get('CASWELL_PW', None)
    except:
        import configparser
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), r'config.ini'))

        caswell_username = config.get('LOGIN_INFO', 'USERNAME')
        caswell_password = config.get('LOGIN_INFO', 'PASSWORD')

    return caswell_username, caswell_password


def get_chromedriver_path():
    try:
        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # chromedriver_path = os.environ.get('CHROME_PATH', None)
        # options.binary_location = chromedriver_path
        # return webdriver.Chrome(executable_path="chromedriver", chrome_options=options)
        return os.environ.get('CHROME_PATH', None)
    except:
        return '/Users/andrewlee/Downloads/chromedriver'



if __name__ == "__main__":
    app.run()
