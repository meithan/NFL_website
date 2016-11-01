#!/usr/bin/env python

# Generates the Players page (with a list of players and, importantly, payments)
import cgi, cgitb
cgitb.enable()
from common import *

# =========================

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# Load Players from DB
db = DBHelper()
db.Connect()
Players = db.loadPlayers()
db.Close()

Players.sort(key=lambda x: x.Username.lower())

# =========================

print "Content-type:text/html\r\n\r\n"
print '<!DOCTYPE html>'
print '<html lang="en">'
print '<head>'
bootstrapHeader()
print '<title>Quiniela NFL %i</title>' % (season)
print '</head>'
print '<body>'

bootstrapNavbar("Players",logged_user)

print '<div class="container">'

print '<h3>Lista de Participantes</h3>'
print '<br>'

print '<div class="table-responsive">'
print '<table class="table table-striped table-bordered table-hover main-table table-left-align">'
print '<thead>'
print '<tr>'
print '<td class="header">#</td>'
print '<td class="header">Usuario</td>'
print '<td class="header">Nombre real</td>'
print '<td class="header">Pago</td>'
print '</tr>'
print '</thead>'

for i,p in enumerate(Players):
    print '<tr>'
    print '<td>%i</td>' % (i+1)
    print '<td>%s</td>' % (p.Username)
    print '<td>%s</td>' % (p.Fullname)
    print '<td style="text-align: center;">%s</td>' % ("&#10004;" if p.paid else "&nbsp;")
    print '</tr>'

print '</table>'
print '</div>'
print '</div>'

bootstrapFooter()

print '</body>'
print '</html>'