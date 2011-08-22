import db
from BodyModel import BodyModel
bm=BodyModel()
bm.initialize_planets()

q=db.query('select b.body_id,b.parent_id,b.name,p.name as parent_name from body as b left join body as p on p.body_id=b.parent_id ')
for r in q:
    print r
