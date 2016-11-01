#!/usr/bin/env python

# Generates crontab entries for the specified weeks
# One useful way to do this is to first run the script redirecting the
# output to a dumpfile, then add it to the crontab with
# (crontab -l; cat <dumpfile>) | crontab -
# This wll append the dumpfile's contents to the crontab

import sys
from common import *
         
# --------------------------------

# Start and end weeks to generate entries for
start_week = 8
end_week = 17

# Datetime of *SERVER* DST end
# This assumes that the server's DST is properly configured, so cron
# will use the correct timezone once DST ends 
# DST ends November 6th in 2016 in the US
server_dst_end = datetime.datetime(2016, 11, 6, 0, 0, 0, tzinfo=ET)

# --------------------------------

# Connect to MySQL database
db = DBHelper()
db.Connect()

for week in range(start_week, end_week+1):

  # Get matches for current week
  print "# WEEK %i" % week
  Matches = db.loadMatches(week)

  curdatetime = Matches[0].DateTime
  groups = [(curdatetime,[])]
  for match in Matches:

    newdatetime = match.DateTime
    if newdatetime == curdatetime:
      groups[-1][1].append(match)
    else:
      groups.append((newdatetime, [match]))
      curdatetime = newdatetime

  for dt,matches in groups: 

    # Set server timezone at the start time of the matches
    if (matches[0].DateTime < server_dst_end): serverTZ = EDT
    else: serverTZ = ET

    minu = dt.astimezone(serverTZ).minute
    hour = dt.astimezone(serverTZ).hour
    day = dt.astimezone(serverTZ).day
    month = dt.astimezone(serverTZ).month
    command = "$HOME/public_html/NFL%i/cgi-bin/email_script.py " % (season)
    matches = map(lambda x: x.MatchID, matches)
    command += " ".join(matches)
    cronline = "%i %i %i %i * %s" % (minu, hour, day, month, command)
    print cronline

db.Close()
