#!/usr/bin/env python

import cgi, cgitb
cgitb.enable()
from common import *

print "Content-type:text/html"
print     # THIS BLANK LINE IS MANDATORY
print '<html><head></head><body>'

# Get form data and Players list
form = cgi.FieldStorage()

print datetime.datetime.now().isoformat(), "<br>"
print "Running Scores and Ranks updater ...<br>"
print "All output is written to logfile.<br>"
updateScoresRanks()
print "Done!"

print '</body></html>'