#!/usr/bin/env python

import datetime
import cgi, cgitb
cgitb.enable()
import Cookie
import os
import random

# Receive login data
form = cgi.FieldStorage()

# Get basic data from Form
if form.has_key("username"):
  user = form["username"].value
else:
  user = None

if form.has_key("password"):
  pswd = form["password"].value
else:
  pswd = None

if form.has_key("remember_me"):
  if form["remember_me"].value == "on":
    remember_me = True
  else:
    remember_me = False
else:
  remember_me = False

# Here we check if the login credentials are valid
# and return an error if they're not. We'll assume
# they were checked and found valid
# After successful authentication, we create a cookie
# with a new random session ID

cookie = Cookie.SimpleCookie()
cookie["session"] = random.randint(1,1000000000)
cookie["session"]["domain"] = "meithan.x10.mx"
cookie["session"]["path"] = "/"
if remember_me:   # Only set an expiration date if the user wants to be remembered
  expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
  cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

# =======================================

print "Content-type:text/html"
print cookie.output()    # <-- here we send the cookie over
print "\r\n\r\n"
print "<html><head></head><body>"

# =======================================

print "Cookie sent!<br>"
print cookie.output()

# =======================================

print "</body></html>"