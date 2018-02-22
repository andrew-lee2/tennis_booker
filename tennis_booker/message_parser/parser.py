import re
import pandas as pd


class Parser(object):
    def __init__(self, message):
        self.message = message
        self.date = None
        self.time = None
        self.am_or_pm = None
        self.game_type = None
        self.booking_time = None
        self.playing_time = None

    def _check_format(self):
        # MM/DD/YYYY HH:MM AM or PM singles/doubles
        r = re.compile('\d{2}/\d{2}/\d{4} \d{2}:\d{2} ([AaPp][Mm]) (singles|doubles)')
        # TODO this is just the initial step, will need to do other checks later
        if r.match(self.message) is not None:
            return True
        else:
            return False

    def _split_message(self):
        # TODO I think we need to break this out into a "main" function
        # if self.check_format():
        message_parts = self.message.split(' ')
        self.date = message_parts[0]
        self.time = message_parts[1]
        self.am_or_pm = message_parts[2]
        self.game_type = message_parts[3]

    def _get_booking_time(self, playing_date):
        booking_time = playing_date - pd.DateOffset(days=2)
        self.booking_time = booking_time.replace(hours=8, minutes=43)
        # return self.booking_time

    def _book_now(self):
        now = pd.to_datetime('now')
        return True if now > self.booking_time else False

    def _get_date(self):
        full_date_str = self.date + self.time + self.am_or_pm
        self.playing_time = pd.to_datetime(full_date_str)

    def to_book_now(self):
        if self._check_format():
            self._split_message()
        else:
            # this prob isnt good
            return False
        # else:
            # we need to return the string here maybe we can just dervive with None
            # return None

        self._get_date()
        return self._book_now()
