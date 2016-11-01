#!/usr/bin/env python

# Manual script to issue MySQL queries to the DB
import cgi, cgitb
import sys
cgitb.enable()

from common import *

# Output HTML header
print "Content-type:text/html"
print     # THIS BLANK LIKE IS MANDATORY
print '<!DOCTYPE html>'
print '<html lang="en">'
print '<head></head><body>'

# Import MySQLdb module
print "Loading MySQLdb ..."
try:
  sys.path.append('/home/meithanx/mysql')
  import MySQLdb
except:
  print "Couldn't load MySQLdb!"
  sys.exit()
print " Loaded.<br>"

# Connect to DB
print "Establishing connection to database %s ..." % DB_NAME
try:
  db = MySQLdb.connect("localhost", "meithanx_sql", "foobar", DB_NAME)
  dbcursor = db.cursor()
except:
  print "Couldn't connect to DB!!"
  sys.exit()
print " Connected.<br>"
print "===============================<br><br>"

def run_query(query):
    print "&gt;", query, "<br>"
    dbcursor.execute(query)
    db.commit()
    rowset = dbcursor.fetchall()
    if len(rowset)==0: print repr(rowset),"<br>"
    for row in rowset:
        print repr(row),"<br>"

# ======================================================

#run_query("DROP TABLE Teams;")
#run_query("SELECT * FROM Teams;")
#run_query('INSERT INTO Teams (team_id, city, name, conf, wins, losses, ties) VALUES ("BAL","Baltimore","Ravens","AFCN",0,0,0);')
#run_query('DESCRIBE Players;')

#run_query('INSERT INTO Forecasts VALUES ("W1-GB@SEA","Meithan","GB",1,"%s");' % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
#run_query('INSERT INTO Forecasts VALUES ("W1-GB@SEA","Foo","SEA",1,"%s");' % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
#run_query('SELECT * FROM Forecasts;')
#run_query('SELECT * FROM Forecasts WHERE user_name="Foo" AND match_week=1;')
#run_query('DELETE FROM Sessions WHERE (type="normal" AND UTC_TIMESTAMP() > expiration) OR (type="session" and UTC_TIMESTAMP() > ADDDATE(issue, INTERVAL 24 HOUR));')
#run_query('SELECT * FROM Sessions')
#print "<br>Expired cookies:<br>"
#run_query('SELECT * FROM Sessions WHERE (type="normal" AND UTC_TIMESTAMP() > expiration) OR (type="session" and UTC_TIMESTAMP() > ADDDATE(issue, INTERVAL 24 HOUR));')
#run_query('UPDATE Matches SET status="Pregame", away_score=NULL, home_score=NULL, winner=NULL WHERE id="W1-GB@SEA";')

#run_query('SELECT * FROM Sessions;')

#updateMatch("W1-GB@SEA","Final",31,17,"GB")
#updateMatch("W1-NO@ATL","Final",3,8,"ATL")
#updateMatch("W1-MIN@STL","Final",20,10,"MIN")
#updateMatch("W1-CLE@PIT","Final",13,10,"CLE")
#updateMatch("W1-JAC@PHI","Final",13,20,"PHI")
#updateMatch("W1-OAK@NYJ","Final",33,20,"OAK")
#updateScoresRanks()

#backupTable("Matches")

# ======================================================

# Final stuff
print '</body></html>'
db.close()