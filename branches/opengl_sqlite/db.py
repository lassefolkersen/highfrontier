import sqlite3
# connect to the db
connection = sqlite3.connect('db/highfrontier.sqlite');
c=connection.cursor()

def dict_factory(cursor, row):
    """ outputs dictionary objects to match the row """
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

c.row_factory = dict_factory


# function to run queries against the db
def query(t,args={}):
    return c.execute(t,args)

# get the id of the newest object, right after creating it
def lastInsertId():
    return c.lastrowid
