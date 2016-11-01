#!/usr/bin/env python

# Convenience script to issue MySQL queries to the DB
import cgi, cgitb
import sys
cgitb.enable()

from common import *

# =====================================

def showBadLogin():
    print '<br><strong>You must have the proper credentials to access this page!</strong>'
    print '</body></html>'

# =====================================

def showGoodPage():

    # Get query string, if present
    formdata = cgi.FieldStorage()
    if formdata.has_key("Query"):
        queryStr = formdata["Query"].value
    else:
        queryStr = ""

    responseStr = ""

    # =======================================
 
    # Send query to DB, obtain response
    if queryStr != "":

        # Import MySQLdb module
        library_loaded = False
        responseStr += "Loading MySQLdb ..."
        try:
          sys.path.append('/home/meithanx/mysql')
          import MySQLdb
          library_loaded = True
        except:
          responseStr += "\nCouldn't load MySQLdb!\n"

        if library_loaded:
            responseStr += " Loaded.\n"

            # Connect to DB
            connected = False
            responseStr += "Establishing connection to DB %s ..." % (DB_NAME)
            try:
                db = MySQLdb.connect("localhost","meithanx_sql","foobar",DB_NAME)
                dbcursor = db.cursor()
                connected = True
            except:
                responseStr += "Couldn't connect to DB %s!!\n" % (DB_NAME)

            if connected:
                responseStr += " Connected.\n"
                responseStr += "===============================\n\n"
                responseStr += "> %s\n\n" % (queryStr)
                query = queryStr.strip()
                dbcursor.execute(query)
                db.commit()
                rows_affected = dbcursor.rowcount
                rowset = dbcursor.fetchall()
                if len(rowset)==0:
                    responseStr += repr(rowset) + "\n"
                for row in rowset:
                    responseStr += repr(row) + "\n"
                responseStr += "%i rows processed.\n" % (rows_affected)

    # =======================================

    print '<form method="GET">'
    print '<div style="width: 800px; margin:0 auto;">'

    print '<br>'
    print 'Query:<br>'
    print '<textarea id="QueryField" name="Query" cols="40" rows="5" style="width: 800px;">%s</textarea>' % (queryStr)

    print '<br>'
    print '<input type="submit" value="Submit"> &nbsp;'
    print '<input type="button" onClick="clearQueryField()" value="Clear">'
    print ' &nbsp;&nbsp;&nbsp; Queries: <input type="button" onClick="enterSelect()" value="SELECT">'
    print ' &nbsp; <input type="button" onClick="enterUpdate()" value="UPDATE">'
    print ' &nbsp; <input type="button" onClick="enterInsert()" value="INSERT">'
    print ' &nbsp; <input type="button" onClick="enterDelete()" value="DELETE">'
    print ' &nbsp; <input type="button" onClick="enterDescribe()" value="DESCRIBE">'

    print '<br>'
    print '<hr>'

    print '</form>'

    print 'Response:<br>'
    print '<textarea readonly id="Response" cols="40" rows="40" style="width: 800px;">%s</textarea>' % (responseStr)


    print '<div>'

    print '</body></html>'

# =====================================

print "Content-type:text/html"
print     # THIS BLANK LIKE IS MANDATORY
print '<!DOCTYPE html>'
print '<html lang="en">'
print '<head>'
print '<script language="JavaScript">'
print 'function clearQueryField() {'
print '  document.getElementById("QueryField").value="";'
print '}'
print 'function enterSelect() {'
print '  document.getElementById("QueryField").value="SELECT * FROM table_name WHERE condition;";'
print '}'
print 'function enterUpdate() {'
print '  document.getElementById("QueryField").value="UPDATE table_name SET field=value WHERE condition;";'
print '}'
print 'function enterInsert() {'
print '  document.getElementById("QueryField").value="INSERT INTO table_name VALUES (value1,value2);";'
print '}'
print 'function enterDelete() {'
print '  document.getElementById("QueryField").value="DELETE FROM table_name WHERE condition;";'
print '}'
print 'function enterDescribe() {'
print '  document.getElementById("QueryField").value="DESCRIBE table_name;";'
print '}'
print '</script></head><body>'

# Determine logged user from cookie, if any
logged_user = authenticateUser()

### HACK!! USER AUTHENTICATION BYPASSED
print "<h3>WARNING: user authentication temporarily overriden! Don\'t forget to re-protect this page!</h3>"

showGoodPage()

#if logged_user != None and logged_user.Username == "Meithan":
#    showGoodPage()
#else:
#    showBadLogin()