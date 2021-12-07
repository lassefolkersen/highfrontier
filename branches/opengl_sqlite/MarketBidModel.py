import db
#todo: test this model
class MarketBidModel:
    """ 
    Crud for bidding on market orders.  

    Eventually one of these will "win," and a resource transfer will take place.

    Not a lot of gameplay mechanics have been implemented here yet.
    """
    def insert(self,market_bid):
        db.query('insert into market_bid (company_id,amount,market_order_id) '
                 +'values (:company_id,:amount,:market_order_id)',
                 market_bid)
        return db.lastInsertId()
    def update(self,market_bid):
        db.query('update market_bid '
                 +'set company_id=:company_id, '
                 +'amount=:amount, '
                 +'market_order_id=:market_order_id '
                 +'where market_bid_id=:market_bid_id',
                 market_bid)
        return market_bid['market_bid_id']
    def createInstance(self):
        return {'company_id':None, 'amount':None,'market_order_id':None}
    def save(self,market_bid={}):
        if('market_bid_id' in market_bid):
            return self.update(market_bid)
        return self.insert(market_bid)
    def load(self,market_bid_id):
        q=db.query('select market_bid_id, company_id, amount, market_order_id '
                   +'from market_bid '
                   +'where market_bid_id=:market_bid_id',
                   {'market_bid_id':market_bid_id})
        r=q.fetchone()
        if(not r):
            return self.createInstance()
        return r
    def __init__(self):
        db.query('create table if not exist market_bid ('
                 +'market_bid_id integer not null primary key,'
                 +'company_id integer not null, '
                 +'amount integer not null default 0, '
                 +'market_order_id integer not null, '
                 +'foreign key(company_id) references company(company_id), '
                 +'foreign key(market_order_id) references market_order(market_order_id) '
                 +')')
        pass
