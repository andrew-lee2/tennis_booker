# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_parse():
    number = request.form['From']
    # print number
    message_body = request.form['Body']
    # print message_body
    # parser = MessageParser(message_body)
    """Respond to incoming messages with a friendly SMS."""
    # correct = parser.check_format()

    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message('placeholder')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)