#!/usr/bin/env python

import cgi, cgitb
cgitb.enable()
import string
import random
import sys
import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from common import *
from config import mailserver_host, mailserver_port, mailserver_username, mailserver_password

# Logging
logfile = open("/home/meithann/public_html/NFL%i/logs/email_sender.log" % (season), "a")

logfile.write("\n\n========================================================================\n")
logfile.write("Starting email sender ...\n")
logfile.write(datetime.datetime.now().isoformat())
logfile.write("\n")

# Get out if incorrect number of arguments
if (len(sys.argv) < 2):
  logfile.write("Must provide at least one matchID as argument!\n")
  logfile.write("Arglist: " + repr(sys.argv) + "\n")
  logfile.close()
  sys.exit()

# Obtain matchIDs from command line argument
passed_matches = []
for elem in sys.argv[1:]:
  passed_matches.append(elem)
logfile.write("\nPassed MatchIDs: %s\n" % repr(passed_matches))

# Connect to MySQL database
db = DBHelper()
db.Connect()

# Load stuff from DB
logfile.write("Loading team and player data ... ")
Teams = db.loadTeams()
Players = db.loadPlayers()
logfile.write("Done\n")

# Load matches from passed matchIDs
logfile.write("Loading matches ...\n")    
Matches = []
for matchID in passed_matches:
  match = db.loadMatch(matchID)
  if match == None:
    logfile.write("Couldn't load match %s! ABORTING!\n" % matchID)    
    sys.exit()
  else:
    logfile.write("Loaded match %s\n" % matchID)    
    Matches.append(match)


# Load player forecasts
logfile.write("Loading player forecasts for these matches ... ")    
for p in Players:
    p.Forecasts = db.loadForecastList(p.Username, passed_matches)
logfile.write("Done\n")    

db.Close()

# Sort players by username
Players.sort(key=lambda x: x.Username.lower())
numPlayers = len(Players)


# Build email body

logfile.write("Building email body ... ")

datenice = Matches[0].DateTime.astimezone(mexicoTZ).strftime("%A %d de %B de %Y")
datenice = spanishDateCorrection(datenice)
mexicoTZ = getMexicoTZ(Matches[0].DateTime)
time = Matches[0].DateTime.astimezone(mexicoTZ).strftime("%H:%M")
week = Matches[0].MatchID[1] if Matches[0].MatchID[2] == "-" else Matches[0].MatchID[1:2]
week = int(week)

htmlbody = """
<html>
<head>
<style>
table {
  text-align: left;
}
th {
  background-color: #d9d9d9;
  color: black;
}
table.striped tr:nth-child(even) {
  background-color: #e6e6e6
}
</style>
</head>
<body>

<h3>Reporte de Pron&oacute;sticos</h3>
<p><big>
Semana %i<br>
%s<br>
%s horas <small>(Tiempo del Centro de M&eacute;xico)</small>
<br><br>
P&aacute;gina de la quiniela: <a href="http://meithan.net/NFL2016">http://meithan.net/NFL2016</a><br>
</big>
<br><small>Enviado %s</small></p>\n""" % (week, datenice, time, datetime.datetime.now(mexicoTZ))


# Forecasts

plainbody = "Participante\t\tPronostico\n"

for match in Matches:

  ateam = Teams[match.AwayTeam].Name
  hteam = Teams[match.HomeTeam].Name
  datenice = match.DateTime.astimezone(mexicoTZ).strftime("%A %d de %B")
  datenice = spanishDateCorrection(datenice)
  # Adjust Mexico timezone at the time of the match (DST ends October 25th)
  mexicoTZ = getMexicoTZ(match.DateTime)
  time = match.DateTime.astimezone(mexicoTZ).strftime("%H:%M")

  htmlbody += "\n\n<hr>\n"
  htmlbody += "<h3>%s vs. %s</h3>\n" % (ateam, hteam)

  # Stats
  team1_picks = 0
  tie_picks = 0
  team2_picks = 0
  no_picks = 0
  for p in Players:
      if match.MatchID not in p.Forecasts:
          no_picks += 1
      else:
          if p.Forecasts[match.MatchID] == match.AwayTeam: team1_picks += 1
          elif p.Forecasts[match.MatchID] == match.HomeTeam: team2_picks += 1
  sl = [[Teams[match.AwayTeam].Name, team1_picks, 0.0]]
  sl.append([Teams[match.HomeTeam].Name, team2_picks, 0.0])
  sl.append(["No envi&oacute;", no_picks, 0.0])
  sl = sorted(sl, key=lambda x: x[1], reverse=True)
  for idx in range(1,len(sl)):
      sl[idx][2] = int(round(sl[idx][1]*100.0/numPlayers))
  sl[0][2] = 100 - sl[1][2] - sl[2][2]

  stats_string = '<table>\n<tr><th colspan="2"><strong>Resumen</strong></th></tr>'
  for idx in range(0,len(sl)):
      stats_string += "<tr><td>%s&nbsp;</td><td>%i (%i%%)</td></tr>\n" % (sl[idx][0], sl[idx][1], sl[idx][2])
  stats_string += "</table>\n"

  htmlbody += stats_string

  # Begin table
  htmlbody +="""
<br><div style="overflow-x:auto;">
<table class="striped">
<thead>
<tr>
<th>Participante&nbsp;&nbsp;</th>
<th>Pron&oacute;stico&nbsp;&nbsp;</th>
</tr>
</thead>
<tbody>"""

  # Table rows (one for each player)
  for i,p in enumerate(Players):
    if match.MatchID in p.Forecasts:
      pick = Teams[p.Forecasts[match.MatchID]].Name
    else:
      pick = "&mdash;"
    if i % 2 == 1: 
      htmlbody += '<tr style="background-color: #e6e6e6"><td>%s</td><td>%s</td></tr>\n' % (p.Username, pick)
    else:
      htmlbody += "<tr><td>%s</td><td>%s</td></tr>\n" % (p.Username, pick)
    plainbody += "%s\t\t%s\n" % (p.Username, pick)
  htmlbody += "</tbody></table></div><br>"

htmlbody += "</body></html>"

logfile.write("Done")
#logfile.write("\n"+htmlbody+"\n")

# Email list
email_list = []
for p in Players:
  if (p.email.count("@")==1):
    email_list.append(p.email)

##################
# DEBUG
#email_list = ["meithan@gmail.com"]
##################

logfile.write("\nEmail list:\n")
logfile.write(repr(email_list))
logfile.write("\n")

logfile.write("Building email header ... ")

# Email header and webmail server login
datenice = Matches[0].DateTime.astimezone(mexicoTZ).strftime("%A %d %b")
datenice = spanishDateCorrection(datenice)
time = Matches[0].DateTime.astimezone(mexicoTZ).strftime("%H:%M")
week = Matches[0].MatchID[1] if Matches[0].MatchID[2]=="-" else Matches[0].MatchID[1:2]
week = int(week)
subject = "Pron&oacute;sticos Semana %i, %s %s horas" % (week, datenice, time)
#subject = "Pron&oacute;sticos: "
#for i,match in enumerate(Matches):
#  if i>0 and i<len(Matches)-1: subject += ", "
#  if i==len(Matches)-1 and i!=0: 
#    if Teams[match.HomeTeam].Name[0] in ["I","i"]: subject += " e "
#    else: subject += " y "
#  subject += "%s vs. %s" % (Teams[match.HomeTeam].Name, Teams[match.HomeTeam].Name)
subject = subject.replace("&aacute;","=C3=A1")
subject = subject.replace("&eacute;","=C3=A9")
subject = subject.replace("&iacute;","=C3=AD")
subject = subject.replace("&oacute;","=C3=B3")
subject = subject.replace("&uacute;","=C3=BA")
subject = subject.replace("&ntilde;","=C3=B1")
subject = "=?utf-8?Q?" + subject + "?="

sender_name = "Quiniela NFL %i" % (season)
sender_email = "webmaster@meithan.net"
server = mailserver_host
port = mailserver_port
login = mailserver_username
pswd = mailserver_password

logfile.write("Done\n")
logfile.write(str(get_utcnow())+"\n")
logfile.write("Contacting mailserver ...\n")

mailserver = smtplib.SMTP(server,port)
response = mailserver.starttls()
logfile.write(repr(response) + "\n")
response = mailserver.ehlo()
logfile.write(repr(response) + "\n")
response = mailserver.login(login, pswd)
logfile.write(repr(response) + "\n")

commaspace = ', '
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = sender_name + " <%s>" % (sender_email)
msg['To'] = commaspace.join(email_list)
msg['Content-Language'] = "es"

part1 = MIMEText(plainbody, 'plain')
part2 = MIMEText(htmlbody, 'html')
msg.attach(part1)
msg.attach(part2)

logfile.write(str(get_utcnow())+"\n")
logfile.write("Sending email ...\n")
response = mailserver.sendmail(login, email_list, msg.as_string())
logfile.write("Sendmail response: %s\n" % repr(response)) 

response = mailserver.quit()
logfile.write(repr(response) + "\n")

logfile.write(str(get_utcnow())+"\n")
logfile.write("\nScript completed successfully!")
logfile.close()
sys.exit()
