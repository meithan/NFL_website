#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Generates the Forecast Submit Page
import cgi, cgitb
cgitb.enable()
from common import *

# ----------------------------------

# Page header, using bootstrap
def outputPageHeader():
    print "Content-type:text/html\r\n\r\n"
    print '<!DOCTYPE html>'
    print '<html lang="en">'
    print '<head><meta http-equiv="Content-Type" content="text/html; charset=gb18030">'
    bootstrapHeader()
    print '<title>Quiniela NFL %i</title>' % (season)
    print '</head>'
    print '<body>'
    bootstrapNavbar("",logged_user)

# Page footer
def outputPageFooter():
    bootstrapFooter()
    print '</body>'
    print '</html>'

# ------------------------------------
# Generate forecast submit page
# ------------------------------------
def generateSubmitPage(player, week):

  # Webpage content header
  print 'Content-type:text/html'

  print 
  print '<html>'
  print '<head>'
  bootstrapHeader()

  print '<script type="text/javascript">'

  print 'function setGreen(matchID,pick) {'
  print '  objid = matchID + "_ateam";'
  print '  var elem = document.getElementById(objid);'
  print '  if (pick=="ateam") {'
  print '    elem.style.backgroundColor = "#93E7AC";'
  print '  } else {'
  print '    elem.style.backgroundColor = "";'
  print '  }'
  print '  objid = matchID + "_hteam";'
  print '  var elem = document.getElementById(objid);'
  print '  if (pick=="hteam") {'
  print '    elem.style.backgroundColor = "#93E7AC";'
  print '  } else {'
  print '    elem.style.backgroundColor = "";'
  print '  }'
  print '}'

  print ''
#  print 'teams = {"ARI": "Arizona Cardinals", "ATL": "Atlanta Falcons", "BAL": "Baltimore Ravens", "BUF": "Buffalo Bills", "CAR": "Carolina Panthers", "CHI": "Chicago Bears", "CIN": "Cincinnati Bengals", "CLE": "Cleveland Browns", "DAL": "Dallas Cowboys", "DEN": "Denver Broncos", "DET": "Detroit Lions", "GB": "Green Bay Packers", "HOU": "Houston Texans", "IND": "Indianapolis Colts", "JAX": "Jacksonville Jaguars", "KC": "Kansas City Chiefs", "LA": "Los Angeles Rams", "MIA": "Miami Dolphins", "MIN": "Minnesota Vikings", "NE": "New England Patriots", "NO": "New Orleans Saints", "NYG": "New York Giants", "NYJ": "New York Jets", "OAK": "Oakland Raiders", "PHI": "Philadelphia Eagles", "PIT": "Pittsburgh Steelers", "SD": "San Diego Chargers", "SEA": "Seattle Seahawks", "SF": "San Francisco 49ers", "TB": "Tampa Bay Buccaneers", "TEN": "Tennessee Titans", "WAS": "Washington Redskins"}'
  print 'teams = {"ARI": "Cardinals", "ATL": "Falcons", "BAL": "Ravens", "BUF": "Bills", "CAR": "Panthers", "CHI": "Bears", "CIN": "Bengals", "CLE": "Browns", "DAL": "Cowboys", "DEN": "Broncos", "DET": "Lions", "GB": "Packers", "HOU": "Texans", "IND": "Colts", "JAX": "Jaguars", "KC": "Chiefs", "LA": "Rams", "MIA": "Dolphins", "MIN": "Vikings", "NE": "Patriots", "NO": "Saints", "NYG": "Giants", "NYJ": "Jets", "OAK": "Raiders", "PHI": "Eagles", "PIT": "Steelers", "SD": "Chargers", "SEA": "Seahawks", "SF": "49ers", "TB": "Buccaneers", "TEN": "Titans", "WAS": "Redskins"}'
  print 'function niceMatch(matchID) {'
  print '  tokens = matchID.split("-")[1].split("@");'
  print '  return teams[tokens[0]] + " vs. " + teams[tokens[1]];'
  print '}'

  print ''
  print 'function checkPicks() {'
  print '  var chx = document.getElementsByTagName("input");'
  print '  var matches = [];'
  print '  var picks = {};'
  print '  for (i = 0; i < chx.length; i++) {'
  print '    if (chx[i].type == "radio" && chx[i].style.display != "none") {'
  print '      if (!(chx[i].name in picks)) {'
  print '        matches.push(chx[i].name);'
  print '        picks[chx[i].name] = false;'
  print '      }'
  print '      if (chx[i].checked) picks[chx[i].name] = true;'
  print '    }'
  print '  }'
  print '  missing = [];'
  print '  for (i = 0; i < matches.length; i++) {'
  print '    if (picks[matches[i]] == false) missing.push(matches[i]);'
  print '  }'
  print '  console.log(missing.length);'
  print '  console.log(missing);'
  print '  save = true;'
  print '  if (missing.length > 0) {'
  print '    if (missing.length == 1) {'
  print '      var s = "No has puesto pronóstico para el siguiente partido:\\n\\n";'
  print '    } else {'
  print '      var s = "No has puesto pronóstico para los siguientes";'
  print '      s += " " + missing.length + " partidos:\\n\\n";'
  print '    }'
  print '    for (i = 0; i < missing.length; i++) {'
  print '      s += niceMatch(missing[i]) + "\\n";'
  print '    }'
  print '    s += "\\n¿Deseas guardar de todas formas?";'
  print '    var save = confirm(s);'
  print '  }'
  print '  console.log("submit? " + save);'
  print '  return save;'
  print '}'

  print '</script>'

  print '</head>'
  print '<body>'
  bootstrapNavbar (None, player)
  print '<div class="container">'

  # -------- DEBUG AREA ---------


  # -------- DEBUG AREA ---------

  print '<h3>Modifica tus pron&oacute;sticos para la Semana %i</h3>' % (week)
  print 'Usuario conectado: <strong>%s</strong>' % (logged_user.Username)
  print '<form name="submitforecast" id="forecastsForm" onsubmit="return checkPicks()" action="FCSubmit.py" method="POST">'

  # Main Table
  print '<br>'
  print '<div class="table-responsive">'
  print '<table class="table table-bordered table-hover table-striped main-table">'

  # Table Header
  print '<thead>'
  print '<tr class="header">'
  print '<td class="header">#</td>'
  print '<td class="header">Hora&#8224;</td>'
  print '<td class="header" style="text-align: center;">Equipo Visitante</td>'
  print '<td class="header" style="text-align: center;">Equipo Local</td>'
  print '</tr>'
  print '</thead>'

  # Table Body
  print '<tbody>'
  curdate = None

  # Matches
  for idx,match in enumerate(Matches):

    # Get Mexico timezone at the time of the match (DST ends October 30th in 2016)
    mexicoTZ = getMexicoTZ(match.DateTime)

    # Date row
    newdate = match.DateTime.astimezone(mexicoTZ).date().isoformat()
    if (curdate != newdate):
      curdate = newdate
      datenice = match.DateTime.astimezone(mexicoTZ).strftime("%A %d de %B")
      datenice = spanishDateCorrection(datenice)
      print '<tr><td class="date" colspan="%i"><strong>%s</strong></td></tr>' % (4, datenice)

    print '<tr>'
   
    # Match details
    print '<td class="number">%i</td>' % (idx+1)
    
    # Time
#    print '<td>%s</td>' % (match.DateTime.astimezone(mexicoTZ).strftime("%H:%M"))
    ampm = " am" if match.DateTime.astimezone(mexicoTZ).hour < 12 else " pm"
    print '<td>%s</td>' % ((match.DateTime.astimezone(mexicoTZ).strftime("%I:%M").lstrip("0") + ampm))

    # Set appropriate styling for the elements
    checked1 = ''
    checked2 = ''
    checkedtie = ''
    styles1 = []
    styles2 = []
    color1 = ""
    color2 = ""
    if match.MatchID in player.Forecasts:
        pick = player.Forecasts[match.MatchID]
    else:
        pick = None
    if match.pastStart():
        if pick == match.AwayTeam:
            checked1 = ' checked'
            styles1.append('background-color:#D0E8D7;')              
            styles2.append('background-color:#E5E5E5;')
        elif pick == match.HomeTeam:
            checked2 = ' checked'
            styles1.append('background-color:#E5E5E5;')                
            styles2.append('background-color:#D0E8D7;')
        else:
            styles1.append('background-color:#E5E5E5;')                
            styles2.append('background-color:#E5E5E5;')                
    else:
        if pick == match.AwayTeam:
            checked1 = ' checked'
            styles1.append('background-color:#93E7AC;')
        elif pick == match.HomeTeam:
            checked2 = ' checked'
            styles2.append('background-color:#93E7AC;')  


    # Remove cell padding so labels occupy all the cell space
#    styles1.append('padding: 0px;')
#    styles2.append('padding: 0px;')

    # Away Team
    id1 = match.MatchID + "_ateam"
    print '<td class="ateam" style="%s" id="%s">' % (" ".join(styles1), id1)
    print '<label for="%s">' % (match.AwayTeam)
    print '<img src="/NFL%i/iconz/%s.png" style="vertical-align:middle;">' % (season, Teams[match.AwayTeam].ID)
    print Teams[match.AwayTeam].City + " " + Teams[match.AwayTeam].Name
    if match.pastStart():
      colorchanger = ""
      disabled = 'style="display: none;"'
    else:
      colorchanger = "onClick=\"setGreen('%s','%s')\"" % (match.MatchID, "ateam")
      disabled = ""
    print '<input type="radio" id="%s" name="%s" value="%s" %s %s %s>' % (match.AwayTeam, match.MatchID, Teams[match.AwayTeam].ID, checked1, disabled, colorchanger)
    print '</label>'
    print '</td>'

    # Home Team
    id2 = match.MatchID + "_hteam"
    print '<td class="hteam" style="%s" id="%s">' % (" ".join(styles2), id2)
    print '<label for="%s">' % (match.HomeTeam)
    print '<img src="/NFL%i/iconz/%s.png">' % (season, Teams[match.HomeTeam].ID)
    print Teams[match.HomeTeam].City + " " + Teams[match.HomeTeam].Name
    if match.pastStart():
      colorchanger = ""
      disabled = 'style="display: none;"'
    else:
      colorchanger = "onClick=\"setGreen('%s','%s')\"" % (match.MatchID, "hteam")
      disabled = ""
    print '<input type="radio" id="%s" name="%s" value="%s" %s %s %s>' % (match.HomeTeam, match.MatchID, Teams[match.HomeTeam].ID, checked2, disabled, colorchanger)
    print '</label>'
    print '</td>'
        
    print '</tr>'

  # Repeat table Header
  print '<thead>'
  print '<tr class="header">'
  print '<td class="header">#</td>'
  print '<td class="header">Hora&#8224;</td>'
  print '<td class="header" style="text-align: center;">Equipo Visitante</td>'
  print '<td class="header" style="text-align: center;">Equipo Local</td>'
  print '</tr>'
  print '</thead>'

  # Note row
  print '<td colspan="5" style="text-align: left;"><small>&#8224;Hora del Centro de M&eacute;xico</small></td>'

  print '</table>'
  print '</div>'

  # Submit button
  print 'Modificando pron&oacute;sticos como: <strong>%s</strong><br><br>' % (logged_user.Username)
  print '<input type="hidden" name="sessionID" value="%s">' % (player.sessionID)
  print '<input type="hidden" name="week" value="%s">' % (week)
  print '<button type="submit" class="btn btn-primary">Guardar</button> <a href="http://meithan.net"><strong>Cancelar</strong></a>'
  print '<br><br>Puedes entrar de nuevo y modificar tus pron&oacute;sticos m&aacute;s tarde.'

  print '</form>' 
  print '</div><!--container-->'
  bootstrapFooter()
  print '</body>'
  print '</html>'

# ------------------------------------
# Generate "bad user password" page
# ------------------------------------
def generateBadLoginPage():
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Pron&oacute;sticos de la Quiniela NFL %i</h3>' % (season)
    print 'Debes iniciar sesi&oacute;n para poder modificar tus pron&oacute;sticos.<br>'
    print '</div>'
    outputPageFooter()

# ========================================================

# Determine logged user from cookie, if any
# Exit if no user is authenticated
logged_user = authenticateUser()
if logged_user == None:
    generateBadLoginPage()
    sys.exit()
    
# Get week from passed cgi parameters
# or get the week from the current date
form = cgi.FieldStorage()
if form.has_key("week"):
    week = int(form["week"].value)
else:
    week = getCurrentWeek(get_utcnow())

# Connect to MySQL database
db = DBHelper()
db.Connect()

# Load stuff from DB
Teams = db.loadTeams()
Matches = db.loadMatches(week)
db.Close()

# Load current forecatss for the player
logged_user.loadForecasts(week)

generateSubmitPage(logged_user, week)
