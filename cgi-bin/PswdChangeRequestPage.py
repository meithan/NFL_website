#!/usr/bin/env python

# Generates the Password Change page
import cgi, cgitb
cgitb.enable()
from common import *

logged_user = authenticateUser()

# HTML header
print "Content-type:text/html"
print
print '<!DOCTYPE html>'
print '<html lang="en">'
print '<head>'
bootstrapHeader()
print '</head>'
print '<body>'

bootstrapNavbar("",logged_user)

print '<div class="container">'
print '<h3>Cambio de Contrase&ntilde;a</h3>'

print 'Si olvidaste tu contrase&ntilde;a, introduce tu nombre de usuario y se te enviar&aacute; un email con instrucciones para establecer una nueva contrase&ntilde;a.<br><br>'

print '<form role="form" class="form-horizontal" name="PswdChange" action="/NFL%i/cgi-bin/PswdChangeTicketGen.py" method="post">' % (season)
print '<div style="width: 40%;">'

print '<div class="form-group">'
print '<label class="col-sm-5 control-label" for="inputUserName">Nombre de usuario: </label>'
print '<div class="col-sm-7">'
print '<input type="text" class="form-control" id="inputUserName" placeholder="Nombre de usuario" maxlength="20" name="Username">'
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

bootstrapFooter()

print '</body>'
print '</html>'