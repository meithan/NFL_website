#!/usr/bin/env python

# Generates the Main Page (with results and links to submit forms)
import cgi, cgitb
cgitb.enable()
from common import *
import subprocess
         
# --------------------------------

# Get current date and time (timezone aware)
now = get_utcnow()

# Get week to display from passed cgi parameters
# or get the week from the current date
form = cgi.FieldStorage()
if form.has_key("week"):
    week = int(form["week"].value)
else:
    week = getCurrentWeek(now)

# Connect to MySQL database
db = DBHelper()
db.Connect()

# Load stuff from DB
Teams = db.loadTeams()
Matches = db.loadMatches(week)
Players = db.loadPlayers()

# Poll live scores
errmsg = ""
try: pollLiveScores(Matches,week)
except Exception as e: errmsg = str(e)

# =================
# MATCH INFO MANUAL OVERRIDE
#for m in Matches:
#  if m.MatchID == "W1-CAR@DEN":
#    m.AwayScore = 10
#    m.HomeScore = 7
#    m.Status = "Final"
##    m.Status = "Q3 13:37"
#    m.PossTeam = ""
#    m.Redzone = False
#    m.Yardline = "DEN 40"
#    m.Down = 3
#    m.ToGo = 10
#  if m.MatchID == "W14-SF@CLE":
#    m.AwayScore = 33
#    m.HomeScore = 31
#    m.Status = "Q1 3:37"
#    m.PossTeam = "CLE"
#    m.Redzone = True
# =================

# Run auto-updater to keep DB up-to-date
autoUpdater(Matches, week)

# Load scores and forecasts (after possible match updates)
for p in Players:
    p.loadScores()
    p.loadForecasts(week)

db.Close()

# Sort players first by global score (descending), then alphabetically
Players = sorted(Players, key=lambda x: x.Username.lower(), reverse=False)
Players = sorted(Players, key=lambda x: x.GlobalScore, reverse=True)

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# If a user is logged in, remember his/her Player object
if logged_user != None:
    for idx,p in enumerate(Players):
        if p.Username == logged_user.Username:
            logged_player = p
            logged_list = [p]
else:
    logged_list = []

numPlayers = len(Players) + len(logged_list)

# --------------------------------
# Generate Main Game Results Page
# Build HTML document
print "Content-type:text/html"
print     # THIS BLANK LINE IS MANDATORY
print '<!DOCTYPE html>'
print '<html lang="en">'

# Header
print '<head>'
bootstrapHeader()
print '<title>Quiniela NFL %i</title>' % (season)
print '</head>'

# body
print '<body>'

# Navbar
bootstrapNavbar("Main",logged_user)

# ============= DEBUG AREA =============

#print "server naive:", datetime.datetime.now(), "<br>"
#print "utc naive:", datetime.datetime.utcnow(), "<br>"
#print "to serverTZ:", datetime.datetime.now(serverTZ), "<br>"
#print "to mexicoTZ:", datetime.datetime.now(mexicoTZ), "<br>"
#print "utc aware:", now, "<br>"

# ======================================

# Page layout

print
print '<div class="container-fluid">'
print '<div class="row-fluid">'

# Main page start

print '<div class="col-md-9 col-md-push-3">'

print '<h2>Quiniela NFL %i</h2>' % (season)

# Links to other weeks

count = 1
for w in range(1,17+1):
    if w not in [1,7,13]: print ' | '
    if (count==7): print '<br>'
    if (count==13): print '<br>'
    if (w==week): print 'Semana %i' % (w)
    else: print '<a href="/NFL%i/cgi-bin/MainPage.py?week=%i">Semana %i</a>' % (season, w, w)
    count += 1

#
# Winners
#
#print '<br>'
#print '<h3>La Quiniela NFL %i ha concluido</h3>' % (season)
#print '<strong>&iexcl;Felicidades a los ganadores!</strong>'
#print '<br><u>1er lugar</u>: Queka (l&iacute;der)'
#print '<br><u>2dos lugares</u>: alejandro (-3), esquivas (-3), moustache (-3)'
#print '<br>No hay tercer lugar'
#print '<br>Para recibir sus <a href="PrizesPage.py">premios</a>, por favor env&iacute;enme un correo con sus datos bancarios, de preferencia CLABE.'

# Week title
print '<br><h2>Semana %i</h2>' % (week)

# Forecast submit button
if (logged_user != None):
    print '<form class="form-horizontal" name="forecastsubmit" action="/NFL%i/cgi-bin/FCSubmitPage.py?week=%i" method="post">' % (season, week)
    print '<button type="submit" class="btn btn-primary">Cambiar Pron&oacute;sticos</button>'
    print '</form><br>'
else:
    print 'Inicia sesi&oacute;n para enviar tus pron&oacute;sticos.<br><br>'

# Byes
if week in week_byes:
    buf = 'Descansan: '
    teamIDs = week_byes[week]
    for i,team in enumerate(teamIDs):
        if i != 0: buf += ", "
        buf += Teams[team].Name
    print buf + "<br>"
else:
    print "Descansan: ninguno<br>"

# Matches table start

print '<div class="table-responsive"><table class="table table-bordered table-hover table-striped table-condensed main-table">'

# Table Header

print '<thead>'
print '<tr>'
print '<td class="header">#</td>'
print '<td class="header">Hora&#8224;</td>'
print '<td class="header" style="text-align: right;">Equipo Visitante</td>'
print '<td class="header">&nbsp;</td>'
print '<td class="header" style="text-align: left;">Equipo Local</td>'
print '<td class="header">Estado</td>'
print '<td class="header">Posici&oacute;n</td>'
print '<td class="header">Stats</td>'
# If a user is logged, add an extra border width to his/her column
for pidx,p in enumerate(logged_list + Players):
    if (logged_user != None and pidx == 0):
        special = 'border-left-width: 3px; border-right-width: 3px;'
    else:
        special = ''
    print '''<td class="header" style="%s"><a data-toggle="tooltip" title="%s" data-placement="top"
    style="text-decoration: none" class="name-tooltip">%s</a></td>''' % (special, p.Fullname.replace('"','&quot;'), p.Username)
print '</tr>'
print '</thead>'

# Table Body

print '<tbody>'
curdate = None
matchnum = 0

for m in Matches:

    # Get Mexico timezone at the time of the match (DST ends October 30th in 2016)
    mexicoTZ = getMexicoTZ(m.DateTime)

    # Date row
    mdate = m.DateTime.astimezone(mexicoTZ).date().isoformat()
    if (curdate != mdate):
        curdate = mdate
        datenice = m.DateTime.astimezone(mexicoTZ).strftime("%A %d de %B")
        datenice = spanishDateCorrection(datenice)
        print '<tr><td class="date success" colspan="%i"><strong>%s</strong></td></tr>' % (8+numPlayers, datenice)
  
    # Match details

    print '<tr>'
    matchnum += 1
    print '<td>%i</td>' % (matchnum)

    # Time
#    print '<td>%s</td>' % (m.DateTime.astimezone(mexicoTZ).strftime("%H:%M"))
    ampm = " am" if m.DateTime.astimezone(mexicoTZ).hour < 12 else " pm"
    print '<td>%s</td>' % ((m.DateTime.astimezone(mexicoTZ).strftime("%I:%M").lstrip("0") + ampm))

    # Away Team

    iconimg = '<img src="/NFL%i/iconz/%s.png">' % (season, Teams[m.AwayTeam].ID)
    away_td_classes = ["team1"]
    away_span_classes = []
    if m.isFinal() and m.getWinner() in [m.AwayTeam, "TIE"]:
        away_span_classes.append("winner")
    elif m.hasScore() and m.AwayScore > m.HomeScore:
        away_span_classes.append("winning")
    if m.PossTeam == m.AwayTeam:
        away_span_classes.append("possession")
        if m.Redzone:
            away_span_classes.append("redzone")
    if m.PossTeam == m.AwayTeam:
        away_poss_icon = '<img src="/NFL%i/iconz/smallfootball2.png">&nbsp;' % (season)
    else:
        away_poss_icon = ''
    print '<td class="%s"><span class="%s">%s%s %s</span>' % \
    (" ".join(away_td_classes), " ".join(away_span_classes), away_poss_icon, Teams[m.AwayTeam].City, Teams[m.AwayTeam].Name)
    print '%s</td>' % (iconimg)

    # Scores

    if m.Status == 'Pregame':
        print '<td>&mdash;</td>'
    elif not m.hasScore():
        print '<td>?</td>'
    else:
        if (m.AwayScore > m.HomeScore):
            print '<td><b>%s</b> &ndash; %s</td>' % (m.AwayScore, m.HomeScore)
        elif (m.AwayScore < m.HomeScore):
            print '<td>%s &ndash; <b>%s</b></td>' % (m.AwayScore, m.HomeScore)
        else:
            print '<td><b>%s</b> &ndash; <b>%s</b></td>' % (m.AwayScore, m.HomeScore)

    # Home Team

    iconimg = '<img src="/NFL%i/iconz/%s.png"> ' % (season, Teams[m.HomeTeam].ID)
    home_td_classes = ["team2"]
    home_span_classes = []
    if m.isFinal() and m.getWinner() in [m.HomeTeam, "TIE"]:
        home_span_classes.append("winner")
    elif m.hasScore() and m.HomeScore > m.AwayScore:
        home_span_classes.append("winning")
    if m.PossTeam == m.HomeTeam:
        home_span_classes.append("possession")
        if m.Redzone:
            home_span_classes.append("redzone")
    if m.PossTeam == m.HomeTeam:
        home_poss_icon = '&nbsp;<img src="/NFL%i/iconz/smallfootball2.png">' % (season)
    else:
        home_poss_icon = ''

    print '<td class="%s">%s' % (" ".join(home_td_classes), iconimg)
    print '<span class="%s">%s %s%s</span ></td>' % (" ".join(home_span_classes), Teams[m.HomeTeam].City, Teams[m.HomeTeam].Name, home_poss_icon)

    # Match status

    print '<td>%s</td>' % (m.Status)

    # Field position

    if m.Redzone:
        classes = ["redzone"]
    else:
        classes = []
    if m.Down != None and m.ToGo != None and m.Yardline != None:
        print '<td><span class="%s">%s</span>, %s</td>' % (" ".join(classes), m.Yardline, m.downString())
    else:
        print '<td>&mdash;</td>'

    # Stats tooltip

    if not m.pastStart():

        # Before game start, display the list of names of people who haven't submitted forecasts
        numpicks = 0
        missing = []
        for p in Players:
            if m.MatchID not in p.Forecasts: missing.append(p.Username)
        num_missing = len(missing)
        if num_missing==0:
            stats_tooltip = "Todos han enviado su pron&oacute;stico"
        else:
            missing = sorted(missing, key=lambda x: x.lower())
            if num_missing==1:
                stats_tooltip = "Falta <strong>1</strong> persona de enviar pron&oacute;stico:<br>"
            else:
                stats_tooltip = "Faltan <strong>%i</strong> personas de enviar pron&oacute;stico:<br>" % (num_missing)
            for k,name in enumerate(missing):
               if k!=0: stats_tooltip += ", "
               if logged_user != None and name == logged_user.Username:
                   stats_tooltip += "<span style='font-weight: bold; text-decoration: underline;'>%s</span>" % (name)
               else:
                   stats_tooltip += "%s" % (name)

    else:

        # Past game start, display pick stats
        ateam_picks = 0
        hteam_picks = 0
        no_picks = 0
        for p in Players:
            if m.MatchID not in p.Forecasts:
                no_picks += 1
            else:
                if p.Forecasts[m.MatchID] == m.AwayTeam: ateam_picks += 1
                elif p.Forecasts[m.MatchID] == m.HomeTeam: hteam_picks += 1

        # The following ensures the rounded percentages add up exactly to 100%
        sl = [[Teams[m.AwayTeam].Name, ateam_picks, 0.0]]
        sl.append([Teams[m.HomeTeam].Name, hteam_picks, 0.0])
        sl.append(["No envi&oacute;", no_picks, 0.0])
        sl = sorted(sl, key=lambda x: x[1], reverse=True)
        for idx in range(1,len(sl)):
            sl[idx][2] = int(round(sl[idx][1]*100.0/numPlayers))
        sl[0][2] = 100 - sl[1][2] - sl[2][2]

        stats_tooltip = ""
        for idx in range(0,len(sl)):
            if idx!=0: stats_tooltip += "<br>"
            if m.isFinal() and Teams[m.getWinner()].Name==sl[idx][0]:
                stats_tooltip += "<span style='text-decoration:underline;'>%s: <strong>%i</strong> (%i%%)</span>" % (sl[idx][0], sl[idx][1], sl[idx][2])
            else:
                stats_tooltip += "%s: <strong>%i</strong> (%i%%)" % (sl[idx][0], sl[idx][1], sl[idx][2])

    print '<td>'
    print '<a data-toggle="tooltip" title="%s" data-html="true" data-placement="right" style="text-decoration: none;" class="info-tooltip">' % (stats_tooltip)
    print '<span class="glyphicon glyphicon-info-sign" style="vertical-align: middle;"></span>'
    print '</a></td>'

    # Forecasts

    for pidx,p in enumerate(logged_list + Players):

        if (logged_user != None and pidx == 0):
            special = 'border-left-width: 3px; border-right-width: 3px;'
        else:
            special = ''

        # Get pick
        if m.MatchID in p.Forecasts: pick = p.Forecasts[m.MatchID]
        else: pick = None

        # If match has not started yet, print either ? (if pick submitted) or a dash
        if not m.pastStart():

            if pick != None:
                if (logged_user != None and p.Username == logged_user.Username):
                    print '<td style="%s"><a data-toggle="tooltip" title="%s" data-html="true" data-placement="right">?</a></td>' % (special, Teams[pick].Name)
                else:
                    print '<td>?</td>'
            else: 
                print '<td style="%s">&mdash;</td>' % special

        # If past match start ...
        else:

            # If match has final score, shade backgrounds appropriately
            if m.isFinal():

                if (m.getWinner() == "TIE"):
                    print '<td nowrap class="tiedgame" style="%s">%s</td>' % (special, Teams[pick].Name if pick != None else "&mdash;")

                elif (pick == None):
                    print '<td nowrap class="badpick" style="%s">&mdash;</td>' % (special)

                elif (m.getWinner() == pick):
                    print '<td nowrap class="goodpick" style="%s">%s</td>' % (special, Teams[pick].Name)

                else:
                    print '<td nowrap class="badpick" style="%s">%s</td>' % (special, Teams[pick].Name)

            # If past match start but not final yet, print pick with colors
            else:

                if (pick == None):
                    print '<td style="%s">&mdash;</td>' % (special)

                elif (m.hasScore()):
                    if m.AwayScore > m.HomeScore: now_wins = m.AwayTeam
                    elif m.HomeScore > m.AwayScore: now_wins = m.HomeTeam
                    else: now_wins = "TIE"
                    if (pick == now_wins):
                        print '<td style="color: green; %s">%s</td>' % (special, Teams[pick].Name)
                    elif (now_wins != "TIE" and pick != now_wins):
                        print '<td style="color: red; %s">%s</td>' % (special, Teams[pick].Name)
                    else:
                        print '<td style="%s">%s</td>' % (special, Teams[pick].Name)

                else:
                    print '<td style="%s">%s</td>' % (special, Teams[pick].Name)


    print '</tr>'

# Repeat table header
print '<thead>'
print '<tr>'
print '<td class="header">#</td>'
print '<td class="header">Hora&#8224;</td>'
print '<td class="header" style="text-align: right;">Equipo Visitante</td>'
print '<td class="header">&nbsp;</td>'
print '<td class="header" style="text-align: left;">Equipo Local</td>'
print '<td class="header">Estado</td>'
print '<td class="header">Posici&oacute;n</td>'
print '<td class="header">Stats</td>'
# If a user is logged, add an extra border width to his/her column
for pidx,p in enumerate(logged_list + Players):
    if (logged_user != None and pidx == 0):
        special = 'border-left-width: 3px; border-right-width: 3px;'
    else:
        special = ''
    print '''<td class="header" style="%s"><a data-toggle="tooltip" title="%s" data-placement="top"
    style="text-decoration: none">%s</a></td>''' % (special, p.Fullname, p.Username)
print '</tr>'
print '</thead>'

# Week score row
print '<tr>'
print '<td nowrap colspan="6" style="text-align: left;"><small>&#8224;Hora del Centro de M&eacute;xico</small></td>'
print '<td nowrap colspan="2" style="text-align: right;">Semana %i:</td>' % (week)
for pidx,p in enumerate(logged_list + Players):
    if (logged_user != None and pidx == 0):
        special = 'border-left-width: 3px; border-right-width: 3px;'
    else:
        special = ''
    if p.WeekPoints[week-1]!=None and p.WeekMisses[week-1]!=None:
        print '<td nowrap style="%s">%i&ndash;%i</td>' % (special, p.WeekPoints[week-1],p.WeekMisses[week-1])
    else:
        print '<td nowrap style="%s">&mdash;</td>' % (special)
print '</tr>'

# Global score row
print '<tr>'
print '<td nowrap colspan="6" style="text-align: left;"><small>Construido con <a href="http://www.python.org/" target="_blank">Python</a> y <a href="http://www.mysql.org/" target="_blank">MySQL</a>. Estilos por <a href="http://getbootstrap.com/">Bootstrap</a>.</small></td>'
print '<td nowrap colspan="2" style="text-align: right;"><b>Global:</b></td>'
for pidx,p in enumerate(logged_list + Players):
    if (logged_user != None and pidx == 0):
        special = 'border-left-width: 3px; border-right-width: 3px;'
    else:
        special = ''
    if p.GlobalScore!=None and p.GlobalMisses!=None:
        print '<td nowrap style="%s"><b>%i&ndash;%i</b></td>' % (special, p.GlobalScore,p.GlobalMisses)
    else:
        print '<td nowrap style="%s">&mdash;</td>' % (special)
print '</tr>'
print '</table></div>'

# Forecast submit button
if (logged_user != None):
    print '<form class="form-horizontal" name="forecastsubmit" action="/NFL%i/cgi-bin/FCSubmitPage.py?week=%i" method="post">' % (season, week)
    print '<button type="submit" class="btn btn-primary">Cambiar Pron&oacute;sticos</button>'
    print '</form>'
#    print '<br>'

print '<hr>'

# ERROR MESSAGES
if errmsg != "": print "<small>%s</small><br>" % (errmsg)

print '<small>P&aacute;gina generada %s</small><br>' % (now.astimezone(mexicoTZ))

print '</div><!--col-md-9 col-md-push-3-->'

# ======================================

# Sidebar (with scores) -- pushed on top on large viewports through bootstrap

print
print '<div class="col-md-3 col-md-pull-9">'
print '<div class="sidebar">'

# Scores table

print
print '<h4>Posiciones</h4>'
print '<table class="table table-striped table-bordered scores-table">'
print '<thead>'
print '<tr>'
print '<th style="text-align: center;">Pos</th>'
print '<th style="text-align: center;">Dif</th>'
print '<th>Jugador</th>'
print '</tr>'
print '</thead>'
print '<tbody>'

if len(Players) > 0:
  topscore = Players[0].GlobalScore
       
for p in Players:

    print '<tr>'
    
    # Rank cell
    if p.GlobalRank==None:
        print '<td>&mdash;</td>'
    else:
        if p.PrevRank==None:
            rank_icon = '' 
        elif p.GlobalRank<p.PrevRank:
            rank_icon = ' <img src="/NFL%i/iconz/rank_up.png" style="vertical-align: middle;">' % (season)
        elif p.GlobalRank==p.PrevRank:
            rank_icon = ' <img src="/NFL%i/iconz/rank_same.png" style="vertical-align: middle;">' % (season)
        elif p.GlobalRank>p.PrevRank:
            rank_icon = ' <img src="/NFL%i/iconz/rank_down.png" style="vertical-align: middle;">' % (season)
#        print '<td style="text-align: center; vertical-align: baseline;">%i%s(%i)</td>' % (p.GlobalRank, rank_icon, p.PrevRank)
        print '<td style="text-align: center; vertical-align: baseline;">%i%s</td>' % (p.GlobalRank, rank_icon)

    # Point difference cell
    if p.GlobalRank==None:
        print '<td>&mdash;</td>'
    else:
        if p.GlobalScore == topscore:
            print '<td style="text-align: center;">L&iacute;der</td>'
        else:
            print '<td style="text-align: center;">&minus;%i</td>' % (abs(p.GlobalScore-topscore))

    # Name cell (with full name tooltip)
    print '''<td><a data-toggle="tooltip" title="%s" data-placement="top"
             style="text-decoration: none">%s</a></td>''' % (p.Fullname, p.Username)

    print '</tr>'

print '</tbody>'
print '</table>'

print '</div><!--sidebar-->'
print '</div><!--col-md-2-->'

# ======================================

print '</div><!--row-fluid-->'
print '</div><!--container-->'

bootstrapFooter()

print '</body>'
print '</html>'