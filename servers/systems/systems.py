from __future__ import division

import json
import bottle

from core import database, handler
from bottle import request, run, route, template, hook, response

statnum = handler.StatusCodes()
webdata = handler.WebData()

app = application = bottle.Bottle()

'''Settings and Setup for the Application'''
c = handler.Bunch(webdata.loader('config.json'))

connection = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)


def conn():
    '''Check if the current threads connection is stale, if so recreate it globally, then pass the connection object along'''
    global connection  # Use the global object instead of the function local
    try:
        database.ping(connection)  # Poll the DB to see if the connection pool is live
    except Exception as e:
        connection = database.connect(c.db_name, c.db_host, c.db_port, c.db_back)  # Recreate the connection pool if it's stale
    return connection


@app.route('{}/key/<uuid>'.format(c.sys_prefix))
def systemkey(uuid):
    try:
        keydata = database.get(c.syst_table, conn(), uuid)
        del keydata['private']
        return keydata
    except:
        return statnum.convert({"status": "100"})

if __name__ == "__main__":
    app.run(host=c.web_host, port=c.sys_port, debug=True, reloader=True)
