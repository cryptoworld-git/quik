import json
import time
import smtplib
import datetime

from huey import RedisHuey, crontab
from . import database, handler, crypto


iterate = handler.Iterate()
webdata = handler.WebData()
quicrypt = crypto.QuiCrypt()

c = handler.configGen()


try:
    huey = RedisHuey('hub-queue', host=c.db_host, port=6379)
except:
    huey = RedisHuey('hub-queue', host=c.db_back, port=6379)


class Automation(object):
    def __init__(self):
        pass

    @huey.periodic_task(crontab(minute='*', hour='*'))
    def cleanUserDatabase():
        '''Huey task to routinely clean the database of all user accounts that are unverified '''  # Set to Five Minutes for debug
        conn = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)
        # expired = time.time() - 86400 #  One day ago
        expired = time.time() - 300  # Five minute(s) ago
        r = database.custom()  # Fetch the entire custom database object - kinda heavy; make sure it's cleaned up
        result = r.table(c.user_table).filter((r.row['created'] < expired) and (r.row['verified'] == False))['id'].coerce_to('array').run(conn)
        #  The above string asks the database server to locate all items out of the user table where 'created' is older than 'expired' and verified is false
        if len(result) > 0:
            database.delete(c.user_table, conn, database.args(result))  # Delete all the IDs recieved by the query string out of the 'user' database
            database.delete(c.auth_table, conn, database.args(result))  # Delete all the IDs recieved by the query string out of the 'auth' database
            print "Removed {} unverified users from the database".format(len(result))
        conn.close()  # Clean up the database connection

    @huey.periodic_task(crontab(minute='*', hour='*'))
    def cleanLoginSessions():
        '''Huey task to clear login sessions out of the database'''
        conn = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)
        expired = time.time() - 120  # Two minute(s) ago
        r = database.custom()  # Fetch the entire custom database object - kinda heavy; make sure it's cleaned up
        result = r.table(c.auth_table).update(lambda row:{'login_sessions':row['login_sessions'].filter(lambda session:session['timestamp'] > expired)}).run(conn)
        #  The above string asks the database server to find all login sessions in the table 'auth' with a timestamp older than 'expired' and delete them
        #  This is a heavy action - should be stress tested
        if result['replaced'] > 0:
            print "Removed expired login_sessions for {} users from the database".format(result['replaced'])
        conn.close()  # Clean up the database connection


class Trigger(object):
    def __init__(self):
        pass

    @huey.task()
    def genDatabaseKey(self, priv_table, key, size=4096, pub_table=False):
        '''Huey task to generate a RSA key for the group mode "Pre-Shared Key"'''
        if pub_table is False:  # Allows us to specify a new table for storing the public key from the private key
            pub_table = priv_table
        privkey, pubkey = quicrypt.keyGenerator(size)  # Generate the actual key and get it back from
        conn = database.connect(c.db_name, c.db_host, c.db_port, c.db_back) 
        database.insert(priv_table, conn, dict(id=key, private=privkey))  # Insert the private key into the database where we specify
        database.insert(pub_table, conn, dict(id=key, key=pubkey))  # Insert the public key into the database where we specify
        conn.close()  # Clean up the database connection

    @huey.task()
    def sendEmail(self, sender, recipients, subject, filename, items, host):
        '''Huey task to format and send an email to users to verify their account on registration'''
        items['boundary'] = "--==_mimepart_{}".format(quicrypt.secretGenerator())  # Generate our BOUNDARY using a random string
        content = 'Content-type: multipart/alternative;\r\n   boundary="{}";\r\n  charset=UTF-8'.format(items['boundary'])  # Generate the content headers
        message = webdata.email(filename).format(**items)  # Populate the template using items passed from the function that called it
        email = "From: Quik <{}>\r\nTo: {}\r\nMIME-Version: 1.0\r\n{}\r\nSubject: {}\r\n\r\n{}".format(sender, ', '.join(recipients), content, subject, message)
        # Above string puts the email together with it's main headers and content headers, then add in the populated template
        smtpObj = smtplib.SMTP(host)  # Create a SMTP object
        smtpObj.sendmail(sender, recipients, email)  # Send the actual email
        print "Sent email from {} to {} successfully".format(sender, ', '.join(recipients))
