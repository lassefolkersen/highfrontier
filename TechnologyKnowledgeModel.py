import db
# todo: test this model
class TechnologyKnowledgeModel:
    """ 
    What companies know about what techs?  How much research is needed to 
    start setting up firms for it?
    """
    def delete(self,company_id, technology_id):
        db.query('delete from technology_knowledge where company_id=:company_id and technology_id=:technology_id',
                 {'company_id':company_id,
                  'technology_id':technology_id})
        pass
    def save(self,company_id,technology_id,research_left):
        q=db.query('replace into technology_knowledge (company_id, technology_id, research_left) '
                   +'values (:company_id,:technology_id,:research_left)',
                   {'company_id':company_id, 'technology_id':technology_id, 'research_left':research_left})
        pass
    def load(self,company_id,technology_id):
        q=db.query('select research_left from technology_knowledge '
                   +'where company_id=:company_id '
                   +'and technology_id=:technology_id',
                   {'company_id':company_id,'technology_id':technology_id})
        r=q.fetchone()
        return r['research_left']
    def check(self,company_id,technology_id):
        q=db.query('select research_left from technology_knowledge '
                   +'where company_id=:company_id '
                   +'and technology_id=:technology_id',
                   {'company_id':company_id,'technology_id':technology_id})
        r=q.fetchone()
        if(not r):
            return False
        return True
    def __init__(self):
        db.query('create table if not exist technology_knowledge ('
                 +'company_id integer not null, '
                 +'technology_id integer not null, '
                 +'research_left integer not null default 9999999, '
                 +'primary key(company_id,technology_id), '
                 +'foreign key(company_id) references company(company_id), '
                 +'foreign key(technology_id) references technology(technology_id))')
        pass
