#!/usr/bin/env python

# Receives forecasts from the html form and enters changes into the DB

import cgi, cgitb
cgitb.enable()
from common import *

# ------------------------------------
# Generate "bad user password" page
# ------------------------------------
def generateBadLoginPage():
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Pron&oacute;sticos de la Quiniela NFL %i</h3>' % (season)
    print 'Parece que tu sesi&oacute;n ha expirado. Inicia de sesi&oacute;n de nuevo e intenta nuevamente.<br>'
    print '</div>'
    outputPageFooter()

# ------------------------------------------
# Generate "forecasts accepted" Page
# ------------------------------------------
def generateConfirmationPage(logged_user, Matches, new_fc, changed_fc, expired_fc, week):
  print "Content-type:text/html\r\n\r\n"
  print '<html>'
  print '<head>'
  print '<title>Quiniela NFL 2013</title>'
  bootstrapHeader()
  print '</head>'
  print '<body>'
  bootstrapNavbar(None, logged_user)
  print '<div class="container">'
  print '<h3>Pron&oacute;sticos guardados</h3>'
  print 'Tus pron&oacute;sticos han sido guardados, <b>%s</b>.<br>' % logged_user.Username
  print 'Volver a la <a href="/NFL%i/cgi-bin/MainPage.py">p&aacute;gina principal</a>.<br><br>' % (season)

  # ------ DEBUG AREA -------



  # -------------------------

  # Report expired forecasts not saved
  if len(expired_fc) > 0:
    print '<strong>Advertencia</strong>: los siguientes pron&oacute;sticos <strong>no</strong> pudieron guardarse pues los partidos ya estaban cerrados.<br>'
    for i,match in enumerate(Matches):
      if match.MatchID in expired_fc:
        print '%s<br>' % (Teams[match.AwayTeam].Name + " vs. " + Teams[match.HomeTeam].Name)
        
  print '<h3>Semana %i</h3>' % (week)
  print 'Total de cambios: <b>%i</b><br>' % (len(new_fc)+len(changed_fc))
  print 'Los cambios est&aacute;n indicados en negritas.<br>'
  print '<table class="table table-bordered table-hover table-striped main-table">'
  print '<thead>'
  print '<tr class="header">'
  print '<td class="header"><b>&nbsp;</b></td>'
  print '<td class="header"><b>Fecha/Hora</b></td>'
  print '<td class="header"><b>Partido</b></td>'
  print '<td class="header"><b>Tu Pron&oacute;stico</b></td>'
  print '</tr>'
  print '</thead>'
  print '<tbody>'
  i = 0
  for match in Matches:
    MatchID = match.MatchID
    if MatchID in logged_user.Forecasts:
      pick = logged_user.Forecasts[MatchID]
    else:
      pick = None
    i += 1
    if MatchID in new_fc or MatchID in changed_fc:
      print '<tr class="boldtext">'
    else:
      print '<tr>'
    print '<td>%s</td>' % (i)
    mdatetime = match.DateTime.astimezone(mexicoTZ).strftime("%a %d de %b, %H:%M")
    mdatetime = spanishDateCorrection(mdatetime)
    print '<td>%s</td>' % (mdatetime)
    print '<td>%s</td>' % (Teams[match.AwayTeam].Name+" vs. "+Teams[match.HomeTeam].Name)
    print '<td>'  
    if pick != None:
      print '%s' % (Teams[pick].Name)
    else:
      print '&mdash;'
    print '</td>'
    print '</tr>'
  print '<tbody>'
  print '</table>'

  print '<small>Horas son del Centro de M&eacute;xico. Programado en <a href="http://www.python.org/" target="_blank">Python</a>.</small>'

  print '</div>'
  bootstrapFooter()
  print '</body>'
  print '</html>'

# ------------------------------------------

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Determine logged user from cookie, if any
# Exit if no user is authenticated
logged_user = authenticateUser()
if logged_user == None:
    generateBadLoginPage()
    sys.exit()

# Get basic data from Form
if form.has_key("num"): num = int(form["num"].value)
else: num = 0
if form.has_key("week"): week = int(form["week"].value)
else: week = defaultweek

# Load stuff from DB
db = DBHelper()
db.Connect()
Teams = db.loadTeams()
Matches = db.loadMatches(week)
logged_user.loadForecasts(week)
db.Close()

# Organize submitted forecasts into a dictionary
sent_fc = {}
for key in form.keys():
  for match in Matches:
     if (key == match.MatchID): sent_fc[match.MatchID] = form[key].value

# Determine which submitted forecasts are new or are changed
new_fc = {}
changed_fc = {}
for matchID in sent_fc:
    if matchID not in logged_user.Forecasts:
        new_fc[matchID] = sent_fc[matchID]
    elif sent_fc[matchID] != logged_user.Forecasts[matchID]:
        changed_fc[matchID] = sent_fc[matchID]

# Remove new or changed forecasts if match is past deadline (prevents page wait exploit)
now = get_utcnow()
MatchesDict = {}
for m in Matches:
    MatchesDict[m.MatchID] = m 
expired_fc = []
keys = new_fc.keys()
for matchID in keys:
    if matchID in MatchesDict and now > MatchesDict[matchID].DateTime:
        expired_fc.append(matchID)
        new_fc.pop(matchID, None)
keys = changed_fc.keys()
for matchID in keys:
    if matchID in MatchesDict and now > MatchesDict[matchID].DateTime:
        expired_fc.append(matchID)
        changed_fc.pop(matchID, None)
    
  
# BACKUP FORECASTS TABLE
backupTable("Forecasts")

# Update DB -- add new forecasts
db = DBHelper()
db.Connect()
for matchID in new_fc:
    db.addForecast(matchID, logged_user.Username, new_fc[matchID], week)
for matchID in changed_fc:
    db.updateForecast(matchID, logged_user.Username, changed_fc[matchID])
db.Close()

# Confirm the saved forecasts
logged_user.loadForecasts(week)
generateConfirmationPage(logged_user, Matches, new_fc, changed_fc, expired_fc, week)





