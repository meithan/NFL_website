#!/usr/bin/python

# Week Generator
import cgi, cgitb, sys
cgitb.enable()
from common import *
import re

# ==================

# Returns the month number
def monthNumber(name):
    if (name == "jan" or name == "january"): return "01"
    elif (name == "feb" or name == "february"): return "02"
    elif (name == "mar" or name == "march"): return "03"
    elif (name == "apr" or name == "april"): return "04"
    elif (name == "may" or name == "may"): return "05"
    elif (name == "jun" or name == "june"): return "06"
    elif (name == "jul" or name == "july"): return "07"
    elif (name == "aug" or name == "august"): return "08"  
    elif (name == "sep" or name == "september"): return "09"
    elif (name == "oct" or name == "october"): return "10"
    elif (name == "nov" or name == "november"): return "11"
    elif (name == "dec" or name == "december"): return "12"
    
# Returns time in 24 hour format
def time24(timestr):
    tokens = timestr.split(" ")
    ampm = tokens[1]
    if ampm == "am":
        return tokens[0]
    elif ampm == "pm":
        hours = int(tokens[0].split(":")[0])
        if hours < 12: hours += 12
        mins = tokens[0].split(":")[1]
        return "%s:%s" % (str(hours),mins)

def getTeamID (name):
    name = name.lower()
    if "louis" in name: return "LA"
    elif "jets" in name: return "NYJ"
    elif "giants" in name: return "NYG"
    for teamID in Teams:
        if Teams[teamID].Name.lower() in name or Teams[teamID].City.lower() in name:
            return teamID

# ==================    

print "Content-type:text/html\r\n\r\n"
print "<html><head></head><body>"

# Create instance of FieldStorage 
form = cgi.FieldStorage()

# Get basic data from Form
fail = False
#if form.has_key("week"): week = int(form["week"].value)
#else: fail = True
if form.has_key("year"): year = int(form["year"].value)
else: fail = True
if form.has_key("tzone"): tzone = form["tzone"].value
else: fail = True
if form.has_key("inputTxt"): input = form["inputTxt"].value
else: fail = True
if fail:
  print "Missing data!"
  print "</body></html>"
  sys.exit()

db = DBHelper()
db.Connect()
Teams = db.loadTeams()
db.Close()

cities = ['Minnesota', 'Miami', 'Carolina', 'Atlanta', 'Detroit', 'Cincinnati', 'New York', 'Denver', 'Tie', 'Baltimore', 'New York', 'Oakland', 'Tennessee', 'New Orleans', 'Dallas', 'New England', 'Seattle', 'Chicago', 'Tampa Bay', 'Pittsburgh', 'St. Louis', 'Cleveland', 'Houston', 'Green Bay', 'Washington', 'Jacksonville', 'Kansas City', 'Philadelphia', 'Buffalo', 'Indianapolis', 'Arizona', 'San Francisco', 'San Diego']

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Parse input
datestr = ""
matches = []
byes = ""
tokens = input.split("\r\n")
week = None

for token in tokens:
    token = token.lower()
    print ">", token, "<br>"
    if "week" in token:
      week = int(token.split()[1])
      print "WEEK = %i<br>" % week
    elif True in map(lambda z: z.lower() in token, days):
        stuff = re.split(', |\. ', token)
        weekday = stuff[0].lower()
        month = stuff[1].lower()
        day = int(stuff[2])
        datestr = "%s-%s-%s" % (year, monthNumber(month.lower()), "%02i" % int(day))
        print "Changed date: %s<br>" % datestr
    elif " at " in token:
        if datestr == "":
            print "Couldn't pick up date!"
            break
        data = re.split('\t| at ', token)
        AwayTeam = data[0]
        AwayID = getTeamID(AwayTeam)
        if AwayID == None:
           print "Couldn't get ID for team %s<br>" % AwayTeam
           break
        HomeTeam = data[1]
        HomeID = getTeamID(HomeTeam)
        if HomeID == None:
           print "Couldn't get ID for team %s<br>" % HomeTeam
           break
        Time = data[2]
        matchid = "W%i-%s@%s" % (week, AwayID, HomeID)
        print "Parsed", matchid, Time, "/", time24(Time), "<br>"
        matches.append((matchid, datestr, time24(Time), AwayID, HomeID))
    elif "bye week" in token:
        data = token.replace("bye week:","").split(",")
        byes = []
        for item in data:
            teamID = getTeamID(item)
            if teamID == None:
                print "Couldn't get ID for team %s<br>" % teamID
                break
            byes.append(teamID)
        print "Week byes: " + ", ".join(byes) + "<br>"

print "<br><strong>MATCHES PARSED</strong>: %i<br><br>" % (len(matches))

# Week byes
if len(byes) > 0:
    print "<strong>Add the following line to the week_byes dictionary in common.py</strong>:<br>"
    print '<textarea readonly cols="40" rows="2" style="width: 400px; resize: none;">'
    print "week_byes[%i] = %s" % (week, repr(byes))
    print '</textarea>'
    print "<br>"
else:
    print "No byes this week<br>"

# Print out MySQL instruction
print "<br><strong>MySQL query to add this week to the DB</strong>:", "<br>"
print "<br>"
print '<textarea readonly cols="40" rows="20" style="width: 800px; resize: none;">'
print "INSERT INTO Matches VALUES"
for i,m in enumerate(matches):
    matchID = m[0]
    mdate = m[1]
    mtime = m[2]
    ateam = m[3]
    hteam = m[4]
    buf = '("%s",%i,"%s","%s","%s","%s","%s","Pregame",NULL,NULL,NULL)' % (matchID,week,mdate,mtime,tzone,ateam,hteam)
    if i < len(matches)-1: buf += ","
    elif i == (len(matches)-1): buf += ";"
    print buf
print '</textarea>'
print '<br><br>'



print "</body></html>"
