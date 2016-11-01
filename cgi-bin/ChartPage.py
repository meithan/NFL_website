#!/usr/bin/env python

# Generates the Rules page
import cgi, cgitb
cgitb.enable()
from common import *

# ==================================================

# Puntos Totales
def Graph1(logged_user, maxweek):

    if logged_user != None: logged_user = logged_user.Username

    print '<script type="text/javascript">'
    print "$(function () {"
    print "$('#chart').highcharts({"

    print "title: {"
    print "text: ''"
    #print "text: 'Puntos Totales por Jugador',"
    #print "x: -20 //center"
    print "},"

    #print "subtitle: {"
    #print "text: 'Puntos Totales por Jugador',"
    #print "x: -20"
    #print "},"

    print "xAxis: {"
    print "title: {"
    print "text: 'Semana'"
    print "},"

    buffer = "categories: ["
    for i in range(maxweek+1):
      if i!=0: buffer += ", "
      if i==0: buffer += "'Inicio'"
      else: buffer += "'%i'" % (i)
    buffer += "]"
    print buffer

    print "},"

    print "yAxis: {"
    print "title: {"
    print "text: 'Puntos Totales'"
    print "},"

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
    print "hideDelay: 100,"
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
      if i>4 and p.Username != logged_user: buffer += "\nvisible: false,"
      buffer += "\ndata: ["
      for w in range(maxweek+1):
        if w == 0: buffer += "0"
        else: buffer += "%i" % (p.TotalPoints[w-1])
        if w < maxweek: buffer += ", "
      buffer += "]"
      if i < len(Players)-1: buffer += "\n}, {"
    buffer += "\n}]"
    print buffer

    print "});"
    print "});"
    print "</script>"

# --------------------------

# Diferencia con el lider
def Graph2(logged_user, maxweek):

    if logged_user != None: logged_user = logged_user.Username

    print '<script type="text/javascript">'
    print "$(function () {"
    print "$('#chart').highcharts({"

    print "title: {"
    print "text: ''"
    #print "text: 'Diferencia de Puntos con el L\u00EDder',"
    #print "x: -20 //center"
    print "},"

    #print "subtitle: {"
    #print "text: 'Puntos Totales por Jugador',"
    #print "x: -20"
    #print "},"

    print "xAxis: {"
    print "title: {"
    print "text: 'Semana'"
    print "},"

    buffer = "categories: ["
    for i in range(maxweek+1):
      if i!=0: buffer += ", "
      if i==0: buffer += "'Inicio'"
      else: buffer += "'%i'" % (i)
    buffer += "]"
    print buffer

    print "},"

    print "yAxis: {"
    print "title: {"
    print "text: 'Diferencia de Puntos'"
    print "},"

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
      if i>4 and p.Username != logged_user: buffer += "\nvisible: false,"
      buffer += "\ndata: ["
      for w in range(maxweek+1):
        if w == 0: buffer += "0"
        else: buffer += "%i" % (p.ScoreDiffs[w-1])
        if w < maxweek: buffer += ", "
      buffer += "]"
      if i < len(Players)-1: buffer += "\n}, {"
    buffer += "\n}]"
    print buffer

    print "});"
    print "});"
    print "</script>"

# ==================================================
# SHOW PAGE

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
    show = form["show"].value
else:
    show = "1"

# For Graph2, Compute score differences to leader
if show == "2":
    for p in Players: p.ScoreDiffs = [0]*17
    for i in range(17):
        top_score = 0
        for p in Players:
            if p.TotalPoints[i] > top_score: top_score = p.TotalPoints[i]
        for p in Players:
            p.ScoreDiffs[i] = p.TotalPoints[i] - top_score

# --------------------------

print '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>'
print '<script src="/NFL%i/js/bootstrap.min.js"></script>' % (season)

if show == "1": Graph1(logged_user, cur_week)
elif show == "2": Graph2(logged_user, cur_week)

print '</head>'
print '<body>'

bootstrapNavbar("Chart",logged_user)

print '<div class="container">'

print '<br>'
print '<div style="text-align: center;">'
if show == "1":
    print '<h4>Tipo de Gr&aacute;fica: <strong>Puntos Totales</strong> | <a href="/NFL%i/cgi-bin/ChartPage.py?show=2">Diferencia de Puntos</a></h4>' % (season)
elif show == "2":
    print '<h4>Tipo de Gr&aacute;fica: <a href="/NFL%i/cgi-bin/ChartPage.py?show=1">Puntos Totales</a> | <strong>Diferencia de Puntos</strong> </h4>' % (season)
print '</div>'

print '<script src="/NFL%i/js/highcharts.js"></script>' % (season)
print '<script src="/NFL%i/js/exporting.js"></script>' % (season)
print '<div id="chart" style="min-width: 310px; height: 600px; margin: 0 auto"></div>'

print '</div>'

print '</body>'
print '</html>'