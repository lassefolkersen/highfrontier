import db
# todo: test this model
class JnCompanyCityModel:
    """
    Crud code to get and set links between companies and cities.  
    """
    def unset(self,company_id,city_id):
        q=db.query('delete from jn_company_city where company_id=:company_id and city_id=:city_id',
                   {'company_id':company_id, 'city_id':city_id})
        pass
    def set(self,company_id,city_id):
        q=db.query('replace into jn_company_city (company_id,city_id) values (:company_id,:city_id)',
                   {'company_id':company_id,
                    'city_id':city_id});
        pass
    def check(self,company_id,city_id):
        q=db.query('select true from jn_company_city where company_id=:company_id and city_id=:city_id limit 1',
                   {'company_id':company_id,
                    'city_id':city_id})
        r=q.fetchone()
        if(r):
            return True
        return False
    def __init__(self):
        db.query('create table if not exists jn_company_city ( '
                 +'company_id integer not null,'
                 +'city_id integer not null,'
                 +'primary key(company_id,city_id),'
                 +'foreign key(company_id) references company(company_id),'
                 +'foreign key(city_id) references city(city_id))');
        pass
