import db
# todo: test this model
class JnFirmResourceModel:
    """ 
    Get and set resources attached to firms.  Firms also have a technology_id, 
    so you know how many parts of each resource is needed to generate an unit 
    of output
    """
    def store(self,firm_id,resource_id,quantity):
        db.query('replace into jn_firm_resource (firm_id,resource_id,quantity) values (:firm_id,:resource_id,:quantity)',
                 {'firm_id':firm_id,'resource_id':resource_id,'quantity':quantity})
        pass
    def load(self,firm_id,resource_id):
        q=db.query('select quantity from jn_firm_resource where firm_id=:firm_id and resource_id=:resource_id',
                   {'firm_id':firm_id, 'resource_id':resource_id})
        r=q.fetchone()
        if(r):
            return r['quantity']
        return 0
    def __init__(self):
        db.query('create table if not exist jn_firm_resource ( '
                 +'firm_id integer not null, '
                 +'resource_id integer not null, '
                 +'quantity integer, '
                 +'primary key(firm_id,resource_id), '
                 +'foreign key(firm_id) references firm(firm_id), '
                 +'foreign key(resource_id) references resource(resource_id) )');
        pass;

