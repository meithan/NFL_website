#!/usr/bin/env python

# Registration Script
import md5
import cgi, cgitb
cgitb.enable()
from common import *

# =========================

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# Connect to MySQL database
db = DBHelper()
db.Connect()

# =========================

# Page header, using bootstrap
def outputPageHeader():
    print "Content-type:text/html\r\n\r\n"
    print '<!DOCTYPE html>'
    print '<html lang="en">'
    print '<head>'
    bootstrapHeader()
    print '<title>Registro</title>'
    print '</head>'
    print '<body>'
    bootstrapNavbar("Registration",logged_user)

# Page footer
def outputPageFooter():
    print '</body>'
    print '</html>'

# ----------------------------------
# Generate "invalid characters in username" page
def invalidCharsGen():
    outputPageHeader()
    print '<center>'
    print '<h3>El nombre de usuario contiene caracteres inv&aacute;lidos</h3>'
    print 'Lo sentimos, el nombre de usuario s&oacute;lo puede contener n&uacute;meros y letras (no espacios, no puntuaci&oacute;n, no acentos).'
    print '<br>Regresa e <a href="javascript:history.go(-1)">intenta de nuevo</a>.'
    print '</center>'
    outputPageFooter()

# ----------------------------------
# Generate "duplicate user error" page
def duplicateGen(user):
    outputPageHeader()
    print '<center>'
    print '<h3>El nombre de usuario ya existe</h3>'
    print 'Lo sentimos, el nombre de usuario <b>%s</b> ya est&aacute; tomado.' % (user)
    print '<br>Regresa e <a href="javascript:history.go(-1)">intenta de nuevo</a>.'
    print '</center>'
    outputPageFooter()

# ----------------------------------
# Generate "user registration successful" page
def registeredGen(user):
    outputPageHeader()
    print '<center>'
    print '<h3>Registro exitoso</h3>'
    print '&iexcl;Tu nombre de usuario ha quedado registrado, <b>%s</b>!' % (user)
    print '<br><a href="MainPage.py">Volver</a> al sitio principal.'
    print '</center>'
    outputPageFooter()

# ----------------------------------
# Generate "incomplete data" page
def incompleteGen():
    outputPageHeader()
    print '<center>'
    print '<h3>Datos incompletos</h3>'
    print '&iexcl;Todos los campso son requeridos!'
    print '<br><a href="javascript:history.go(-1)">Regresa</a> e intenta de nuevo.'
    print '</center>'
    outputPageFooter()

# ----------------------------------
# Generate "registration closed" page
def closedGen():
    outputPageHeader()
    print '<center>'
    print '<h3>Registro cerrado</h3>'
    print 'Lo sentimos, el registro se encuentra cerrado.<br>'
    print '<br><a href="MainPage.py">Volver</a> al sitio principal.'
    print '</center>'
    outputPageFooter()

# ----------------------------------
# Generate "unmatched new password" page
def unmatchedConfirmation():
    outputPageHeader()
    print '<center>'
    print '<h3>Confirmaci&oacute;n de contrase&ntilde;a no coincide</h3>'
    print '&iexcl;El campo de confirmaci&oacute;n de tu contrase&ntilde;a no coincide!'
    print '<br><a href="javascript:history.go(-1)">Regresa</a> e intenta de nuevo.'
    print '</center>'
    outputPageFooter()

# ----------------------------------

# Get form data
form = cgi.FieldStorage()
if (registrationClosed): closedGen()
elif (form.has_key("Username") and form.has_key("Password") and \
form.has_key("Fullname") and form.has_key("Email") and form.has_key("PasswordConf")):

    # Get fields from form
    Username = form["Username"].value
    Password = form["Password"].value
    PasswordConf = form["PasswordConf"].value
    Fullname = form["Fullname"].value
    Email = form["Email"].value

    # Stop if username has invalid chars
    if not Username.isalnum(): invalidCharsGen()
    else:

        # Check if username already exists in DB (conversion to lowercase redundant, but oh well)
        query = "SELECT EXISTS(SELECT 1 FROM Players WHERE user_name='%s')" % (Username.lower())
        db.cursor.execute(query)
        duplicate = (db.cursor.fetchone()[0] != 0)

        if (duplicate):
            duplicateGen(Username)
        elif (Password != PasswordConf):
            unmatchedConfirmation()
        else:
            # Add player to Players table
            PswdHash = md5.new(Password).hexdigest()
            db.addPlayer([Username, Fullname, Email, PswdHash])
            # Notify registration success
            registeredGen(Username)
        db.Close()

else:
    incompleteGen()