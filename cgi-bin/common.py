# =====================================
# Common definitions module
# =====================================
import md5
import datetime
import string
import xml.dom.minidom as xml
import urllib2
import json
import locale
import os
import Cookie
import sys
import random
import subprocess
import MySQLdb

# =====================================
# Time zone information

class UTC_offset(datetime.tzinfo):
    def __init__(self, offset, name):
        self.offset = offset
        self.name = name
    def utcoffset(self, dt):
        return datetime.timedelta(hours=self.offset)
    def dst(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return self.name
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.name + " (UTC%+i)" % self.offset

# Timezones
ET  = UTC_offset(-5,"ET")
EDT = UTC_offset(-4,"EDT")
CT  = UTC_offset(-6,"CT")
CDT = UTC_offset(-5,"CDT")
MT  = UTC_offset(-7,"MT")
MDT = UTC_offset(-6,"MDT")
PT  = UTC_offset(-8,"PT")
PDT = UTC_offset(-7,"PDT")
UTC = UTC_offset(0,"UTC")

# Returns the correct Mexico timezone for the given date and time (DST ends October 30th at 00:00)
def getMexicoTZ(date_time=None):   
  if date_time == None: date_time = get_utcnow()
  if (date_time < datetime.datetime(2016, 10, 29, 0, 0, 0, tzinfo=CT)):
    return CDT
  else:
    return CT

# Returns the current UTC as a tz-aware object
def get_utcnow():
  return datetime.datetime.utcnow().replace(tzinfo=UTC)

# =====================================
# Localization

locale.setlocale(locale.LC_ALL, 'es_MX')

# =====================================
# MySQLdb stuff

import sys
import MySQLdb

# =====================================
# Site-wide Configuration

# x10Hosting is on CST/CDT
# Heliohost is on PST/PDT
#serverTZ = EDT
mexicoTZ = getMexicoTZ()
registrationClosed = True
season = 2016
DB_NAME = "meithann_nfl2016"
entry_cost = 300
perfect_bonus = 500
perfect_awards = []
page_cost = 350

# =====================================

# WEEK BYES, TEMPORARY -- this should be obtained from DB
week_byes = {}
week_byes[4] = ['GB', 'PHI']
week_byes[5] = ['JAX', 'KC', 'NO', 'SEA']
week_byes[6] = ['MIN', 'TB']
week_byes[7] = ['CAR', 'DAL']
week_byes[8] = ['BAL', 'MIA', 'NYG', 'PIT', 'LA', 'SF']
week_byes[9] = ['ARI', 'CHI', 'CIN', 'WAS', 'NE', 'HOU']
week_byes[10] = ['BUF', 'DET', 'IND', 'OAK']
week_byes[11] = ['ATL', 'DEN', 'NYJ', 'SD']
# No byes on week 12
week_byes[13] = ['TEN', 'CLE']

# WEEK STARTS
# A week is considered to start two days before first gameday at 8pm ET
week_starts = [None]*18
week_starts[1] = datetime.datetime(2016, 9, 6, 20, 0, 0, 0, EDT)
week_starts[2] = datetime.datetime(2016, 9, 13, 20, 0, 0, 0, EDT)
week_starts[3] = datetime.datetime(2016, 9, 20, 20, 0, 0, 0, EDT)
week_starts[4] = datetime.datetime(2016, 9, 27, 20, 0, 0, 0, EDT)
week_starts[5] = datetime.datetime(2016, 10, 4, 20, 0, 0, 0, EDT)
week_starts[6] = datetime.datetime(2016, 10, 11, 20, 0, 0, 0, EDT)
week_starts[7] = datetime.datetime(2016, 10, 18, 20, 0, 0, 0, EDT)
week_starts[8] = datetime.datetime(2016, 10, 25, 20, 0, 0, 0, EDT)
week_starts[9] = datetime.datetime(2016, 11, 1, 20, 0, 0, 0, ET)
week_starts[10] = datetime.datetime(2016, 11, 8, 20, 0, 0, 0, ET)
week_starts[11] = datetime.datetime(2016, 11, 15, 20, 0, 0, 0, ET)
week_starts[12] = datetime.datetime(2016, 11, 22, 20, 0, 0, 0, ET)
week_starts[13] = datetime.datetime(2016, 11, 30, 20, 0, 0, 0, ET)
week_starts[14] = datetime.datetime(2016, 12, 6, 20, 0, 0, 0, ET)
week_starts[15] = datetime.datetime(2016, 12, 13, 20, 0, 0, 0, ET)
week_starts[16] = datetime.datetime(2016, 12, 20, 20, 0, 0, 0, ET)
week_starts[17] = datetime.datetime(2017, 12, 28, 20, 0, 0, 0, ET)

# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# Session handling
# =====================================

# Reads a cookie and authenticates the user, returning a Player object (or None)
def authenticateUser():

    # Read cookies. If present, authenticate and set logged user.
    if 'HTTP_COOKIE' in os.environ:
        cookies = os.environ['HTTP_COOKIE']
        cookies = cookies.split('; ')
    else:
#        print "No cookies sent<br>"
        return None
    cookiejar = {}
    for cookie in cookies:
        cookie = cookie.split('=',1)
        cookiejar[cookie[0]] = cookie[1]

#    print "cookiejar=",cookiejar,"<br>"

    # Check for sessionID cookie
    if "sessionID" not in cookiejar: return None 
    else: sessionID = cookiejar["sessionID"]

    # Look for sessionID in DB
    db = DBHelper()
    db.Connect()
    response = db.getSession(sessionID)

#    print "db response=",response,"<br>"

    # Return None if sessionID not found, or recover user data
    logged_user = None
    if response==None: return None
    else:
        user = response[1]
        logged_user = db.getPlayer(user)
        if logged_user != None: logged_user.sessionID = sessionID
    db.Close()
    return logged_user


# =====================================

# Create a new session, save its data to the DB and send a cookie
def createSession(user,remember_me):

    # Create new session and cookie
    new_sessionID = ""
    for i in range(20):
        new_sessionID += random.choice("0123456789") 
    cookie = Cookie.SimpleCookie()
    cookie["sessionID"] = new_sessionID
    cookie["sessionID"]["domain"] = "meithan.net"
    cookie["sessionID"]["path"] = "/"

    # Only set an expiration date if the user wants to be remembered
    if remember_me:
        duration = datetime.timedelta(days=30)
        expiration = datetime.datetime.utcnow() + duration
        expiry_str = expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        expiry_str = toEnglishWeekdays(expiry_str)
        cookie["sessionID"]["expires"] = expiry_str
        type = "normal"
        expiration = expiration.strftime("%Y-%m-%d %H:%M:%S")
    else:
        type = "session"
        expiration = None

    issue = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Store new session details to DB
    db = DBHelper()
    db.Connect()
    db.addSession(new_sessionID, user, type, expiration, issue)
    db.Close()

    # Send cookie and redirect to main page
    print "Content-type:text/html"
    print cookie.output()    # <-- send the cookie to the browser
    print "Status: 303 See other"
    print "Location: http://meithan.net"
    print "\r\n\r\n"

# =====================================

# Logs a user out by sending a cookie revocation
# and eliminates the session from the DB
def doLogout(sessionID):
    
    # Remove session from DB
    db = DBHelper()
    db.Connect()
    db.removeSession(sessionID)
    db.Close()

    # Create new cookie for revocation
    cookie = Cookie.SimpleCookie()
    cookie["sessionID"] = sessionID
    cookie["sessionID"]["domain"] = "meithan.net"
    cookie["sessionID"]["path"] = "/"
    expiration = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    cookie["sessionID"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

    # Send cookie and redirect to main page
    print "Content-type:text/html"
    print cookie.output()    # <-- send the cookie to the browser
    print "Status: 303 See other"
    print "Location: http://meithan.net/NFL%i/cgi-bin/MainPage.py" % (season)
    print "\r\n\r\n"

# =====================================

# Removes all expired sessions from the DB
def removeExpiredSessions():
    db = DBHelper()
    db.Connect()
    db.removeExpiredSessions()
    db.Close()


# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# Common page blocks
# =====================================

# Bootstrap Header, without the head tags
def bootstrapHeader():
    print '<meta charset="utf-8">'
    print '<meta http-equiv="X-UA-Compatible" content="IE=edge">'
    print '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">'
    print '<meta name="description" content="">'
    print '<meta name="author" content="">'
    print '<meta http-equiv="cache-control" content="max-age=0" />'
    print '<meta http-equiv="cache-control" content="no-cache" />'
    print '<meta http-equiv="expires" content="0" />'
    print '<meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />'
    print '<meta http-equiv="pragma" content="no-cache" />'
    print '<link rel="shortcut icon" href="/NFL%i/favicon.ico?reload=yes">' % (season)
    print '<!-- Bootstrap core CSS -->'
    print '<link href="/NFL%i/css/bootstrap.css" rel="stylesheet">' % (season)
    print '<!-- Custom styles for this template -->'
    print '<link href="/NFL%i/css/nfl%i.css" rel="stylesheet">' % (season, season)

# =====================================

# Bootstrap Navbar
# Receives the current page in order to highlight it
def bootstrapNavbar(curpage, logged_user):
    print
    print '<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">'
    print '<div class="container">'
    print '<div class="navbar-header">'
    print '<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">'
    print '<span class="sr-only">Toggle navigation</span>'
    print '<span class="icon-bar"></span>'
    print '<span class="icon-bar"></span>'
    print '<span class="icon-bar"></span>'
    print '</button>'
    print '<a class="navbar-brand" href="http://meithan.net/NFL%i/cgi-bin/MainPage.py">Quiniela NFL %i</a>' % (season, season)
    print '</div>'
    print '<div class="collapse navbar-collapse">'
    print '<ul class="nav navbar-nav">'

    active = ' class="active"' if curpage=="Main" else ""  
    print '<li%s><a href="/NFL%i/cgi-bin/MainPage.py">Principal</a></li>' % (active, season)

    active = ' class="active"' if curpage=="Standings" else ""
    print '<li%s><a href="/NFL%i/cgi-bin/StandingsPage.py">Posiciones</a></li>' % (active, season)

    active = ' class="active"' if curpage=="Prizes" else ""
    print '<li%s><a href="/NFL%i/cgi-bin/PrizesPage.py">Premios</a></li>' % (active, season)

    active = ' class="active"' if curpage=="Chart" else ""
    print '<li%s><a href="/NFL%i/cgi-bin/ChartPage.py">Gr&aacute;ficas</a></li>' % (active, season)

    active = ' class="active"' if curpage=="Rules" else ""
    print '<li%s><a href="/NFL%i/cgi-bin/RulesPage.py">Reglas</a></li>' % (active, season)

    active = ' class="active"' if curpage=="Players" else ""  
    print '<li%s><a href="/NFL%i/cgi-bin/PlayersPage.py">Jugadores</a></li>' % (active, season)

    if not registrationClosed:
        active = ' class="active"' if curpage=="Registration" else ""
        print '<li%s><a href="/NFL%i/cgi-bin/RegistrationPage.py">Registro</a></li>' % (active, season)

    print '</ul>'


    # Session stuff

    if logged_user==None:
        # Show login form
        print '<ul class="nav navbar-nav navbar-right">'
        print '<li class="dropdown">'
        print '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Login <span class="caret"></span></a>'
        print '<div class="dropdown-menu" style="padding: 10px; margin-top: 1px;" role="menu">'
        print '<form role="form" class="form-horizontal" method="POST" action="/NFL%i/cgi-bin/login.py">' % (season)
        print '<div class="input-group" style="padding: 5px">'
        print '<input type="text" class="form-control" name="username" size="30" placeholder="Usuario" />'
        print '</div>'
        print '<div class="input-group" style="padding: 5px">'
        print '<input type="password" class="form-control" name="password" size="30" placeholder="Contrase&ntilde;a" />'
        print '</div>'
        print '<div class="input-group" style="padding: 5px">'
        print '<input type="checkbox" style="float: left; margin-right: 10px;" name="remember_me" value="yes" checked /> Recordarme'
        print '</div>'
        print '<div class="input-group" style="padding: 5px">'
        print '<button type="submit" class="btn btn-primary">Acceder</button>'
        print '</div>'
        print '</form>'
        print '</div>'
        print '</li>'
        print '</ul>'

    else:
        # Show logged user and logout button
        print '<ul class="nav navbar-nav navbar-right">'
        print '<li class="dropdown">'
        print '<a href="#" class="dropdown-toggle" data-toggle="dropdown">Hola, <strong>%s</strong> <span class="caret"></span></a>' % (logged_user.Username)
        print '<div class="dropdown-menu" style="padding: 10px; margin-top: 1px;" role="menu">'
        print '<form role="form" class="form-horizontal" method="POST" action="/NFL%i/cgi-bin/logout.py?sessionID=%s">' % (season, logged_user.sessionID)
        print 'Est&aacute;s viendo la p&aacute;gina como <strong>%s</strong>.' % (logged_user.Username)
        print '<div class="input-group" style="padding: 5px">'
        print '<button type="submit" class="btn btn-primary">Salir</button>'
        print '</div>'
        print '</form>'
        print '</div>'
        print '</li>'
        print '</ul>'


    print '</div><!--/.nav-collapse -->'
    print '</div>'
    print '</div>'

# =====================================

# Bootstrap footer with javascript stuff
def bootstrapFooter():
    print '<!-- Bootstrap core JavaScript'
    print '================================================== -->'
    print '<!-- Placed at the end of the document so the pages load faster -->'
    print '<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>'
    print '<script src="/NFL%i/js/bootstrap.min.js"></script>' % (season)
    print '<script> $(function () { $("[data-toggle=\'tooltip\']").tooltip(); }); </script>'   # ENABLE TOOLTIPS

# =====================================

# Outputs rules, with full markup
def outputRules():
    print '<ol class="ruleslist">'
    print '<li><strong>Costo</strong>. La entrada es de $%i (tres cientos) pesos, la cual deber&aacute; ser pagada antes del inicio de la Temporada NFL %i (8 de septiembre a las 7:30pm). La suma de las entradas constituye la Bolsa.</li>' % (entry_cost, season)
    print '<li><strong>Registro</strong>. Cada participante deber&aacute; registrarse en esta p&aacute;gina para poder participar. No se aceptar&aacute;n participantes despu&eacute;s del inicio de la Temporada.</li>'
    print '<li><strong>Mec&aacute;nica</strong>. Para cada uno de los 256 partidos de la <em>Temporada Regular</em>, cada participante deber&aacute; enviar su pron&oacute;stico de <em>ganador</em>, empleando la interfaz web de esta p&aacute;gina. Cada pron&oacute;stico correcto equivale a un punto; los juegos que llegaran a terminar en empate no se contar&aacute;n. El ranking de los jugadores est&aacute; determinado por el total de puntos.</li>'
    print '<li><strong>Premios</strong>. Al final de la Temporada Regular, la Bolsa (despu&eacute;s de las deducciones posibles por bonos; ver siguiente regla) se dividir&aacute; en tres premios de la siguiente forma:'
    print '<ul>'
    print '<li>1er lugar: 50%</li>'
    print '<li>2do lugar: 30%</li>'
    print '<li>3er lugar: 20%</li>'
    print '</ul>'
    print '<p>Estos premios ser&aacute;n entregados a los ganadores seg&uacute;n el ranking final que hayan obtenido.</p>'
    print '<p>En caso de empates, los premios se dividir&aacute;n equitativamente entre los ganadores, sujeto a lo siguiente: si hay m&aacute;s de dos jugadores en primer o segundo lugar, no habr&aacute; premio a tercer lugar; si m&aacute;s de dos jugadores empatan a primer lugar, tampoco habr&aacute; premio a segundo lugar. La distribuci&oacute;n hipot&eacute;tica de los premios determinada por el ranking puede consultarse en todo momento en la p&aacute;gina <a href="/NFL%i/cgi-bin/PrizesPage.py">Premios</a>.</p>' % (season)
    print '</li>'
    print '<li><strong>Bono a Semana Perfecta</strong>. Adem&aacute;s de los premios a los tres primeros lugares, se otorgar&aacute; un bono de <strong>$500</strong> al jugador que acierte a <u><em>todos</em> los partidos de una misma semana</u>, excluyendo aquellos que hayan terminado en empate (si ocurriera). Este bono podr&aacute; otorgarse m&uacute;ltiples veces (incluso al mismo jugador) si la haza&ntilde;a ocurriera en varias ocasiones. Los bonos correspondientes ser&aacute;n deducidos de la Bolsa.</li>'
    print '<li><p><strong>Plazo para env&iacute;o</strong>. El plazo l&iacute;mite para enviar cada pron&oacute;stico individual es el inicio <em>originalmente anunciado</em> de ese partido (incluso si el inicio del partido ocurriera en un momento distinto). Es responsabilidad de cada participante recordar enviar sus pron&oacute;sticos a tiempo. <u>No habr&aacute; excepciones a esta regla</u>.</p>'
    print '<p>Si por cualquier raz&oacute;n el participante no puede enviar su pron&oacute;stico a trav&eacute;s de esta p&aacute;gina web, puede enviarlo al organizador <em>antes del inicio programado del partido</em> a trav&eacute;s de cualquier v&iacute;a electr&oacute;nica, como el grupo de facebook o correo electr&oacute;nico. La hora de recepci&oacute;n del mensaje se usar&aacute; para determinar si el pron&oacute;stico es aceptado.</p>'
    print '</li>'
    print '</ol>'


# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# Misc functions
# =====================================

# Determine the "current week" from the passed datetime object
# A week is considered the "current" one two days before first gameday at 8pm ET
def getCurrentWeek(date_time):   
    if date_time < week_starts[1]: return 1
    for i in range(2,17+1):
       if date_time < week_starts[i]: return i-1
    return 17

# =====================================

# Uppercases spanish weekdays and months, gets rid of leading zeros in dates
def spanishDateCorrection(s):
    corrections = [("lun","Lun"),("mar","Mar"),("mi\xe9","Mi&eacute;"),("jue","Jue"),("viernes","Viernes"),\
    ("s\xe1b","S&aacute;b"),("dom","Dom"),\
    ("ene","Ene"),("feb","Feb"),("mar","Mar"),("abr","Abr"),("may","May"),("jun","Jun"),\
    ("jul","Jul"),("ago","Ago"),("sep","Sep"),("oct","Oct"),("noviembre","Noviembre"),("dic","Dic") ]
    for item,corrected in corrections:
        s = s.replace(item,corrected)
    s = s.replace(" 0", " ")
    return s

# =====================================

# Replaces spanish week day abbreviations to english equivalents
# Required for cookie expiration date
def toEnglishWeekdays(s):
    corrections = [("lun","Mon"),("mar","Tue"),("mi\xe9","Wed"),("jue","Thu"),("vie","Fri"),\
    ("s\xe1b","Sat"),("dom","Sun")]
    for item,corrected in corrections:
        s = s.replace(item,corrected)
    return s

# =====================================

# Returns the 'sane' version of a string (no spaces, no punctuation)
alphanumeric = string.ascii_letters + string.digits
def sane(s):
    result = ""
    for i in range(len(s)):
        if s[i] in alphanumeric: result += s[i]
        if s[i]==" ": result += "_"
    return result

# =====================================

# Returns a datetime object from an iso formatted date
def datetimeFromISO(isodate,tz):
    foo = isodate.split('-')
    year = int(foo[0])
    month = int(foo[1])
    day = int(foo[2])
    return datetime.datetime(year,month,day,tzinfo=tz)


# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# MySQL Database Helper Class
# =====================================

class DBHelper:

    def __init__(self):
        self.db = None
        self.cursor = None

    # Connects to the database and sets the global db object
    def Connect (self):
        from config import mysql_hostname, mysql_dbname, mysql_username, mysql_password
        self.db = MySQLdb.connect(mysql_hostname, mysql_username, mysql_password, mysql_dbname)
        self.cursor = self.db.cursor()

    # Close connection
    def Close (self):
        self.db.close()

    # The following functions assume the cursor object is loaded

    # Adds a new player to the DB
    # data must be [user_name, full_name, email, pswd_hash]
    def addPlayer (self, data):
        user_name = data[0]
        full_name = data[1]
        email = data[2]
        pswd_hash = data[3]
        payment = "FALSE"
        query = """INSERT INTO Players VALUES ('%s', '%s', '%s', '%s', %s);""" % (user_name, 
full_name, email, pswd_hash, payment)
        try:
            self.cursor.execute(query)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        self.cursor = self.db.cursor()   # create new cursor to prevent duplicate queries
        query = "INSERT INTO Scores (user_name,global_rank,prev_rank) VALUES ('%s',1,1);" % (user_name)
        try:
            self.cursor.execute(query)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    # Reads the players from the DB and returns a list of Player objects
    def loadPlayers (self):
        Players = []
        self.cursor.execute("SELECT * FROM Players;")
        rowset = self.cursor.fetchall()
        for row in rowset:
            newPlayer = Player(row)
            if newPlayer.paid==1:
                newPlayer.paid = True
            else:
                newPlayer.paid = False
            Players.append(newPlayer)
        return Players

    # Reads the teams from the DB and returns a dict of Team objects
    def loadTeams (self):
        Teams = {}
        self.cursor.execute("SELECT * FROM Teams;")
        rowset = self.cursor.fetchall()
        for row in rowset:
            newTeam = Team(row)
            Teams[newTeam.ID] = newTeam
        return Teams

    # Reads the matches for the given week number from the DB and returns a list of Match objects
    # Sorts the list by ascending date and time
    def loadMatches (self, week):
        Matches = []
        self.cursor.execute('SELECT * FROM Matches WHERE week="%i";' % week)
        rowset = self.cursor.fetchall()
        for row in rowset:
            newMatch = Match(row)
            Matches.append(newMatch)
        Matches.sort(key=lambda m: m.DateTime)
        return Matches

    # Retrieves the information of a single match from the DB and returns a Match object
    def loadMatch (self, matchID):
        self.cursor.execute('SELECT * FROM Matches WHERE id="%s";' % matchID)
        rowset = self.cursor.fetchall()
        if len(rowset) == 0: return None
        return Match(rowset[0])

    # Stores a new user session in the DB
    def addSession (self, SessionID, Username, Type, Expiration, Issue):
        values = '"%s", "%s", "%s", "%s", "%s"' % (SessionID, Username, Type, Expiration, Issue)
        query = 'INSERT INTO Sessions VALUES (%s);' % values
        try:
            self.cursor.execute(query)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    # Looks for a sessionID in the DB. Return None if not found, else returns the row
    def getSession (self, sessionID):
        query = 'SELECT * FROM Sessions WHERE session_ID="%s";' % (sessionID)
        self.cursor.execute(query)
        self.db.commit()
        rowset = self.cursor.fetchall()
        if len(rowset)==0: return None
        else: return rowset[0]

    # Removes a sessionID from the DB
    def removeSession (self, sessionID):
        query = 'DELETE FROM Sessions WHERE session_ID="%s";' % (sessionID)
        self.cursor.execute(query)
        self.db.commit()

    # Removes expired sessions from the DB
    # Normal sessions use their expiration datetime, while session-long sessions
    # are considered expired after 24 hours
    def removeExpiredSessions (self):
        query = 'DELETE FROM Sessions WHERE (type="normal" AND UTC_TIMESTAMP() > expiration) OR (type="session" and UTC_TIMESTAMP() > ADDDATE(issue, INTERVAL 24 HOUR));'
        self.cursor.execute(query)
        self.db.commit()

    # Looks for a player in the DB. Builds and returns a Player object if found, or returns None if not
    def getPlayer (self, username):
        query = 'SELECT * FROM Players WHERE user_name="%s";' % (username)
        self.cursor.execute(query)
        self.db.commit()
        rowset = self.cursor.fetchall()
        if len(rowset)==0: return None
        else: return Player(rowset[0])

    # Extracts forecasts for the given player and week, 
    # and returns them as a dict
    def loadForecasts(self, username, week):
        query = 'SELECT * FROM Forecasts WHERE user_name="%s" AND match_week=%i;' % (username, week)
        self.cursor.execute(query)
        self.db.commit()
        rowset = self.cursor.fetchall()
        forecasts = {}
        for row in rowset: forecasts[row[0]] = row[2]
        return forecasts

    # Loads forecasts for the given list of match IDs and for the given player
    # and returns them as a dict
    def loadForecastList (self, username, matchIDs):
        if len(matchIDs) == 0: return None
        query_list = " OR ".join(['match_id="%s"' % x for x in matchIDs])
        query = 'SELECT * FROM Forecasts WHERE user_name="%s" AND (%s);' % (username, query_list)
        self.cursor.execute(query)
        self.db.commit()
        rowset = self.cursor.fetchall()
        forecasts = {}
        for row in rowset: forecasts[row[0]] = row[2]
        return forecasts

    # Adds a new forecast to the DB
    def addForecast(self, matchid, username, pick, week):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = 'INSERT INTO Forecasts VALUES ("%s","%s","%s",%i,"%s");' % (matchid, username, pick, week, now)
        self.cursor.execute(query)
        self.db.commit()

    # Updates an existing forecast
    def updateForecast(self, matchid, username, pick):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = 'UPDATE Forecasts SET pick="%s", last_change="%s" WHERE user_name="%s" AND match_id="%s";' % (pick, now, username, matchid)
        self.cursor.execute(query)
        self.db.commit()

    # Extracts all scores for the given player
    # Returns a tuple with (global_score, global_misses, global_rank, points_list[], misses_list[], rank_list[])
    def loadScores(self, username):
        query = 'SELECT * FROM Scores WHERE user_name="%s"' % (username)
        self.cursor.execute(query)
        self.db.commit()
        rows = self.cursor.fetchall()
        data = rows[0]
        response = (data[1], data[2], data[3], data[4], data[5::2], data[6::2])
        return response

    # Updates the status, home and away scores, and winner of a given match ID
    def updateMatch(self, id, status, away_score, home_score, winner):
        ascore = "NULL" if away_score == None else "%i" % (away_score)
        hscore = "NULL" if home_score == None else "%i" % (home_score)
        winner = "NULL" if winner == None else "\"%s\"" % (winner)
        query = 'UPDATE Matches SET status="%s", away_score=%s, home_score=%s, winner=%s WHERE id="%s";' % (status, ascore, hscore, winner, id)
        self.cursor.execute(query)
        self.db.commit()

    # Updates the stored scores using the passed player
    def updateScores(self, player):
        # Build query
        query = 'UPDATE Scores SET '
        query += 'global_score=%i' % player.GlobalScore
        query += ',global_misses=%i' % player.GlobalMisses
        query += ',global_rank=%i' % player.GlobalRank
        query += ',prev_rank=%i' % player.PrevRank
        for w in range(1,17+1):
            query += ",week%i_score=%i" % (w, player.WeekPoints[w-1])
            query += ",week%i_misses=%i" % (w, player.WeekMisses[w-1])
        query += ' WHERE user_name="%s";' % player.Username
#        print query
        self.cursor.execute(query)
        self.db.commit()

    # Registers a password change ticket for the given player
    # If a ticket is already issued, it will be overwritten
    def issuePswdChangeTicket(self, username, ticketID):
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        query = 'INSERT INTO PswdTickets VALUES ("%s", "%s", "%s") ON DUPLICATE KEY UPDATE ticket="%s",issue_date="%s";' % (username, ticketID, now, ticketID, now)
        self.cursor.execute(query)
        self.db.commit()

    # Recovers the password change ticket for the given player
    # If no ticket found, returns None
    def readPswdChangeTicket(self, ticketID):
        query = 'SELECT * FROM PswdTickets WHERE ticket="%s";' % (ticketID)
        self.cursor.execute(query)
        self.db.commit()
        rowset = self.cursor.fetchall()
        if len(rowset)==0: return None
        else: return rowset[0][0]

    # Erases the password change ticket for the given player
    def erasePswdChangeTicket(self, username):
        query = 'DELETE FROM PswdTickets WHERE user_name="%s";' % (username)
        self.cursor.execute(query)
        self.db.commit()

    # Changes the password hash of a user
    # The user must exist
    def changeUserPassword(self, username, newPswdHash):
        query = 'UPDATE Players SET pswd_hash="%s" WHERE user_name="%s";' % (newPswdHash, username)
        self.cursor.execute(query)
        self.db.commit()
        rowset = self.cursor.fetchall()
        if len(rowset) == 0: return False
        else: return True

# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# Live scores fetching
# =====================================

# Simple object to hold live  match data
class liveMatchData:
    def __init__(self, ID, EID=None, AScore=None, HScore=None, Status=None, PossTeam=None, Yardline=None, Down=None, ToGo=None, Redzone=False):
        self.EID = EID
        self.AScore = AScore
        self.HScore = HScore
        self.Status = Status
        self.PossTeam = PossTeam
        self.Yardline = Yardline
        self.Down = Down
        self.ToGo = ToGo
        self.Redzone = Redzone

# Receives a list of Match objects and overwrites their statuses
# and scores if live info is available from the web
def pollLiveScores(Matches, week):

    liveMatches = {}
    
    # Fetch week XML document and parse match data
    xmldoc = xml.parse(urllib2.urlopen("http://www.nfl.com/liveupdate/scorestrip/ss.xml",timeout=30))
    xmlWeek = xmldoc.getElementsByTagName('gms')[0].getAttribute('w')
    xmlMatches = xmldoc.getElementsByTagName('g')
    for m in xmlMatches:
        xmlID = "W%s-%s@%s" % (xmlWeek, m.getAttribute('v'), m.getAttribute('h'))
        xmlEID = m.getAttribute('eid')
        xmlAScore = m.getAttribute('vs')
        xmlHScore = m.getAttribute('hs')
        Status = m.getAttribute('q')
        if (Status=='P'):
            xmlStatus = "Pregame"
        elif (Status=='F' or Status=='FO'):
            xmlStatus = "Final"
        elif (Status=='H'):
            xmlStatus = "Half"
        else:
            remaining = m.getAttribute('k')
            xmlStatus = "Q%s %s" % (Status, remaining)
        liveMatches[xmlID] = liveMatchData(xmlID, xmlEID, xmlAScore, xmlHScore, xmlStatus)

    # Fetch per-match real-time info from json files
    for ID in liveMatches:
        if liveMatches[ID].Status in ["Pregame", "Final", "Half"]: continue
        EID = liveMatches[ID].EID
        if EID == None: continue
        try:
            jsonurl = "http://www.nfl.com/liveupdate/game-center/%s/%s_gtd.json" % (EID, EID)
            jsondoc = json.load(urllib2.urlopen(jsonurl,timeout=30))
            if "posteam" in jsondoc[EID]:
                liveMatches[ID].PossTeam = jsondoc[EID]["posteam"]
                # HACK because realtime info still uses JAC instead of JAX
                if liveMatches[ID].PossTeam == "JAC": liveMatches[ID].PossTeam = "JAX"
            if "yl" in jsondoc[EID]:
                liveMatches[ID].Yardline = jsondoc[EID]["yl"]
            if "down" in jsondoc[EID]:
                liveMatches[ID].Down = jsondoc[EID]["down"]
            if "togo" in jsondoc[EID]:
                liveMatches[ID].ToGo = jsondoc[EID]["togo"]
            if "redzone" in jsondoc[EID]:
                liveMatches[ID].Redzone = jsondoc[EID]["redzone"]
        except:
            continue

    # Overwrite current match data if live data is available
    for m in Matches:
        ID = m.MatchID
        if ID in liveMatches:
            m.AwayScore = int(liveMatches[ID].AScore)
            m.HomeScore = int(liveMatches[ID].HScore)
            m.Status = liveMatches[ID].Status
            m.PossTeam = liveMatches[ID].PossTeam
            m.Yardline = liveMatches[ID].Yardline
            m.Down = liveMatches[ID].Down
            m.ToGo = liveMatches[ID].ToGo
            m.Redzone = liveMatches[ID].Redzone



# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# Match Auto Updater
# =====================================

# Receives a list of Matches with supposedly live data and
# updates finalized matches that are out of the date in the DB
def autoUpdater(Matches, week):
    
    # TEMPORARY LOGGING FOR DEBUGGING PURPOSES
    dolog = True
    if (dolog):
        logfile = open("/home/meithann/public_html/NFL%i/logs/autoupdater.log" % (season), "a")
        logfile.write("\n========================================\n")
        logfile.write(get_utcnow().isoformat())
        logfile.write("\nRunning autoupdater ...\n")

    # Load stored matches from DB
    db = DBHelper()
    db.Connect()
    stored_Matches = db.loadMatches(week)

    # Put passed matches into dict for more efficient comparison
    live_Matches = {}
    for m in Matches:
        live_Matches[m.MatchID] = m

    # Compare stored matches to live matches
    # Update DB for out-of-date matches
    update_applied = False
    for m1 in stored_Matches:
        if m1.MatchID in live_Matches:
            m2 = live_Matches[m1.MatchID]
            if (dolog): logfile.write("Checking match %s ... " % m2.MatchID)
            if m2.Status == "Final" and m1.Status != "Final":
                if (dolog): logfile.write("More recent live data found! Updating DB ...\n")
                db.updateMatch(m1.MatchID, "Final", m2.AwayScore, m2.HomeScore, m2.getWinner())
                update_applied = True
            else:
                if (dolog): logfile.write("No newer data\n")

    # Close DB connection
    db.Close()

    # If at least one update was made, recompute and update scores/ranks
    if update_applied:
        if (dolog): logfile.write("Match update triggered scores and ranks update ...\n")
        updateScoresRanks()

    if (dolog): logfile.write("Autoupdater done.\n")
    if (dolog): logfile.close()

# =====================================
# Directly updates the stored info of a match
# =====================================
def updateMatch(MatchID, status, ascore, hscore, winner):
    db = DBHelper()
    db.Connect()
    db.updateMatch(MatchID, status, ascore, hscore, winner)
    db.Close()

# =====================================
# Recomputes and updates all scores and ranks
# To be called after a match is updated
# =====================================
def updateScoresRanks():

    # TEMPORARY LOGGING FOR DEBUGGING PURPOSES
    dolog = True
    if (dolog):
        logfile = open("/home/meithann/public_html/NFL%i/logs/updateScoresRanks.log" % (season), "a")
        logfile.write("\n================================================================================\n")
        logfile.write(get_utcnow().astimezone(mexicoTZ).isoformat())
        logfile.write("\nRecomputing and updating scores and ranks ...\n")

    # Get current week
    cur_week = getCurrentWeek(get_utcnow())

    db = DBHelper()
    db.Connect()
    Players = db.loadPlayers()

    # Reset player scores and ranks
    for p in Players:
        p.GlobalScore = 0
        p.GlobalMisses = 0
        p.PrevScore = 0
        p.GlobalRank = 0
        p.PrevRank = 0
        p.WeekPoints = [0]*17
        p.WeekMisses = [0]*17
        p.GlobalPercent = 0.0
        
    # Compute scores for all weeks up to current week
    # Uses the LastPoint temp Player var to store last point
    for week in range(1,cur_week+1):
        for p in Players: p.loadForecasts(week)
        Matches = db.loadMatches(week)
        Matches.sort(key=lambda x: x.DateTime)  # sort matches by date
        num_matches = len(Matches)
        # Now count up scores
        for i,match in enumerate(Matches):
            if match.isFinal():
                latest_week = week
                if (dolog): logfile.write("Counting score for %s\n" % match.MatchID)
                for p in Players:
                    if (match.MatchID in p.Forecasts):
                        if (match.Winner==p.Forecasts[match.MatchID]):
                            if (dolog): logfile.write("%s: SCORE\n" % p.Username)
                            p.WeekPoints[week-1] += 1
                        elif match.Winner!="TIE":
                            if (dolog): logfile.write("%s: MISS\n" % p.Username)
                            p.WeekMisses[week-1] += 1
                        else:
                           if (dolog): logfile.write("%s: TIE -- ignoring\n" % p.Username)
                    else:
                        if (dolog): logfile.write("%s entered NO forecast\n" % p.Username)

    # Latest week is the most recent week with at least one completed match
    latest_week = max(latest_week,1)
    if (dolog): logfile.write("LATEST WEEK = %i\n" % latest_week)

    # Count up scores
    for p in Players:
        p.GlobalScore = sum(p.WeekPoints)
        p.GlobalMisses = sum(p.WeekMisses)
        p.PrevScore = sum(p.WeekPoints[:latest_week-1])
        if (p.GlobalScore+p.GlobalMisses)!=0:
            p.GlobalPercent = (p.GlobalScore*1.0)/(p.GlobalScore+p.GlobalMisses)
        else:
            p.GlobalPercent = 0.0
        print p.Username, p.WeekPoints, "<br>"
           
    # Now determine rankings - previous ranking first
    Players.sort(key=lambda x: x.PrevScore, reverse=True)
    lastrank = 1
    for i in range(len(Players)):
        if i==0:
            Players[i].PrevRank = 1
        else:
            if Players[i].PrevScore == Players[i-1].PrevScore:
                Players[i].PrevRank = lastrank
            else:
                Players[i].PrevRank = i+1
                lastrank = i+1

    # Determine current rankings
    Players.sort(key=lambda x: x.GlobalScore, reverse=True)
    lastrank = 1
    for i in range(len(Players)):
        if i==0:
            Players[i].GlobalRank = 1
        else:
            if Players[i].GlobalScore == Players[i-1].GlobalScore:
                Players[i].GlobalRank = lastrank
            else:
                Players[i].GlobalRank = i+1
                lastrank = i+1

    for p in Players:
        print "%s is now %i-%i (%f), prev score %i -- new rank: %i, prev rank: %i<br>" % (p.Username, p.GlobalScore, p.GlobalMisses, p.GlobalPercent, p.PrevScore, p.GlobalRank, p.PrevRank)

    if (dolog):
        for p in Players:
            logfile.write("%s is now %i-%i (%f), prev score %i -- new rank: %i, prev rank: %i\n" % (p.Username, p.GlobalScore, p.GlobalMisses, p.GlobalPercent, p.PrevScore, p.GlobalRank, p.PrevRank))

    # Now that all's been recomputed, update DB
    if (dolog): logfile.write("Updating DB ...\n")
    for p in Players:
        db.updateScores(p)
    
    db.Close()

    if (dolog): logfile.close()

    
# =====================================
# Backups a database table to file
# =====================================
# Not part of the DBHelper class because it
# uses an external command (mysqldump)
def backupTable(tbl_name):

    from config import mysql_dbname, mysql_username, mysql_password

    # Number of backups to keep for each table
    numBackups = 20

    # Erase older backup(s) if 10 or more already exist
    files = os.listdir("/home/meithann/public_html/NFL%i/backups/" % (season))
    files = [fname for fname in files if tbl_name in fname]
    files.sort()
    if len(files) >= numBackups:
        to_remove = files[:len(files)-numBackups+1]
        for fname in to_remove:
            os.remove(("/home/meithann/public_html/NFL%i/backups/" % (season)) + fname)

    # Backup table
    stamp = datetime.datetime.utcnow().isoformat()
    fname = "/home/meithann/public_html/NFL%i/backups/%s%s.sql" % (season, tbl_name, stamp)
    f = open(fname,"w")
    p = subprocess.Popen(["mysqldump","--user=%s" % mysql_username, "--password=%s" % mysql_password, mysql_dbname, tbl_name], stdout=f)
    f.close()


# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#

# =====================================
# Class definitions
# =====================================

# Team class definition - redesigned for MySQL
class Team:

    def __init__(self, data):
        self.ID = data[0]
        self.City = data[1]
        self.Name = data[2]
        self.Conf = data[3]
        self.Wins = data[4]
        self.Losses = data[5]
        self.Ties = data[6]

    def __repr__(self):
        return "&lt;" + "Team instance: " + self.ID + "&gt;"

    def scorestr (self):
        if ((self.Wins != None) and (self.Losses != None)):
            if (self.Ties >= 1):
                return "(%i-%i-%i)" % (self.Wins, self.Losses, self.Ties)
            else:
                return "(%i-%i)" % (self.Wins, self.Losses)
        else:
            return ""

    def name(self):
        return self.Name
       
# =====================================

# Match class definition - redesigned for MySQL
class Match:

    def __init__(self, data):
        # Data array must contain the following elements (all strings but the week and scores)
        # MatchID, Week, DateTime, TZone, AwayTeam, HomeTeam, Status, AwayScore, HomeScore, Winner
        # Can also optionally include two extra fields: Posession (team ID) and Redzone indicator (boolean)
        self.MatchID = data[0]
        self.Week = data[1]
        foo = data[2] + " " + data[3]
        if (data[4]=='CDT'): tz=CDT
        elif (data[4]=='CT'): tz=CT
        elif (data[4]=='EDT'): tz=EDT
        elif (data[4]=='ET'): tz=ET
        elif (data[4]=='UTC'): tz=UTC
        else: tz=UTC
        self.DateTime = datetime.datetime.strptime(foo,"%Y-%m-%d %H:%M").replace(tzinfo=tz)
        self.Date = self.DateTime.date()
        self.Time = self.DateTime.time()
        self.AwayTeam = data[5]
        self.HomeTeam = data[6]
        self.Status = data[7]
        self.AwayScore = data[8]
        self.HomeScore = data[9]
        self.Winner = data[10]
        # Extra data (to be filled by live scores polling)
        self.PossTeam = None
        self.Redzone = False
        self.Yardline = None
        self.Down = None
        self.ToGo = None

    def __repr__(self):
        return "&lt;" + "Match instance: " + self.MatchID + "&gt;"

    def pastStart(self):
        if self.isFinal(): return True   # Finalized matches are always considered past start
        now = get_utcnow()
#        now = datetime.datetime.now(serverTZ)   ## This is not server-timezone-agnostic, the above is
#        now = datetime.datetime(2016, 9, 8, 20, 0, 0, tzinfo=mexicoTZ)   ### DEBUG
        if (now >= self.DateTime): return True
        else: return False

    def isFinal(self):
        if self.Status=="Final": return True
        else: return False

    def hasScore(self):
        if (self.AwayScore != None and self.HomeScore != None): return True
        else: return False

    def getWinner(self):
        if self.Winner != None: return self.Winner
        else:
            if self.isFinal() and self.hasScore():
                if self.AwayScore > self.HomeScore: return self.AwayTeam
                elif self.AwayScore < self.HomeScore: return self.HomeTeam
                else: return "TIE"
            else:
                return None

    def downString(self):
        if self.Down == None or self.ToGo == None: return ""
        if self.Down == 1: return "1st & %s" % self.ToGo
        elif self.Down == 2: return "2nd & %s" % self.ToGo
        elif self.Down == 3: return "3rd & %s" % self.ToGo
        elif self.Down == 4: return "4th & %s" % self.ToGo
        else: return ""


# =====================================

# Player class definition - redesigned for MySQL
class Player:

    def __init__(self,data):
        self.Username = data[0]
        self.Fullname = data[1]
        self.email = data[2]
        self.PswdHash = data[3]
        self.paid = data[4]
        self.Forecasts = {}
        self.sessionID = None
        self.GlobalScore = None
        self.GlobalMisses = None
        self.PrevScore = None
        self.GlobalRank = None
        self.PrevRank = None
        self.WeekPoints = None
        self.WeekMisses = None
        self.GlobalPercent = None

    def loadForecasts(self, week):
        db = DBHelper()
        db.Connect()
        self.Forecasts = db.loadForecasts(self.Username, week)
        db.Close()

    def loadScores(self):
        db = DBHelper()
        db.Connect()
        data = db.loadScores(self.Username)
        db.Close()
        self.GlobalScore = data[0]
        self.GlobalMisses = data[1]
        self.GlobalRank = data[2]
        self.PrevRank = data[3]
        self.WeekPoints = data[4]
        self.WeekMisses = data[5]
        if (self.GlobalScore == None or self.GlobalMisses == None):
           self.GlobalPercent = None
        elif (self.GlobalScore+self.GlobalMisses)!=0:
            self.GlobalPercent = (self.GlobalScore*1.0)/(self.GlobalScore+self.GlobalMisses)
        else:
            self.GlobalPercent = 0

    def __repr__(self):
        return "&lt;" + "Player instance: " + self.Username + "&gt;"

# =#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
        
# =====================================
# Statistics
# =====================================

# Returns the factorial of N, recursively calculated
def fact(N):
    if (N==0): return 1
    else: return N*fact(N-1)

# Returns the Binomial function B(N,p,x)
def Binomial(N,p,x):
    return fact(N)/fact(N-x)/fact(x)*pow(p,x)*pow(1-p,N-x)

# Returns the accumulated probability of doing *as good or better* than x out of N correct guesses
def Luck(N,p,x):
    S = 0
    for k in range(x,N+1):
        S += Binomial(N,p,k)
    return S
