#!/usr/bin/env python

# Generates the Rules page
import cgi, cgitb
cgitb.enable()
from common import *

# Session
logged_user = authenticateUser()

# HTML header
print "Content-type:text/html\r\n\r\n"
print '<!DOCTYPE html>'
print '<html lang="en">'
print '<head>'
bootstrapHeader()
print '</head>'
print '<body>'

bootstrapNavbar("Rules",logged_user)

print '<div class="container">'
print '<h3>Reglas de la Quiniela NFL %i</h3>' % (season)

outputRules()

print '</div>'
bootstrapFooter()

print '</body>'
print '</html>'