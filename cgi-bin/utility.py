#!/usr/bin/env python

# A utility script to run misc stuff on the server

import cgi, cgitb
cgitb.enable()
from common import *

print "Content-type:text/html"
print     # THIS BLANK LINE IS MANDATORY
print "<html><head></head><body>"

# ============================================

# DATABASE TABLES BACKUP

if (False):
  tables = ["Forecasts", "Matches", "Players", "PswdTickets", "Scores", "Sessions", "Teams"]
  for table in tables:
    print "Creating full backup of table %s ...<br>" % table
    backupTable(table)
  print "All backups done.<br>"



# ============================================

print "</body></html>"