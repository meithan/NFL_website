#!/usr/bin/env python

# Generates the Rules page
import cgi, cgitb
cgitb.enable()
from common import *

# =========================

# Determine logged user from cookie, if any
logged_user = authenticateUser()

# =========================

def outputRegClosedPage():

    print "Content-type:text/html"
    print
    print '<!DOCTYPE html>'
    print '<html lang="en">'
    print '<head>'
    bootstrapHeader()
    print '<title>Quiniela NFL %i</title>' % (season)
    print '</head>'
    print '<body>'
    bootstrapNavbar("",logged_user)
    print '<div class="container">'
    print '<h3>&iexcl;Registro cerrado!</h3>'
    print 'Lo sentimos, el registro se encuentra actualmente cerrado. Si crees que esto es un error, contacta al administrador.<br>'
    print '</div>'
    bootstrapFooter()
    print '</body>'
    print '</html>'

def outputRegistrationPage():

    # HTML header
    print "Content-type:text/html\r\n\r\n"
    print '<!DOCTYPE html>'
    print '<html lang="en">'
    print '<head>'
    bootstrapHeader()
    print '</head>'
    print '<body>'

    bootstrapNavbar("Registration",logged_user)
     
    print '<div class="registration">'
    print '<h3>Reglas de la Quiniela NFL %i</h3>' % (season)

    outputRules()

    print '<hr>'

    print '<form class="form-horizontal" name="register" action="/NFL%i/cgi-bin/register.py" method="post">' % (season)
    print '<table class="regtable">'

    print '<tr>'
    print '<td>Nombre de usuario: </td>'
    print '<td><input class="form-control shortinput" type="text" size="12" maxlength="12" name="Username">'
    print '</td>'
    print '</tr>'

    print '<tr>'
    print '<td></td>'
    print '<td><small>M&aacute;ximo 12 caracteres <span style="text-decoration: underline;">alfanum&eacute;ricos</span></small></td>'
    print '</tr>'

    print '<tr>'
    print '<td>Contrase&ntilde;a: </td>'
    print '<td><input class="form-control shortinput" type="password" size="12" maxlength="20" name="Password">'
    print '</td>'
    print '</tr>'

    print '<tr>'
    print '<td>Confirma contrase&ntilde;a: </td>'
    print '<td><input class="form-control shortinput" type="password" size="12" maxlength="20" name="PasswordConf"></td>'
    print '</tr>'

    print '<tr>'
    print '<td></td>'
    print '<td><small>La contrase&ntilde;a es sensible a may&uacute;sculas</small></td>'
    print '</tr>'

    print '<tr>'
    print '<td>Nombre real: </td>'
    print '<td><input class="form-control" type="text" size="30" maxlength="64" name="Fullname"></td>'
    print '</tr>'

    print '<tr>'
    print '<td>Email: </td>'
    print '<td><input class="form-control" type="text" size="30" maxlength="64" name="Email"></td>'
    print '</tr>'

    print '<tr>'
    print '<td></td>'
    print '<td><small>Se te enviar&aacute;n reportes de pron&oacute;sticos a esta direcci&oacute;n.</small></td>'
    print '</tr>'

    print '</table>'

    print '<small><b>Nota</b>: el sistema almacena las contrase&ntilde;as cifradas, por lo que nadie (ni el administrador) puede recuperarla. Si la olvidas, contacta al administrador para generar una nueva.</small>'

    print '</center>'

    print '<hr>'

    print '<div class="checkbox-inline">'
    print '<label style="font-weight: normal; margin-bottom: 5px;">'
    print '<input type="checkbox" id="ruleschk" onClick="$(\'#submitBtn\').toggleClass(\'disabled\')";">'
    print 'He le&iacute;do y acepto las reglas'
    print '</label>'
    print '</div>'
    print '<br><button type="submit" class="btn btn-primary disabled" id="submitBtn">Registrarme</button>'

    print '</form>'
    print '</div>'

    bootstrapFooter()

    print '</body>'
    print '</html>'

# =======================================

if registrationClosed:
    outputRegClosedPage()
else:
    outputRegistrationPage()