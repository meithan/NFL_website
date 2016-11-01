#!/usr/bin/env python

# Generates the Standings Page (with a detail of scoring for everybody)
import cgi, cgitb
cgitb.enable()
from common import *
         
# --------------------------------

# Get current date (timezone aware)
now = get_utcnow()

# Get current week
week = getCurrentWeek(now)

# Connect to MySQL database
db = DBHelper()
db.Connect()

# Load Players from DB
Players = db.loadPlayers()
for p in Players:
    p.loadScores()
numPlayers = len(Players)

db.Close()

# --------------------------------
# Generate Standings Page
# Build HTML document
print "Content-type:text/html\r\n\r\n"
print '<!DOCTYPE html>'
print '<html lang="en">'

# Header
print '<head>'
bootstrapHeader()
print '<title>Quiniela NFL %i</title>' % (season)
print '</head>'

# Body start
print '<body>'

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# Navbar
bootstrapNavbar("Standings",logged_user)

# --- DEBUG AREA ---

# ------------------

# Page layout
print
print '<div class="container">'

# Page body title
print '<h2>Tabla de Posiciones</h2>'

# Standings table
print '<br>'
print '<div class="table-responsive">'
print '<table class="table table-bordered table-hover table-striped table-condensed main-table">'

# Table Header
print '<thead>'
print '<tr>'
print '<td class="header" colspan="2">Pos</td>'
print '<td class="header" style="text-align: left;">Jugador</td>'
print '<td class="header">Global</td>'
print '<td class="header">Dif</td>'
print '<td class="header">%</td>'
print '<td class="header"><a data-toggle="tooltip" data-html="true" title="Probabilidad de obtener un marcador global <em>igual o mejor</em> jugando al azar" data-placement="top" style="text-decoration: none;" class="legend-tooltip">Azar</a></td>'
for i in range(17):
    link = "/NFL%i/cgi-bin/MainPage.py?week=%i" % (season, i+1)
    print '<td class="header"><a href="%s">W%i</a></td>' % (link, i+1)
print '</tr>'
print '</thead>'

# Sort players first by global score, then alphabetically
Players = sorted(Players, key=lambda x: x.Username.lower())
Players = sorted(Players, key=lambda x: x.GlobalScore, reverse=True)
if len(Players) > 0: leaderScore = Players[0].GlobalScore
else: leaderScore = 0

# Table Body
print '<tbody>'
for i,p in enumerate(Players):
    if p.GlobalRank < p.PrevRank:
        rank_icon = '<img src="/NFL%i/iconz/rank_up.png" style="vertical-align: middle;">' % (season)
    elif p.GlobalRank == p.PrevRank:
        rank_icon = '<img src="/NFL%i/iconz/rank_same.png" style="vertical-align: middle;">' % (season)
    else:
        rank_icon = '<img src="/NFL%i/iconz/rank_down.png" style="vertical-align: middle;">' % (season) 
    print '<tr>'
    print '<td><strong>%i</strong></small></td>' % (p.GlobalRank)
    print '<td>%s<small>(%i)</small></td>' % (rank_icon, p.PrevRank)
    print '<td style="text-align: left;"><a data-toggle="tooltip" title="%s" data-placement="top" style="text-decoration: none;">%s</a></td>' % (p.Fullname, p.Username)
    print '<td><strong>%i</strong>&ndash;%i</td>' % (p.GlobalScore, p.GlobalMisses)
#    print '<td><strong>%i</strong></td>' % (p.GlobalScore)
    if p.GlobalScore==leaderScore:
        print '<td>L&iacute;der</td>'
    else:
        print '<td>&minus;%i</td>' % (abs(p.GlobalScore-leaderScore))
    print '<td>%2.1f%%</td>' % (p.GlobalPercent*100)
    luck_prob = Luck(p.GlobalScore+p.GlobalMisses,0.5,p.GlobalScore)*100
    if luck_prob < 1.0:
        print '<td nowrap align="center">&lt;1%</td>'
    else:
        print '<td nowrap align="center">%.0f%%</td>' % (luck_prob)
    for i in range(17):
        if (i+1) <= week:
            if p.WeekPoints[i] == None or p.WeekMisses[i] == None:
                points = 0
                misses = 0
            else:
                points = p.WeekPoints[i]
                misses = p.WeekMisses[i]
            print '<td>%i&ndash;%i</td>' % (points, misses)
        else:
            print '<td>&mdash;</td>'
    print '</tr>'
print '</tbody>'

# Repeat table header
print '<thead>'
print '<tr>'
print '<td class="header" colspan="2">Pos</td>'
print '<td class="header" style="text-align: left;">Jugador</td>'
print '<td class="header">Global</td>'
print '<td class="header">Dif</td>'
print '<td class="header">%</td>'
print '<td class="header"><a data-toggle="tooltip" data-html="true" title="Probabilidad de obtener un marcador global <em>igual o mejor</em> jugando al azar" data-placement="top" style="text-decoration: none;" class="legend-tooltip">Azar</a></td>'
for i in range(17):
    link = "/NFL%i/cgi-bin/MainPage.py?week=%i" % (season, i+1)
    print '<td class="header"><a href="%s">W%i</a></td>' % (link, i+1)
print '</tr>'
print '</thead>'
print '</table>'
print '</div>'

print '</div><!--container-->'

bootstrapFooter()

print '</body>'
print '</html>'