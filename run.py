# /usr/bin/env python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.scheduler import Scheduler
import pandas as pd
from datetime import datetime, timedelta
import os


app = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/wakemydyno.txt')
def no_sleep():
    return "no sleep"

@app.route('/')
def home():
    return "display_test"

@app.route("/sms", methods=['GET', 'POST'])
def sms_parse():
    # number = request.form['From']
    # print number
    # message_body = request.form['Body']
    # print message_body
    # parser = MessageParser(message_body)
    """Respond to incoming messages with a friendly SMS."""
    # correct = parser.check_format()

    # Start our response
    # resp = MessagingResponse()
    # Add a message
    # resp.message('placeholder')
    message_num = request.form['From']
    alarm_time = datetime.now() + timedelta(minutes=2)

    scheduler.add_job(send_response, 'date', run_date=alarm_time, args=[message_num])

    return "recorded"


def send_response(message):
    send_back_num = message

    twilio_sid = os.environ.get('TWILIO_SID', None)
    twilio_token_auth = os.environ.get('TWILIO_AUTH', None)
    client = Client(twilio_sid, twilio_token_auth)
    # eventually need to change the resp to sending messages properly
    now = pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S")
    message_txt = 'Texting you back at {}'.format(now)

    client.api.account.messages.create(
        to=send_back_num,
        from_="+12349013540",
        body=message_txt)


if __name__ == "__main__":
    # app.run(debug=True)
    app.run()
