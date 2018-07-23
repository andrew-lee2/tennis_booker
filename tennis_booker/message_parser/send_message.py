from twilio.rest import Client
import os


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

    print('sending text - {}'.format(message_response))
