
import web
import itertools

db = None

def getdb():
    global db
    if db is None:
        db = web.database(**web.config.db_parameters)
    return db
    
def query(*a, **kw):
    return getdb().query(*a, **kw)

def storify(d):
    if isinstance(d, list):
        return [storify(x) for x in d]
    elif isinstance(d, dict):
        return web.storage((k, storify(v)) for k, v in d.items())
    else:
        return d

def get_party(name):
    id = id.upper()
    try:
        return query("SELECT * FROM party WHERE id=$id", vars=locals())[0]
    except IndexError:
        return None

def get_candidate(name):
    return web.storage()

def get_state(id):
    id = id.upper()
    try:
        return query("SELECT * FROM state WHERE id=$id", vars=locals())[0]
    except IndexError:
        return None

def get_constituency(state, id):
    try:
        constituency = query("SELECT * FROM constituency where id=$id", vars=locals())[0]
    except IndexError:
        return None
        
    d = web.storage()
    d.id = id
    d.name = constituency.name
    d.state = get_state(constituency.state)
    d.election_history = list(get_election_history(id))
    return d
    
def get_election_history(constituency_id):
    def parse_candidate(d):
        out = web.storage()
        out.id = d.candidate_id
        out.party = web.storage(id="party/" + d.party_id, name=d.party_id)
        out.percentage_votes = d.percentage_votes_polled
        return out
    
    result = query("SELECT * FROM election where constituency_id=$constituency_id ORDER BY year desc, percentage_votes_polled desc", vars=locals())

    for year, data in itertools.groupby(result, lambda row: row.year):
        data = list(data)
        x = web.storage()
        x.year = year
        x.numvoters = data[0].total_votes
        x.candidates = [parse_candidate(d) for d in data]
        yield x
