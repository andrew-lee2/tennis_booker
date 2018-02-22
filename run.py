# /usr/bin/env python
from flask import Flask, request
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import os
from tennis_booker.court_booker.book_court import run_booker
from tennis_booker.message_parser.parser import Parser


app = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.start()


@app.route('/')
def home():
    return "display_test"


@app.route("/sms", methods=['GET', 'POST'])
def sms_parse():
    message_number = request.form['From']
    message_body = request.form['Body']

    message_parser = Parser(message_body)
    book_now = message_parser.to_book_now()
    booking_dt = message_parser.booking_time
    match_type = message_parser.game_type
    playing_time = message_parser.playing_time

    if book_now:
        run_booker(playing_time, match_type)
        response_str = 'Ran for {}'.format(playing_time)
    else:
        if message_parser.booking_time:
            scheduler.add_job(run_booker, 'date', run_date=booking_dt, args=[playing_time, match_type])
            response_str = 'Scheduled to run on {} for {}'.format(booking_dt, playing_time)
        else:
            response_str = 'Error: needs to be in DD/MM/YYYY HH:MM PM/AM singles/doubles format'

    send_response(message_number, response_str)

    return "recorded"


def send_response(return_number, message_response):
    send_back_num = return_number

    twilio_sid = os.environ.get('TWILIO_SID', None)
    twilio_token_auth = os.environ.get('TWILIO_AUTH', None)
    client = Client(twilio_sid, twilio_token_auth)
    # eventually need to change the resp to sending messages properly
    # now = pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S")
    # message_txt = 'Texting you back at {}'.format(now)

    client.api.account.messages.create(
        to=send_back_num,
        from_="+12349013540",
        body=message_response)


if __name__ == "__main__":
    # app.run(debug=True)
    app.run()
