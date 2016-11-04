#!/usr/bin/env python

# Generates the Rules page
import cgi, cgitb
cgitb.enable()
from common import *

# ==================================================

# Colors
color_wheel = ["434348", "90ED7D", "F7A35C", "8085E9", "F15C80", "8D4653", "91E8E1", "7CB5EC"]

# Marker symbols
symbols_wheel = ["circle", "square", "diamond", "triangle", "triangle-down"]

# --------------------------

# HTML header
print "Content-type:text/html\r\n\r\n"
print '<!DOCTYPE html>'
print '<html lang="en">'
print '<title>Quiniela NFL %i</title>' % (season)
print '<head>'
bootstrapHeader()

# --------------------------

# Get current date (timezone aware)
now = get_utcnow()

# Get current week from current date
cur_week = getCurrentWeek(now)

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# Load stuff
db = DBHelper()
db.Connect()
Teams = db.loadTeams()
Players = db.loadPlayers()
for p in Players: p.loadScores()
numPlayers = len(Players)
db.Close()

Players = sorted(Players, key=lambda x: x.Username.lower())
Players = sorted(Players, key=lambda x: x.GlobalScore, reverse=True)

# Compute *cumulative* week points
for p in Players:
    sum = 0
    p.TotalPoints = [0]*17
    for i in range(17):
        sum += p.WeekPoints[i]
        p.TotalPoints[i] = + sum

# Get graph type from passed cgi parameters
form = cgi.FieldStorage()
if form.has_key("show"):
    graph_type = int(form["show"].value)
else:
    graph_type = 1

# For Graph2, Compute score differences to leader
if graph_type == 2:
    for p in Players: p.ScoreDiffs = [0]*17
    for i in range(17):
        top_score = 0
        for p in Players:
            if p.TotalPoints[i] > top_score: top_score = p.TotalPoints[i]
        for p in Players:
            p.ScoreDiffs[i] = p.TotalPoints[i] - top_score

# For Graph3, compute weekly ranks
if graph_type == 3:
    for p in Players: p.WeekRanks = [1]*17
    for w in range(17):
        Players.sort(key=lambda x: x.TotalPoints[w], reverse=True)
        lastrank = 1
        for i in range(len(Players)):
            if i == 0:
                Players[i].WeekRanks[w] = 1
            else:
                if Players[i].TotalPoints[w] == Players[i-1].TotalPoints[w]:
                    Players[i].WeekRanks[w] = lastrank
                else:
                    Players[i].WeekRanks[w] = i+1
                    lastrank = i+1

# --------------------------

print '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>'
print '<script src="/NFL%i/js/bootstrap.min.js"></script>' % (season)

# --------------------------

# Create graph

print '<script type="text/javascript">'
print "$(function () {"
print "$('#chart').highcharts({"

print "title: {"
print "text: ''"
print "},"

print "xAxis: {"
print "title: {"
print "text: 'Semana'"
print "},"

buffer = "categories: ["
for i in range(cur_week+1):
  if i != 0: buffer += ", "
  if i == 0: buffer += "'Inicio'"
  else: buffer += "'%i'" % (i)
buffer += "]"
print buffer

print "},"

print "yAxis: {"
print "title: {"
if graph_type   == 1: ylabel = "Puntos Totales"
elif graph_type == 2: ylabel = "Diferencia de Puntos"
elif graph_type == 3: ylabel = "Posicion Global"
print 'text: "%s"' % ylabel
print "},"

if graph_type == 2:
  print "max: 0.9,"
  print "tickInterval: 1,"
  print "startOnTick: false,"

if graph_type == 3:
#  print "tickInterval: 5,"
  print "tickPositions: [1, 5, 10, 15, 20, 25, 30],"
  print "reversed: true,"
  print "min: -1,"
  print "startOnTick: false,"

if graph_type != 3:
  print "plotLines: [{"
  print "value: 0,"
  print "width: 1,"
  print "color: '#808080'"
  print "}]"

print "},"

print "plotOptions: {series: {stickyTracking: false}},"

print "tooltip: {"
print "crosshairs: [true, true],"
print "shared: false,"
print "snap: 2,"
print "followPointer: false,"
print "hideDelay: 250,"
print "valueSuffix: ''"
print "},"

print "legend: {"
print "layout: 'vertical',"
print "align: 'right',"
print "verticalAlign: 'middle',"
print "borderWidth: 0"
print "},"

buffer = "series: [{"
for i,p in enumerate(Players):
  buffer += "\nname: '%s'," % (p.Username)
  if i > 4 and (logged_user == None or p.Username != logged_user.Username): buffer += "\nvisible: false,"
  buffer += "\ndata: ["
  for w in range(cur_week+1):
    if w == 0: buffer += "1" if graph_type == 3 else "0"
    else:
      if graph_type   == 1: buffer += "%i" % (p.TotalPoints[w-1])
      elif graph_type == 2: buffer += "%i" % (p.ScoreDiffs[w-1])
      elif graph_type == 3: buffer += "%i" % (p.WeekRanks[w-1])
    if w < cur_week: buffer += ", "
  buffer += "],"
  buffer += '\ncolor: "#%s",' % color_wheel[i%len(color_wheel)]
  buffer += '\nmarker:  {symbol: "%s"}' % symbols_wheel[i%len(symbols_wheel)]
  if i < len(Players)-1: buffer += "\n}, {"
buffer += "\n}]"
print buffer

print "});"
print "});"
print "</script>"

# --------------------------

print '</head>'
print '<body>'

bootstrapNavbar("Chart",logged_user)

print '<div class="container">'
print '<br>'
print '<div style="text-align: center;">'
print '<h4>Tipo de Gr&aacute;fica: '
graph_names = ["Puntos Totales", "Diferencia de Puntos", "Posici&oacute;n Global"]
buffer = ""
for i in range(3):
  if (i+1) == graph_type: buffer += "<strong>"
  else: buffer += '<a href="/NFL%i/cgi-bin/ChartPage.py?show=%i">' % (season, i+1)
  buffer += graph_names[i]
  if (i+1) == graph_type: buffer += "</strong>"
  else: buffer += '</a>'
  if i != 2: buffer += " | "
print buffer
print '</div>'

print '<script src="/NFL%i/js/highcharts.js"></script>' % (season)
print '<script src="/NFL%i/js/exporting.js"></script>' % (season)
print '<div id="chart" style="min-width: 310px; height: 600px; margin: 0 auto"></div>'

print '</div>'

print '</body>'
print '</html>'