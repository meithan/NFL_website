#!/usr/bin/python

# Password change script
import cgi, cgitb
cgitb.enable()
from common import *
import os
import sys
import string

# Page header, using bootstrap
def outputPageHeader():
    print "Content-type:text/html"
    print
    print '<!DOCTYPE html>'
    print '<html lang="en">'
    print '<head>'
    bootstrapHeader()
    print '<title>Quiniela NFL %i</title>' % (season)
    print '</head>'
    print '<body>'
    logged_user = authenticateUser()
    bootstrapNavbar("",logged_user)

# Page footer
def outputPageFooter():
    bootstrapFooter()
    print '</body>'
    print '</html>'

# ----------------------------------
# Generate "invalid ticket" page
def invalidTicket():
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Ticket inv&aacute;lido o expirado</h3>'
    print 'El <em>ticket</em> proporcionado no es v&aacute;lido o ha expirado.'
    print '<br>Puedes <a href="/NFL%i/cgi-bin/PswdChangeRequestPage.py">generar otro ticket</a>.' % (season)
    print '</div>'
    outputPageFooter()

# ----------------------------------
# Generate password change page
def PswdChangeForm(user):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Cambio de Contrase&ntilde;a</h3>'
    print 'Ingresa una nueva contrase&ntilde;a, <strong>%s</strong>.<br><br>' % (user)

    print '<form role="form" class="form-horizontal" name="PswdChange" action="/NFL%i/cgi-bin/PswdChange.py" method="post">' % (season)
    print '<input type="hidden" name="Username" value="%s">' % (user)

    print '<div style="width: 50%;">'

    print '<div class="form-group">'
    print '<label class="col-sm-5 control-label" for="inputNewPswd">Nueva constrase&ntilde;a:</label>'
    print '<div class="col-sm-7">'
    print '<input type="password" class="form-control" id="inputNewPswd" placeholder="Nueva contrase&ntilde;a" maxlength="20" name="NewPswd">'
    print '</div>'
    print '</div>'

    print '<div class="form-group">'
    print '<label class="col-sm-5 control-label" for="inputPswdConf">Confirma constrase&ntilde;a:</label>'
    print '<div class="col-sm-7">'
    print '<input type="password" class="form-control" id="inputPswdConf" placeholder="Confirma contrase&ntilde;a" maxlength="20" name="NewPswdConf">'
    print '</div>'
    print '</div>'

    print '<div class="form-group">'
    print '<div class="col-sm-offset-5 col-sm-7">'
    print '<button type="submit" class="btn btn-primary">Enviar</button>'
    print '</div>'
    print '</div>'

    print '</div>'

    print '</form>'
    print '</div>'
    outputPageFooter()
# ----------------------------------

# Get form data and Players list
form = cgi.FieldStorage()

# Exit if incomplete form
if (not form.has_key("ticket")):
    invalidTicket()
    sys.exit()

# Check if ticket exists
ticketID = form["ticket"].value
db = DBHelper()
db.Connect()
username = db.readPswdChangeTicket(ticketID)
ticketFound = (username != None)
db.Close()

if not ticketFound:
    invalidTicket()
    sys.exit()
else:
    PswdChangeForm(username)