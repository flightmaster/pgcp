import webapp2
from google.appengine.api import urlfetch


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


QUERY_URL="https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=csv&stationString={}&hoursBeforeNow=1"

class ShowForm(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(MAIN_PAGE_HTML)
    
class SubmitHandler(webapp2.RequestHandler):
    def get(self):
        ident = self.request.get('ident')
        self.response.write('You entered ' + ident)
        self.response.write(self.query_weather(ident))

    def query_weather(self, ident):
        result = urlfetch.fetch(QUERY_URL.format(ident))
        if result.status_code == 200:
            return result.content
        return None


application = webapp2.WSGIApplication([
    ('/', ShowForm),
    ('/submit', SubmitHandler),
], debug=True)
