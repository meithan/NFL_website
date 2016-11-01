#!/usr/bin/env python

# Password change ticket generator
import md5
import cgi, cgitb
cgitb.enable()
import os
import sys
import string
import random
from common import *
import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart

# Page header, using bootstrap
def outputPageHeader():
    print "Content-type:text/html"
    print
    print '<!DOCTYPE html>'
    print '<html lang="en">'
    print '<head>'
    bootstrapHeader()
    print '<title>Quiniela Brasil %i</title>' % (season)
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
# Generate "user not found" page
def userNotFoundPage(user, Players):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Usuario no encontrado</h3>'
    print '&iexcl;No se encontr&oacute; el nombre de usuario <strong>%s</strong>!' % (user)
    print '<br><a href="javascript:history.go(-1)">Regresa</a> e intenta de nuevo.'
    print Players, "<br>"
    print '</div>'
    outputPageFooter()
# ----------------------------------
def TicketSentPage (user):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Ticket enviado</h3>'
    print 'Se te envi&oacute; por email un <em>ticket</em> para que puedas cambiar tu contrase&ntilde;a, <strong>%s</strong>.' % (user)
    print '<br>Sigue las instrucciones en el email para completar el proceso.'
    print '<br><br>Volver a la <a href="http://meithan.net">p&aacute;gina principal</a>.'
    print '</div>'
    outputPageFooter()
# ----------------------------------
def ErrorPage (user, response):
    outputPageHeader()
    print '<div class="container">'
    print '<h3>Error</h3>'
    print 'Lo sentimos, <strong>%s</strong>, hubo un problema en el env&iacute;o del <em>ticket</em>. Reporta este error al administrador.' % (user)
    print '<br><br>Volver a la <a href="http://meithan.net">p&aacute;gina principal</a>.'
    print '<br><br><strong>Error report</strong>'
    if (response != None):
        print '<br>mailserver response dict:'
        for key in response:
            print '<br>%s: %s' % (repr(key), repr(response[key]))
    else:
        print '<br>mailserser response dict is NoneType' 
    print '</div>'
    outputPageFooter()
# ----------------------------------
def sendTicketByEmail (user, user_email, ticket):

    from config import mailserver_host, mailserver_port, mailserver_username, mailserver_password

    subject = "Cambio de contrase=C3=B1a"
    subject = "=?utf-8?Q?" + subject + "?="
    sender_name = "Quiniela NFL %i" % (season)
    sender_email = "webmaster@meithan.net"
    server = mailserver_host
    port = mailserver_port
    login = mailserver_username
    pswd = mailserver_password

    mailserver = smtplib.SMTP(server,port)
    resp = mailserver.starttls()
    resp = mailserver.ehlo()
    resp = mailserver.login(login, pswd)

    htmlbody = "Hola, %s.<br><br>Haz clic en el link siguiente para crear una nueva contrase&ntilde;a. El link s&oacute;lo podr&aacute; ser usado una vez. Si no solicitaste un cambio de contrase&ntilde;a, ignora este email.<br><br>http://meithan.net/NFL%i/cgi-bin/PswdChangeFormPage.py?ticket=%s" % (user, season, ticket)

    plainbody = "Hola, %s. Haz clic en el link siguiente para crear una nueva contrasenia. El link solo podra ser usado una vez. Si no solicitaste un cambio de contrasenia, ignora este email. http://meithan.net/NFL%i/cgi-bin/PswdChangeFormPage.py?ticket=%s" % (user, season, ticket)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_name + " <%s>" % (sender_email)
    msg['To'] = user_email

    part1 = MIMEText(plainbody, 'plain')
    part2 = MIMEText(htmlbody , 'html')
    msg.attach(part1)
    msg.attach(part2)

    response = mailserver.sendmail(login, [user_email], msg.as_string())

    mailserver.quit()
    return response

# ----------------------------------

# Get form data and Players list
form = cgi.FieldStorage()

# Exit if username is blank
if not form.has_key("Username"):
    userNotFoundPage("")
    sys.exit()

db = DBHelper()
db.Connect()
Players = db.loadPlayers()

# Check if user exists
Username = form["Username"].value
UserNotFound = True
for p in Players:
    if (p.Username.lower() == Username.lower()): 
        UserNotFound = False
        user_email = p.email
        break
if UserNotFound:
    userNotFoundPage(Username, Players)
    sys.exit()

# Generate a new ticket ID
charPool = string.ascii_lowercase + string.digits
ticketID = ""
for i in range(20):
    ticketID += random.choice(charPool)

# Register password change ticket in DB
# Only one ticket per user is possible
db = DBHelper()
db.Connect()
db.issuePswdChangeTicket(Username, ticketID)
db.Close()

# Send ticket by email
response = sendTicketByEmail (Username, user_email, ticketID)
#response = {}

if response == {}:
  TicketSentPage (Username)
else:
  ErrorPage (Username, response)

