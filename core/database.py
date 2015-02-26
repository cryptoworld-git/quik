from __future__ import division

import time
import math
import json

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


def connect(db, host, port, backup=None):
    '''Create a Connection to the Database'''
    try:
        return r.connect(host=host, port=port, db=db)
    except:
        return r.connect(host=backup, port=port, db=db)


def setup(db, host, port, tables, backup=None):
    '''Setup databases, tables, and indexes'''
    try:
        conn = r.connect(host=host, port=port)  # Connect to the database server
    except:
        conn = r.connect(host=backup, port=port)

    try:
        r.db_create(db).run(conn)  # Create the database
    except:
        pass

    for table, indexes in tables.items():  # Seperate the tables and indexes and iterate over them
        try:
            r.db(db).table_create(table).run(conn)  # Try to create the table
        except:
            pass
        for index in indexes:  # Create the indexes for the specified table
            try:
                if type(index) is list:
                    r.db(db).table(table).index_create(index[0], **index[1]).run(conn)  # Create compound indexes if we need to 
                else:
                    r.db(db).table(table).index_create(index).run(conn)  # Create a normal index
            except:
                pass

    conn.close()


def args(key):
    '''Create a rethinkdb ARGS object out of a list'''
    if type(key) is str:
        return key
    return r.args(key)


def ping(conn):
    '''Check if the Database Pool is still open'''
    return r.expr(1).run(conn)


def uuid(conn):
    '''Generate a Unique ID'''
    return r.uuid().run(conn)


def get(table, conn, key):
    '''Fetch a specific item out of the database by Primary Key'''
    return r.table(table).get(key).run(conn)


def getall(table, conn, key, index):
    '''Fetch all results out of the database by Secondary Key'''
    return r.table(table).get_all(key, index=index).coerce_to('array').run(conn)


def getordered(table, conn, key, index, order, direction=None):
    '''Fetch all results out of the database by Secondary Key and order them by non-index'''
    if direction is 'desc':
        return r.table(table).get_all(key, index=index).order_by(r.desc(order)).coerce_to('array').run(conn)
    else:
        return r.table(table).get_all(key, index=index).order_by(r.asc(order)).coerce_to('array').run(conn)


def match(table, conn, value, index, matching="equals"):  # Use Sparingly... Doesn't use an Index and will hit Array_Limit
    '''Fetch all results out of the database by specific index and value pair by match type'''
    if "equal" in matching:
        return r.table(table).filter(r.row[index] == value).coerce_to('array').run(conn)
    elif "great" in matching:
        return r.table(table).filter(r.row[index] < value).coerce_to('array').run(conn)
    elif "less" in matching:
        return r.table(table).filter(r.row[index] > value).coerce_to('array').run(conn)


def submatch(table, conn, key, index, sub, value, matching="equals"):
    '''Fetch all results out of the database by specific key and index with a sub value pair by match type'''
    query = r.table(table).get(key)[index]
    if "equal" in matching:
        query = query.filter(lambda subgroup: subgroup[sub] == value)
    if "great" in matching:
        query = query.filter(lambda subgroup: subgroup[sub] < value)
    if "less" in matching:
        query = query.filter(lambda subgroup: subgroup[sub] > value)
    if "not" in matching:
        query = query.filter(lambda subgroup: subgroup[sub] != value)
    return query.run(conn)


def contains(table, conn, value, index):  # Use Sparingly... Doesn't use an Index and will hit Array_Limit
    '''Fetch all results out of the database by a specific index and regex search pair'''
    return r.table(table).filter(lambda doc: doc[index].match(value)).coerce_to('array').run(conn)


def delete(table, conn, key):
    '''Delete a key from the database'''
    return r.table(table).get_all(key).delete().run(conn)


def custom():
    '''Return the r cursor so that other functions can string together their own rethinkdb queries'''
    return r


def insert(table, conn, data, conflict='update'):
    '''Insert data into the database and allow swapping away from Upsert'''
    return r.table(table).insert(data, conflict=conflict).run(conn)


def append(table, conn, key, item, data):
    '''Append data to a list in the database'''
    #  chunks = [chunks[x:x+size] for x in xrange(0, len(chunks), size)]
    r.table(table).get(key).update({item: r.row[item].append(data)}).run(conn)
