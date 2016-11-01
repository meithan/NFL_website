#!/usr/bin/python

# Password change script
import md5
import cgi, cgitb
cgitb.enable()
import os
import sys
import string
from common import *

# Page header, using bootstrap
def outputPageHeader():
    print "Content-type:text/html\r\n\r\n"
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
# Generate "incomplete form" page
def incompleteForm():
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Datos incompletos</h3>'
    print 'Debes llenar todos los campos.'
    print '<br><a href="javascript:history.go(-1)">Regresa</a> e intenta de nuevo.'
    print '</div>'
    outputPageFooter()

# ----------------------------------
# Generate "password changed successfully" page
def showSuccess(user):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Cambio de contrase&ntilde;a exitoso</h3>'
    print '&iexcl;Tu contrase&ntilde;a ha sido cambiada, <b>%s</b>!' % (user)
    print '<br>Volver al <a href="http://meithan.x10.mx">sitio principal</a>.'
    print '</div>'
    outputPageFooter()

# ----------------------------------
# Generate "invalid new password" page
def invalidNewPswd():
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Contrase&ntilde;a nueva inv&aacute;lida</h3>'
    print 'Tu contrase&ntilde;a s&oacute;lo puede contener caracteres alfanum&eacute;ricos y guiones.'
    print '<br><a href="javascript:history.go(-1)">Regresa</a> e intenta de nuevo.'
    print '</div>'
    outputPageFooter()

# ----------------------------------
# Generate "unmatched new password" page
def unmatchedNewPswd():
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Confirmaci&oacute;n no coincide</h3>'
    print '&iexcl;El campo de confirmaci&oacute;n de tu nueva contrase&ntilde;a no coincide!'
    print '<br><a href="javascript:history.go(-1)">Regresa</a> e intenta de nuevo.'
    print '</div>'
    outputPageFooter()

# ----------------------------------
# Generate "generic error" page
def ErrorPage (user):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Error</h3>'
    print 'Lo sentimos, <strong>%s</strong>, hubo un problema con el cambio de contrase&ntilde;a. Reporta este error al administrador.' % (user)
    print '<br><br>Volver a la <a href="http://meithan.x10.mx">p&aacute;gina principal</a>.'
    print '</div>'
    outputPageFooter()
# ----------------------------------

# Get form data and Players list
form = cgi.FieldStorage()
db = DBHelper()
db.Connect()
Players = db.loadPlayers()

# Exit if incomplete form
if (not form.has_key("Username") or \
    not form.has_key("NewPswd") or \
    not form.has_key("NewPswdConf")):
    incompleteForm()
    sys.exit()

Username = form["Username"].value
NewPswd = form["NewPswd"].value
NewPswdConf = form["NewPswdConf"].value

# Check if new password has valid chars
validChars = string.ascii_letters + string.digits + "_-"
invalidPswd = False
for c in NewPswd:
    if (c not in validChars): 
        invalidPswd = True
        break
if (invalidPswd):
    invalidNewPswd()
    db.Close()
    sys.exit()

# Check if password confirmation is good
if (NewPswd!=NewPswdConf):
    unmatchedNewPswd()
    db.Close()
    sys.exit()

# All good. Generate and store new password hash.
NewPswdHash = md5.new(NewPswd).hexdigest()
try: db.changeUserPassword(Username, NewPswdHash)
except:
    ErrorPage(Username)
    db.Close()
    sys.exit()

# Eliminate used ticket from DB
db.erasePswdChangeTicket(Username)

db.Close()

# Report success
showSuccess(Username)



