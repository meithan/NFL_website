#!/usr/bin/env python

# Performs session logout by sending a revocation cookie and
# eliminating the entry from the db
import cgi, cgitb
cgitb.enable()
from common import *

# Retrieve sessionID from POST and do logout
form = cgi.FieldStorage()
if form.has_key("sessionID"): 
    sessionID = form["sessionID"].value
    doLogout(sessionID)
else: 
    # Just redirect to Main Page if no sessionID passed
    print "Content-type:text/html"
    print "Location: http://meithan.x10.mx/NFL%i/cgi-bin/MainPage.py" % (season)
    print "\r\n\r\n"
