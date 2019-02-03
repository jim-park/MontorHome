
__author__ = "James Park"
__email__ = "jim@linuxnetworks.co.uk"
__license__ = "Apache License, Version 2.0"

from twisted.python.log import FileLogObserver
from twisted.python.logfile import DailyLogFile
from datetime import datetime

# Application base path
PATH = '/opt/mh/'


class MyFileLogObserver(FileLogObserver):

    def formatTime(self, when):
        """
        Format the given UTC value as a string representing that time in the
        local timezone.

        By default it's formatted as a ISO8601-like string (ISO8601 date and
        ISO8601 time separated by a space). It can be customized using the
        C{timeFormat} attribute, which will be used as input for the underlying
        L{datetime.datetime.strftime} call.

        BACKPORTED VERSION: and adding support for %z.

        @type when: C{int}
        @param when: POSIX (ie, UTC) timestamp for which to find the offset.

        @rtype: C{str}
        """
        tzOffset = -self.getTimezoneOffset(when)
        tzHour = abs(int(tzOffset / 60 / 60))
        tzMin = abs(int(tzOffset / 60 % 60))
        if tzOffset < 0:
            tzSign = '-'
        else:
            tzSign = '+'
        tz = "%s%02d%02d" % (tzSign, tzHour, tzMin)
        if self.timeFormat is not None:
            return datetime.fromtimestamp(when).strftime(self.timeFormat.replace("%z", tz))

        when = datetime.utcfromtimestamp(when + tzOffset)
        return '%d-%02d-%02d %02d:%02d:%02d%s%02d%02d' % (
                when.year, when.month, when.day,
                when.hour, when.minute, when.second,
                tzSign, tzHour, tzMin)


def mhlogger(name):
    logfile = DailyLogFile(name + '.log', PATH + 'log/')
    flo = MyFileLogObserver(logfile)
    # flo.timeFormat = "%Y-%m-%d %H:%M:%S %f%z"
    flo.timeFormat = "%Y-%m-%d %H:%M:%S"
    return flo.emit
