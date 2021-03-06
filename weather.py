import webapp2
import logging
from google.appengine.api import urlfetch
from datetime import datetime


class WeatherQuery():

    TIME_FORMAT='%Y-%m-%dT%H:%M:%SZ'
    QUERY_URL='https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource={}&requestType=retrieve&format=csv&stationString={}&hoursBeforeNow={}'

    def query_weather(self, ident, report_type, hours=1):
        result = urlfetch.fetch(WeatherQuery.QUERY_URL.format(report_type, ident, hours))
        if result.status_code != 200:
            logging.error("Error querying for {}/{}/{} hours".format(ident, report_type, hours))
            logging.error(result.content)
            return None

        """ 
        There are 5 lines of header information that come back, then a
        header row, then the results (one per line) e.g:
            No errors
            No warnings
            2 ms
            data source=metars
            0 results
            <header>
        """
        logging.debug(result.content)
        lines = result.content.splitlines()
        if len(lines) < 7:
            logging.info("No results for {} in past {} hours".format(ident, hours))
            return []
        return [self.parse_line(l) for l in lines[6:]]

    def parse_line(self, line):
        items = line.split(',')[:3] 
        items[2] = datetime.strptime(items[2], self.TIME_FORMAT)
        return items

    def query_metars(self, ident, hours=None):
        hours = 4 if hours == None else hours
        return self.query_weather(ident, ReportType.METAR, hours)

    def query_tafs(self, ident, hours=None):
        hours = 4 if hours == None else hours
        return self.query_weather(ident, ReportType.TAF, hours)


class ReportType():
    TAF = 'tafs'
    METAR = 'metars'


class TafView(webapp2.RequestHandler):
    def get(self, ident):
        for taf in WeatherQuery().query_tafs(ident):
            self.response.write(taf)
            self.response.write('<br>')


class MetarView(webapp2.RequestHandler):
    def get(self, ident, hours):
        for metar in WeatherQuery().query_metars(ident, hours):
            self.response.write(metar)
            self.response.write('<br>')


application = webapp2.WSGIApplication([
    ('/(.*)/taf', TafView),
    ('/(.*)/metar(?:/([0-9]*))?', MetarView),
], debug=True)
