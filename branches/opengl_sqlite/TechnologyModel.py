import db
#todo: test this model
class TechnologyModel:
    """ 
    Technologies are things that you research, which involve processing 
    resources into other stuff.
    """
    def update(self,technology):
        db.query('update technology set name=:name, resource_id=:resource_id where technology_id=:technology_id',
                 technology)
        return technology['technology_id']
    def insert(self,technology):
        db.query('insert into technology (name,resource_id) values (:name,:technology_id)',
                 technology)
        return db.lastInsertId()
    def save(self,technology):
        if(technology.has_key('technology_id')):
            return self.update(technology)
        return self.insert(technology)
    def createInstance(self):
        return {'name':None,'resource_id':None}
    def load(self,technology_id):
        q=db.query('select technology_id, name, resource_id from technology where technology_id=:technology_id',
                   {'technology_id':technology_id})
        r=q.fetchone()
        if(not r):
            return self.createInstance()
        return r
    def __init__(self):
        db.query('create table if not exist technology ('
                 'technology_id integer not null primary key, '
                 'name text not null, '
                 'resource_id integer not null, '
                 'foreign key(resource_id) references resource(resource_id) '
                 ') ')
        pass

