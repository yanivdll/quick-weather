#!/usr/bin/python

import json
import urllib
import time
from datetime import datetime
import cgi

# Functions #


def wunder(lat, lon, wukey):
    "Return a dictionary of weather data for the given location."

    # URLs
    baseURL = 'http://api.wunderground.com/api/%s/' % wukey
    dataURL = baseURL + \
        'conditions/astronomy/hourly/forecast/q/%f,%f.json' % (lat, lon)
    radarURL = baseURL + 'radar/image.png' \
                       + '?centerlat=%f&centerlon=%f' % (lat, lon - 1) \
                       + '&radius=100&width=480&height=360&timelabel=1' \
                       + '&timelabel.x=10&timelabel.y=350' \
                       + '&newmaps=1&noclutter=1'

    # Collect data.
    ca = urllib.urlopen(dataURL).read()
    j = json.loads(ca)
    current = j['current_observation']
    astro = j['moon_phase']
    hourly = j['hourly_forecast'][0:13:3]
    daily = j['forecast']['simpleforecast']['forecastday']

    # Turn sun rise and set times into dxatetimes.
    rise = '%s:%s' % (astro['sunrise']['hour'], astro['sunrise']['minute'])
    set = '%s:%s' % (astro['sunset']['hour'], astro['sunset']['minute'])
    sunrise = datetime.strptime(rise, '%H:%M')
    sunset = datetime.strptime(set, '%H:%M')

    # Mapping of pressure trend symbols to words.
    pstr = {'+': 'rising', '-': 'falling', '0': 'steady'}

    # Forecast for the next 12 hours.
    today = []
    for h in hourly:
        f = [h['FCTTIME']['civil'],
             h['condition'],
             h['temp']['english'] + '&deg;']
        today.append(f)

    # Forecasts for the next 2 days.
    d1 = daily[1]
    tomorrow = {'day': d1['date']['weekday'],
                'desc': d1['conditions'],
                'trange': '%s&deg; to %s&deg;' %
                (d1['low']['fahrenheit'], d1['high']['fahrenheit'])}
    d2 = daily[2]
    dayafter = {'day': d2['date']['weekday'],
                'desc': d2['conditions'],
                'trange': '%s&deg; to %s&deg;' %
                (d2['low']['fahrenheit'], d2['high']['fahrenheit'])}

    # Construct the dictionary and return it.
    wudata = {'pressure': float(current['pressure_in']),
              'ptrend': pstr[current['pressure_trend']],
              'temp': current['temp_f'],
              'desc': current['weather'],
              'wind_dir': current['wind_dir'],
              'wind': current['wind_mph'],
              'gust': float(current['wind_gust_mph']),
              'feel': float(current['feelslike_f']),
              'sunrise': sunrise,
              'sunset': sunset,
              'radar': radarURL,
              'today': today,
              'tomorrow': tomorrow,
              'dayafter': dayafter}
    return wudata


def wuHTML(lat, lon, wukey):
    "Return HTML with WU data for given location."

    d = wunder(lat, lon, wukey)

    # Get data ready for presentation
    sunrise = d['sunrise'].strftime('%-I:%M %p').lower()
    sunset = d['sunset'].strftime('%-I:%M %p').lower()
    temp = '%.0f&deg;' % d['temp']
    pressure = 'Pressure: %.2f and %s' % (d['pressure'], d['ptrend'])
    wind = 'Wind: %s at %.0f mph, gusting to %.0f mph' %\
           (d['wind_dir'], d['wind'], d['gust'])
    feel = 'Feels like: %.0f&deg;' % d['feel']
    sun = 'Sunlight: %s to %s' % (sunrise, sunset)
    htmplt = '<tr><td class="right">%s</td><td>%s</td>' +\
             '<td class="right">%s</td></tr>'
    hours = [htmplt % tuple(f) for f in d['today']]
    today = '\n'.join(hours)
    forecast1 = '<tr><td>%s</td><td>%s</td></tr>' %\
                (d['tomorrow']['desc'], d['tomorrow']['trange'])
    forecast2 = '<tr><td>%s</td><td>%s</td></tr>' %\
                (d['dayafter']['desc'], d['dayafter']['trange'])

    # Assemble the HTML.
    html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<meta name="viewport" content = "width = device-width" />
<title>Weather</title>
<style type="text/css">
  body { font-family: Helvetica; }
  p { margin-bottom: 0; }
  h1 { font-size: 175%%;
    text-align: center;
    margin-bottom: 0; }
  h2 { font-size: 125%%;
    margin-top: .5em ;
    margin-bottom: .25em; }
  td { padding-right: 1em;}
  td.right { text-align: right; }
  #now { margin-left: 0; }
  #gust { padding-left: 2.75em; }
  div p { margin-top: .25em;
    margin-left: .25em; }
</style>
</head>
<body onload="setTimeout(function() { window.top.scrollTo(0, 1) }, 100);">
  <h1>%s &bull; %s </h1>

  <p><img width="100%%" src="%s" /></p>

  <p id="now">%s<br />
  %s<br />
  %s<br />
  %s<br /></p>
  <h2>Today</h2>
  <table>
  %s
  </table>
  <h2>%s</h2>
  <table>
  %s
  </table>
  <h2>%s</h2>
  <table>
  %s
  </table>

</body>
</html>''' % (temp, d['desc'], d['radar'], wind, feel, pressure, sun, today, d['tomorrow']['day'], forecast1, d['dayafter']['day'], forecast2)

    return html


############################## Main program ###############################

# My Weather Underground key.
wukey = '7b1d7f2dda02088f'

# Get the latitude and longitude.
form = cgi.FieldStorage()
lat = 40.730610 #float(form.getvalue('lat'))
lon = -73.935242 #float(form.getvalue('lon'))

# Generate the HTML.
html = wuHTML(lat, lon, wukey)

print '''Content-Type: text/html

%s''' % html
