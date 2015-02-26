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
        conn = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)
        # expired = time.time() - 86400 #  One day ago
        expired = time.time() - 300  # Five minute(s) ago
        r = database.custom()
        result = r.table(c.user_table).filter((r.row['created'] < expired) and (r.row['verified'] == False))['id'].coerce_to('array').run(conn)
        if len(result) > 0:
            database.delete(c.user_table, conn, database.args(result))
            database.delete(c.auth_table, conn, database.args(result))
            print "Removed {} unverified users from the database".format(len(result))
        conn.close()

    @huey.periodic_task(crontab(minute='*', hour='*'))
    def cleanLoginSessions():
        conn = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)
        expired = time.time() - 70  # 70 second(s) ago
        r = database.custom()
        result = r.table('auth').update(lambda row: {'login_sessions': row['login_sessions'].filter(lambda session: session['timestamp'] > expired)}).run(conn)
        if result['replaced'] > 0:
            print "Removed expired login_sessions for {} users from the database".format(result['replaced'])
        conn.close()


class Trigger(object):
    def __init__(self):
        pass

    @huey.task()
    def genDatabaseKey(self, priv_table, key, size=8192, pub_table=False):
        if pub_table is False:
            pub_table = priv_table
        privkey, pubkey = quicrypt.keyGenerator(size)
        conn = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)
        database.insert(priv_table, conn, dict(id=key, private=privkey))
        database.insert(pub_table, conn, dict(id=key, key=pubkey))
        conn.close()

    @huey.task()
    def sendEmail(self, sender, recipients, subject, filename, items, host):
        items['boundary'] = "--==_mimepart_{}".format(quicrypt.secretGenerator())
        content = 'Content-type: multipart/alternative;\r\n   boundary="{}";\r\n  charset=UTF-8'.format(items['boundary'])
        message = webdata.email(filename).format(**items)
        email = "From: Quik <{}>\r\nTo: {}\r\nMIME-Version: 1.0\r\n{}\r\nSubject: {}\r\n\r\n{}".format(sender, ', '.join(recipients), content, subject, message)
        smtpObj = smtplib.SMTP(host)
        smtpObj.sendmail(sender, recipients, email)
        print "Sent email from {} to {} successfully".format(sender, ', '.join(recipients))
