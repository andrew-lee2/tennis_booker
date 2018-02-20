# /usr/bin/env python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd
from datetime import datetime, timedelta


app = Flask(__name__)

scheduler = BlockingScheduler()
scheduler.start()

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
    alarm_time = datetime.now() + timedelta(minutes=2)
    scheduler.add_job(send_response, 'date', run_date=alarm_time, args=[request])


def send_response(request):
    # eventually need to change the resp to sending messages properly
    now = pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S")
    request.message('Texting you back at {}'.format(now))


if __name__ == "__main__":
    app.run(debug=True)