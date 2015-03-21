import webapp2
from google.appengine.api import urlfetch


class WeatherQuery():
    QUERY_URL="https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource={}&requestType=retrieve&format=csv&stationString={}&hoursBeforeNow={}"
    def query_weather(self, ident, wxtype, hours=1):
        result = urlfetch.fetch(WeatherQuery.QUERY_URL.format(wxtype, ident, hours))
        if result.status_code != 200:
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
        lines = result.content.splitlines()
        if len(lines) < 7:
            logging.info("No results for {} in past {} hours".format(ident, hours))
            return None
        return [l.split(',')[:3] for l in lines[6:]]

    def query_metars(self, ident, hours=1):
        return self.query_weather(ident, 'metars', hours)

    def query_tafs(self, ident, hours=1):
        return self.query_weather(ident, 'tafs', hours)


class ShowForm(webapp2.RequestHandler):
    MAIN_PAGE_HTML = """\
    <html>
      <body>
        <p>Enter an identifier:</p>
        <form action="/submit" method="get">
          <div><input name="ident" rows="1" cols="10"></input></div>
          <div><input type="submit" value="ident"></div>
        </form>
      </body>
    </html>
    """

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(ShowForm.MAIN_PAGE_HTML)
    

class SubmitHandler(webapp2.RequestHandler):
    def get(self):
        ident = self.request.get('ident')
        for metar in WeatherQuery().query_metars(ident):
            self.response.write(metar)
            self.response.write('<br>')
        for taf in WeatherQuery().query_tafs(ident):
            self.response.write(taf)
            self.response.write('<br>')

application = webapp2.WSGIApplication([
    ('/', ShowForm),
    ('/submit', SubmitHandler),
], debug=True)
