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
        message_parts = self.message.split(' ')
        self.date = message_parts[0]
        self.time = message_parts[1]
        self.am_or_pm = message_parts[2]
        self.game_type = message_parts[3]

    def _get_booking_dt(self):
        booking_time = self.playing_time - pd.DateOffset(days=2)
        # FIXME move this earlier maybe
        self.booking_time = booking_time.replace(hour=8, minute=44, second=30)

    def _get_booking_utc(self):
        booking_time = self.booking_time.tz_localize('US/Central')
        booking_time = booking_time.astimezone('UTC')
        self.booking_time = booking_time.isoformat()

    def _book_now(self):
        now = pd.to_datetime('now')
        return True if now > self.booking_time else False

    def _get_date(self):
        full_date_str = '{} {} {}'.format(self.date, self.time, self.am_or_pm)
        # ValueError for wrong date
        self.playing_time = pd.to_datetime(full_date_str)

    def to_book_now(self):
        # TODO i think changing the response to this would be better
        if self._check_format():
            self._split_message()
        else:
            # TODO change this
            return False

        self._get_date()
        self._get_booking_dt()
        to_book = self._book_now()
        self._get_booking_utc()
        return to_book
