#!/usr/bin/env python

# Generates the Prizes Page (with the distribution of prizes assuming current ranking)
import cgi, cgitb
cgitb.enable()
from common import *

# --------------------------------

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

# Generate Prizes Page
# Build HTML document
print "Content-type:text/html"
print
print '<!DOCTYPE html>'
print '<html lang="en">'

# Header
print '<head>'
bootstrapHeader()
print '<title>Quiniela NFL %i</title>' % (season)
print '</head>'

# body
print '<body>'

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# Navbar
bootstrapNavbar("Prizes",logged_user)

# --------------------------------

# Page layout
print
print '<div class="container">'

# Page body title
#print '<h3>La Quiniela NFL %i ha concluido. Los ganadores son:</h3>' % (season)
print '<h3>Si la quiniela terminara ahora, los ganadores ser&iacute;an ...</h3>'
print '<br>'

# Sort Players and determine rankings
Players = sorted(Players, key=lambda x: x.Username.lower())
Players = sorted(Players, key=lambda x: x.GlobalScore, reverse=True)
rankings= [0]*numPlayers
for i in range(numPlayers):
    if i == 0:
        rankings[i] = 1
        lastrank = 1
    else:
        if Players[i].GlobalScore == Players[i-1].GlobalScore:
            rankings[i] = lastrank
        else:
            rankings[i] = i+1
            lastrank = i+1
if len(Players) > 0: leaderScore = Players[0].GlobalScore
else: leaderScore = 0

# Determine prizes
# The following assumes 'rankings' is a valid ranking list

rawpot = numPlayers*entry_cost
totpot = rawpot - len(perfect_awards)*perfect_bonus
pot1 = totpot*0.5
pot2 = totpot*0.3
pot3 = totpot*0.2
firstplaces = rankings.count(1)
secondplaces = rankings.count(2)
thirdplaces = rankings.count(3)

prize1 = None
prize2 = None
prize3 = None
if thirdplaces == 0 and secondplaces == 0:
  prize1 = (pot1+pot2+pot3)/firstplaces
elif thirdplaces == 0 and secondplaces > 0:
  prize1 = pot1
  prize2 = (pot2+pot3)/secondplaces
elif thirdplaces > 0 and firstplaces > 1:
  prize1 = (pot1+pot2)/firstplaces
  prize3 = (pot3)/thirdplaces
elif thirdplaces > 0 and firstplaces == 1:
  prize1 = pot1
  prize2 = pot2
  prize3 = pot3/thirdplaces

# Print table

print '<div class="table-responsive">'
print '<table class="table table-bordered table-condensed main-table table-left-align">'
print '<thead>'
print '<tr class="yellow-header">'
print '<td>Lugar</td>'
print '<td>Jugador</td>'
print '<td>Premio</td>'
print '</tr>'
print '</thead>'

# First prizes
print '<tr><td rowspan="%i" style="vertical-align: middle; border-bottom: 1px solid black;">1er Lugar</td>' % (firstplaces)
if firstplaces==1:
    style = ' style="border-bottom: 1px solid black;"'
else:
    style = ''
print '<td%s>%s</td>' % (style, Players[0].Username)
print '<td%s>$%.2f</td>' % (style, prize1)
print '</tr>'
nextp = 1
for i in range(firstplaces-1):
    if i==(firstplaces-2):
        style = ' style="border-bottom: 1px solid black;"'
    else:
        style = ''
    print '<tr>'
    print '<td%s>%s</td>' % (style, Players[nextp].Username)
    print '<td%s>$%.2f</td>' % (style, prize1)
    print '</tr>'
    nextp += 1

# Second prizes
if prize2 == None:
    print '<tr><td colspan="3" style="border-bottom: 1px solid black; text-align: center;">Sin 2do Lugar</td></tr>'
else:
    print '<tr><td rowspan="%i" style="vertical-align: middle; border-bottom: 1px solid black; text-align: center;">2do Lugar</td>' % (secondplaces)
    if secondplaces==1:
        style = ' style="border-bottom: 1px solid black;"'
    else:
        style = ''
    print '<td%s>%s</td>' % (style, Players[nextp].Username)
    nextp += 1
    print '<td%s>$%.2f</td>' % (style, prize2)
    print '</tr>'
    for i in range(secondplaces-1):
        if i==(secondplaces-2):
            style = ' style="border-bottom: 1px solid black;"'
        else:
            style = ''
        print '<tr>'
        print '<td%s>%s</td>' % (style, Players[nextp].Username)
        nextp += 1
        print '<td%s>$%.2f</td>' % (style, prize2)
        print '</tr>'

# Third prizes
if prize3 == None:
    print '<tr><td colspan="3" style="text-align: center;">Sin 3er Lugar</td></tr>'
else:
    print '<tr><td rowspan="%i" style="vertical-align: middle;">3er Lugar</td>' % (thirdplaces)
    print '<td>%s</td>' % (Players[nextp].Username)
    nextp += 1
    print '<td>$%.2f</td>' % (prize3)
    print '</tr>'
    for i in range(thirdplaces-1):
        print '<tr>'
        print '<td>%s</td>' % (Players[nextp].Username)
        nextp += 1
        print '<td>$%.2f</td>' % (prize3)
        print '</tr>'

print '</table>'

print '<table class="table table-bordered table-condensed main-table table-left-align">'
print '<thead>'
print '<tr class="yellow-header">'
print '<td>Ganadores Semana Perfecta: %i</td>' % (len(perfect_awards))
print '</tr>'
print '</thead>'
print '<tr><td>%s</td></tr>' % (",".join(perfect_awards))
print '</table>'

print '<h4>Bolsa Total: $%i</h4>' % (rawpot)
print '<h4>Bonos a Semana Perfecta: $%i</h4>' % (len(perfect_awards)*perfect_bonus)
print '<h4>Bolsa de 1ero, 2do y 3er lugar: $%i</h4>' % (totpot)

print '</div>'
print '</div>'

bootstrapFooter()

print '</body>'
print '</html>'